import argparse
import yaml
import json
import csv
import time
import os
import sys
import re
from datetime import datetime
from pathlib import Path
import base64
import html as html_lib
import unicodedata
from openai import OpenAI, APIConnectionError, APIError

# --- Utils ---

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def load_suite(path):
    """
    スイートファイルを読み込み、includesフィールドがあれば
    分割されたカテゴリファイルをマージする。
    各テストケースにカテゴリ情報(category_id, category_name)を付与。
    """
    suite_path = Path(path)
    with open(suite_path, 'r', encoding='utf-8') as f:
        suite = yaml.safe_load(f)
    
    # includesフィールドがあればファイルを読み込んでマージ
    if 'includes' in suite:
        merged_cases = []
        categories = []
        
        for include_path in suite['includes']:
            # 相対パスの場合、スイートファイルからの相対位置として解決
            full_path = suite_path.parent / include_path
            
            if not full_path.exists():
                print(f"Warning: Include file not found: {full_path}")
                continue
            
            with open(full_path, 'r', encoding='utf-8') as f:
                category_data = yaml.safe_load(f)
            
            # カテゴリ情報を抽出
            cat_info = category_data.get('category', {})
            category_id = cat_info.get('id', 'unknown')
            category_name = cat_info.get('name', 'Unknown')
            category_desc = cat_info.get('description', '')
            
            categories.append({
                'id': category_id,
                'name': category_name,
                'description': category_desc,
                'source_file': include_path
            })
            
            # 各テストケースにカテゴリ情報を追加
            for case in category_data.get('cases', []):
                case['category_id'] = category_id
                case['category_name'] = category_name
                merged_cases.append(case)
        
        suite['cases'] = merged_cases
        suite['categories'] = categories
        del suite['includes']
    
    validate_suite(suite)
    return suite


def validate_suite(suite: dict) -> None:
    """
    スイートの基本整合性を検証する（重複IDなど）。
    破壊的変更はせず、問題があれば例外を投げる。
    """
    cases = suite.get("cases", []) if isinstance(suite, dict) else []
    ids = [c.get("id") for c in cases if isinstance(c, dict)]
    duplicates = sorted({i for i in ids if i and ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"テストケースIDが重複しています: {duplicates}")


def resolve_suite_asset_paths(suite: dict, suite_path: Path) -> dict:
    """
    suite 内の image_path を suite_path 基準で絶対パス化する。
    - 旧形式: case.request.messages[].content[].image_path
    - 新形式: case.variants[].image_path
    """
    suite_path = Path(suite_path).resolve()
    suite_dir = suite_path.parent

    def resolve_one(p: str) -> str:
        # 1) suite.yaml からの相対
        p1 = suite_dir / p
        if p1.exists():
            return str(p1)
        # 2) suite.yaml の親（bench/）からの相対（images が sibling のケース）
        p2 = suite_dir.parent / p
        if p2.exists():
            return str(p2)
        return str(p1)

    for case in suite.get("cases", []) if isinstance(suite, dict) else []:
        if not isinstance(case, dict):
            continue

        # legacy format
        req = case.get("request", {})
        if isinstance(req, dict):
            for msg in req.get("messages", []):
                if isinstance(msg, dict) and isinstance(msg.get("content"), list):
                    for item in msg["content"]:
                        if isinstance(item, dict) and item.get("type") == "image_url" and "image_path" in item:
                            item["image_path"] = resolve_one(item["image_path"])

        # variants format
        for variant in case.get("variants", []) if isinstance(case.get("variants"), list) else []:
            if isinstance(variant, dict) and variant.get("image_path"):
                variant["image_path"] = resolve_one(variant["image_path"])

    return suite


def expected_result_count_for_case(case: dict, runs: int) -> int:
    """
    run_bench_logic が「結果として push する件数」を見積もる。
    - variants あり: ケースごとに集約1件
    - 旧形式: runs 件
    """
    if isinstance(case, dict) and case.get("variants"):
        return 1
    return int(runs)


def expected_total_results(suite: dict, models_count: int, runs: int) -> int:
    cases = suite.get("cases", []) if isinstance(suite, dict) else []
    per_model = sum(expected_result_count_for_case(c, runs) for c in cases if isinstance(c, dict))
    return int(models_count) * int(per_model)

def get_models(base_url):
    client = OpenAI(base_url=base_url, api_key="lm-studio") # dummy key
    try:
        models = client.models.list()
        return [m.id for m in models.data]
    except Exception as e:
        print(f"Error fetching models: {e}")
        return []

def probe_vision_capability(base_url, model_id):
    """
    Probes if the model supports vision by sending a tiny image.
    This is a heuristic.
    """
    client = OpenAI(base_url=base_url, api_key="lm-studio")
    
    # 1x1 transparent png
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    try:
        client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe this."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{dummy_b64}"}}
                    ]
                }
            ],
            max_tokens=10
        )
        return True
    except APIError as e:
        # LM Studio typically returns 400 or specific error message for text-only models receiving images
        if "vision" in str(e).lower() or "image" in str(e).lower():
            return False
        return False # Assume failure means no vision if unsure
    except Exception:
        return False

# --- Evaluator ---

def _normalize_basic(text: str) -> str:
    return unicodedata.normalize("NFKC", (text or "")).casefold().strip()


def _normalize_loose(text: str) -> str:
    """
    句読点・空白類を落として比較したい用途向け（日本語にも効く）。
    """
    text = _normalize_basic(text)
    text = re.sub(r'[\s\.,!?;:、。！？；：「」『』（）\(\)\[\]【】{}<>＜＞"\'`]', '', text)
    return text


def _extract_first_json(text: str):
    """
    文字列から最初にパース可能な JSON (object/array) を抽出して返す。
    見つからない場合は (None, reason) を返す。
    """
    if not text:
        return None, "空文字"

    # fenced code block
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    candidates = []
    if fence:
        candidates.append(fence.group(1).strip())
    candidates.append(text)

    decoder = json.JSONDecoder()
    for cand in candidates:
        for m in re.finditer(r"[\{\[]", cand):
            s = cand[m.start():].lstrip()
            try:
                obj, _end = decoder.raw_decode(s)
                return obj, ""
            except Exception:
                continue
    return None, "JSONを検出できません"


def _extract_first_number(text: str, extract_regex=None):
    """
    テキストから数値を抽出する。見つからない場合は None。
    """
    if not text:
        return None
    src = text
    if extract_regex:
        m = re.search(extract_regex, src, re.MULTILINE)
        if not m:
            return None
        src = m.group(0)

    src = src.replace(",", "")
    nums = re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", src)
    if not nums:
        return None
    try:
        return float(nums[0])
    except Exception:
        return None


def evaluate_result(response_text, rule, llm_client=None, judge_model=None):
    """
    評価を実行し、結果とその詳細を返す。
    Returns: (passed: bool, details: dict)
    
    強化された評価タイプ:
    - exact_match: 完全一致
    - contains_all: 全キーワード含む
    - contains_any: いずれかのキーワード含む
    - json_parse: JSON形式チェック
    - numeric: 数値比較（許容誤差あり）
    - regex_match: 正規表現マッチ
    - normalized_contains: 正規化した上で部分一致（句読点・スペース無視）
    - fuzzy_match: 曖昧一致（編集距離ベース）
    - semantic_match: LLMによる意味的判定（最も正確）
    """
    eval_type = rule.get('type')
    details = {
        'eval_type': eval_type,
        'matched': None,
        'reason': ''
    }
    
    # テキストの正規化（NFKC + casefold）
    normalized = _normalize_basic(response_text)
    
    if eval_type == 'exact_match':
        expected = rule.get('expected', '')
        # alternativesがあれば複数パターンをチェック
        alternatives = rule.get('alternatives', [expected])
        if expected and expected not in alternatives:
            alternatives.insert(0, expected)
        
        for alt in alternatives:
            if response_text.strip() == alt.strip():
                details['matched'] = alt
                details['reason'] = f'完全一致: "{alt}"'
                return True, details
        
        details['reason'] = f'期待値: {alternatives[0] if alternatives else expected}'
        return False, details
    
    elif eval_type == 'normalized_contains':
        # 正規化して部分一致（句読点・空白・大小文字を無視）
        expected = rule.get('expected', '')
        alternatives = rule.get('alternatives', [expected])
        if expected and expected not in alternatives:
            alternatives.insert(0, expected)
        
        norm_response = _normalize_loose(response_text)
        
        for alt in alternatives:
            norm_alt = _normalize_loose(alt)
            if norm_alt in norm_response:
                details['matched'] = alt
                details['reason'] = f'正規化一致: "{alt}"'
                return True, details
        
        details['reason'] = f'正規化後も不一致: 期待="{alternatives[0]}"'
        return False, details
    
    elif eval_type == 'fuzzy_match':
        # 曖昧一致（レーベンシュタイン距離）
        expected = rule.get('expected', '')
        threshold = rule.get('threshold', 0.8)  # 80%以上の類似度で合格
        alternatives = rule.get('alternatives', [expected])
        if expected and expected not in alternatives:
            alternatives.insert(0, expected)
        normalize_mode = rule.get('normalize', 'basic')  # basic | loose
        
        def levenshtein_ratio(s1, s2):
            """レーベンシュタイン距離に基づく類似度（0-1）"""
            if len(s1) == 0 and len(s2) == 0:
                return 1.0
            
            # 簡易実装
            rows = len(s1) + 1
            cols = len(s2) + 1
            dist = [[0] * cols for _ in range(rows)]
            
            for i in range(rows):
                dist[i][0] = i
            for j in range(cols):
                dist[0][j] = j
            
            for i in range(1, rows):
                for j in range(1, cols):
                    cost = 0 if s1[i-1].lower() == s2[j-1].lower() else 1
                    dist[i][j] = min(
                        dist[i-1][j] + 1,
                        dist[i][j-1] + 1,
                        dist[i-1][j-1] + cost
                    )
            
            max_len = max(len(s1), len(s2))
            return 1 - (dist[rows-1][cols-1] / max_len) if max_len > 0 else 1.0
        
        response_clean = response_text.strip()
        response_clean = _normalize_loose(response_clean) if normalize_mode == "loose" else _normalize_basic(response_clean)
        best_ratio = 0
        best_match = None
        
        for alt in alternatives:
            alt_clean = alt.strip()
            alt_clean = _normalize_loose(alt_clean) if normalize_mode == "loose" else _normalize_basic(alt_clean)
            ratio = levenshtein_ratio(response_clean, alt_clean)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = alt
        
        if best_ratio >= threshold:
            details['matched'] = best_match
            details['reason'] = f'曖昧一致: {best_ratio*100:.1f}% (閾値: {threshold*100:.0f}%)'
            return True, details
        else:
            details['reason'] = f'類似度不足: {best_ratio*100:.1f}% < {threshold*100:.0f}%'
            return False, details
    
    elif eval_type == 'semantic_match':
        # LLMを使った意味的判定（最も正確）
        expected = rule.get('expected', '')
        alternatives = rule.get('alternatives', [])
        if expected:
            alternatives = [expected] + alternatives
        
        if not llm_client or not judge_model:
            # LLMが利用できない場合はfuzzy_matchにフォールバック
            details['reason'] = 'LLMジャッジ不可、fuzzy_matchにフォールバック'
            fallback_rule = {**rule, 'type': 'fuzzy_match', 'threshold': 0.7}
            return evaluate_result(response_text, fallback_rule)
        
        # LLMに判定させる
        expected_str = " または ".join([f'"{a}"' for a in alternatives[:3]])
        judge_prompt = f"""以下の回答が正しいかどうかを判定してください。

【期待される回答】
{expected_str}

【実際の回答】
"{response_text.strip()}"

【判定ルール】
- 意味が同じであれば正解（表現の違いは許容）
- 余分な説明があっても、核心部分が正しければ正解
- 明らかに間違っている場合は不正解

【回答形式】
1行目に "PASS" または "FAIL" のみを記載
2行目に理由を簡潔に記載"""
        
        try:
            judge_response = llm_client.chat.completions.create(
                model=judge_model,
                messages=[{"role": "user", "content": judge_prompt}],
                max_tokens=100,
                temperature=0
            )
            judge_text = judge_response.choices[0].message.content.strip()
            
            first_line = judge_text.split('\n')[0].strip().upper()
            reason_lines = judge_text.split('\n')[1:] if '\n' in judge_text else []
            reason = ' '.join(reason_lines).strip() if reason_lines else 'LLMジャッジ判定'
            
            if 'PASS' in first_line:
                details['matched'] = expected
                details['reason'] = f'意味一致: {reason}'
                return True, details
            else:
                details['reason'] = f'意味不一致: {reason}'
                return False, details
        except Exception as e:
            details['reason'] = f'LLMジャッジエラー: {str(e)[:50]}'
            # エラー時はfuzzy_matchにフォールバック
            fallback_rule = {**rule, 'type': 'fuzzy_match', 'threshold': 0.7}
            return evaluate_result(response_text, fallback_rule)
        
    elif eval_type == 'contains_all':
        keywords = rule.get('keywords', [])
        normalize_mode = rule.get('normalize', 'basic')  # basic | loose
        haystack = _normalize_loose(response_text) if normalize_mode == "loose" else normalized
        missing = [
            k for k in keywords
            if (_normalize_loose(k) if normalize_mode == "loose" else _normalize_basic(k)) not in haystack
        ]
        
        if not missing:
            details['matched'] = keywords
            details['reason'] = f'全キーワード検出: {keywords}'
            return True, details
        else:
            details['reason'] = f'未検出キーワード: {missing}'
            return False, details
    
    elif eval_type == 'contains_any':
        # いずれかのキーワードを含めば合格
        keyword_sets = rule.get('keyword_sets', [])
        keywords = rule.get('keywords', [])
        normalize_mode = rule.get('normalize', 'basic')  # basic | loose
        haystack = _normalize_loose(response_text) if normalize_mode == "loose" else normalized
        
        # keyword_setsがあればOR条件のセットとして評価
        if keyword_sets:
            for kw_set in keyword_sets:
                if all((_normalize_loose(k) if normalize_mode == "loose" else _normalize_basic(k)) in haystack for k in kw_set):
                    details['matched'] = kw_set
                    details['reason'] = f'キーワードセット検出: {kw_set}'
                    return True, details
            details['reason'] = f'いずれのキーワードセットも未検出'
            return False, details
        
        # 単純なOR条件
        found = [
            k for k in keywords
            if (_normalize_loose(k) if normalize_mode == "loose" else _normalize_basic(k)) in haystack
        ]
        if found:
            details['matched'] = found
            details['reason'] = f'キーワード検出: {found}'
            return True, details
        else:
            details['reason'] = f'いずれのキーワードも未検出: {keywords}'
            return False, details

    elif eval_type == 'json_parse':
        try:
            data, reason = _extract_first_json(response_text)
            if data is None:
                details['reason'] = f'JSON抽出失敗: {reason}'
                return False, details
            must_have = rule.get('must_have_keys', [])

            if isinstance(data, list):
                if must_have:
                    details['reason'] = f'JSON配列のためキー検証不可: 必須={must_have}'
                    return False, details
                details['matched'] = f"list(len={len(data)})"
                details['reason'] = 'JSONパース成功（配列）'
                return True, details

            if not isinstance(data, dict):
                details['reason'] = f'JSON形式が想定外: {type(data).__name__}'
                return False, details

            missing_keys = [k for k in must_have if k not in data]
            
            if not missing_keys:
                details['matched'] = list(data.keys())
                details['reason'] = f'JSONパース成功、必須キー: {must_have}'
                return True, details
            else:
                details['reason'] = f'不足キー: {missing_keys}'
                return False, details
        except json.JSONDecodeError as e:
            details['reason'] = f'JSONパースエラー: {str(e)[:50]}'
            return False, details
        except Exception as e:
            details['reason'] = f'エラー: {str(e)[:50]}'
            return False, details

    elif eval_type == 'numeric':
        try:
            extract_regex = rule.get('extract_regex')
            val = _extract_first_number(response_text, extract_regex=extract_regex)
            if val is None:
                details['reason'] = '数値が見つかりません'
                return False, details

            if 'expected_range' in rule:
                lo, hi = rule.get('expected_range', [None, None])
                lo = float(lo)
                hi = float(hi)
                if lo <= val <= hi:
                    details['matched'] = val
                    details['reason'] = f'数値が範囲内: {val} (期待: {lo}..{hi})'
                    return True, details
                details['reason'] = f'数値が範囲外: {val} (期待: {lo}..{hi})'
                return False, details

            expected = float(rule.get('expected'))
            tolerance = float(rule.get('tolerance', 0))
            rel_tol = float(rule.get('relative_tolerance', 0))
            allowed = max(tolerance, abs(expected) * rel_tol)

            if abs(val - expected) <= allowed:
                details['matched'] = val
                details['reason'] = f'数値一致: {val} (期待値: {expected}±{allowed})'
                return True, details

            details['reason'] = f'数値不一致: {val} ≠ {expected}'
            return False, details
        except Exception as e:
            details['reason'] = f'数値評価エラー: {str(e)[:50]}'
            return False, details
    
    elif eval_type == 'regex_match':
        pattern = rule.get('pattern', '')
        # alternativesパターンがあれば複数チェック
        patterns = rule.get('alternatives', [pattern])
        if pattern and pattern not in patterns:
            patterns.insert(0, pattern)
        
        for pat in patterns:
            match = re.search(pat, response_text, re.MULTILINE | re.IGNORECASE)
            if match:
                details['matched'] = match.group(0)
                details['reason'] = f'パターン一致: "{match.group(0)}"'
                return True, details
        
        details['reason'] = f'パターン不一致'
        return False, details

    elif eval_type == 'regex_fullmatch':
        pattern = rule.get('pattern', '')
        patterns = rule.get('alternatives', [pattern])
        if pattern and pattern not in patterns:
            patterns.insert(0, pattern)

        flags = 0
        for f in rule.get('flags', []) or []:
            if f == "IGNORECASE":
                flags |= re.IGNORECASE
            elif f == "MULTILINE":
                flags |= re.MULTILINE
            elif f == "DOTALL":
                flags |= re.DOTALL

        for pat in patterns:
            m = re.fullmatch(pat, response_text.strip(), flags=flags)
            if m:
                details['matched'] = m.group(0)
                details['reason'] = '完全一致（正規表現）'
                return True, details

        details['reason'] = '完全一致（正規表現）に失敗'
        return False, details

    details['reason'] = f'不明な評価タイプ: {eval_type}'
    return False, details


def evaluate_result_simple(response_text, rule):
    """後方互換性のためのシンプルなラッパー"""
    passed, _ = evaluate_result(response_text, rule)
    return passed

# --- Runner ---

# --- Runner ---

def run_bench_logic(suite, base_url, model_pattern, runs, warmup, timeout, 
                    progress_callback=None, use_llm_judge=False, judge_model=None,
                    cancel_check=None):
    """
    Core benchmark logic.
    progress_callback: function(event_type, data)
    use_llm_judge: bool - LLMをジャッジとして使用するか
    judge_model: str - ジャッジに使うモデル（Noneの場合はテスト対象と同じ）
    """
    if progress_callback: progress_callback("info", f"Connecting to {base_url}...")
    
    available_models = get_models(base_url)
    if not available_models:
        if progress_callback: progress_callback("error", "No models found.")
        return []

    target_models = []
    for m in available_models:
        if re.match(model_pattern, m):
            target_models.append(m)
    
    if progress_callback: progress_callback("info", f"Target Models: {target_models}")

    model_tags = {}
    has_vision_cases = any(c.get('modality') == 'vision' for c in suite['cases'])
    
    for m in target_models:
        tags = set(["text"])
        if has_vision_cases:
            if progress_callback: progress_callback("info", f"Probing vision capability for {m}...")
            if probe_vision_capability(base_url, m):
                tags.add("vision")
        model_tags[m] = tags
        if progress_callback: progress_callback("info", f"Model {m} tags: {tags}")

    client = OpenAI(base_url=base_url, api_key="lm-studio")
    results = []
    
    timestamp = datetime.now().isoformat()
    meta = suite.get('meta', {})

    for model in target_models:
        if cancel_check and cancel_check():
            if progress_callback: progress_callback("info", "キャンセルされました（モデル開始前）")
            break
        tags = model_tags[model]
        
        for case in suite['cases']:
            if cancel_check and cancel_check():
                if progress_callback: progress_callback("info", "キャンセルされました（ケース開始前）")
                break
            req_tags = set(case.get('required_tags', []))
            if not req_tags.issubset(tags):
                res = {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "case_id": case['id'],
                    "case_name": case.get('name', case['id']),
                    "case_description": case.get('description', ''),
                    "category_id": case.get('category_id', ''),
                    "category_name": case.get('category_name', ''),
                    "status": "skipped",
                    "reason": "missing_capabilities"
                }
                results.append(res)
                if progress_callback: progress_callback("result", res)
                continue

            # ========================================
            # variants形式のテストケースかどうかをチェック
            # ========================================
            variants = case.get('variants', None)
            
            if variants:
                # ========================================
                # 新形式: variants を持つテストケース
                # ========================================
                pass_threshold = case.get('pass_threshold', 0.8)
                variant_results = []
                
                for v_idx, variant in enumerate(variants):
                    # バリエーションのプロンプトを構築
                    variant_prompt = variant.get('prompt', '')
                    variant_eval = variant.get('evaluation', {})
                    
                    # システムプロンプトがケースレベルにあれば使用
                    system_prompt = case.get('system_prompt', '')
                    
                    variant_messages = []
                    if system_prompt:
                        variant_messages.append({"role": "system", "content": system_prompt})
                    
                    # 画像が指定されている場合
                    image_path = variant.get('image_path')
                    image_missing = False
                    
                    if image_path:
                        # 画像パスはrun_benchですでに絶対パスに解決されている
                        if os.path.exists(image_path):
                            try:
                                base64_image = encode_image(image_path)
                                user_content = [
                                    {"type": "text", "text": variant_prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
                                ]
                                variant_messages.append({"role": "user", "content": user_content})
                            except Exception as e:
                                print(f"Error encoding image {image_path}: {e}")
                                image_missing = True
                                missing_reason = str(e)
                        else:
                            print(f"Error: Image not found at {image_path}")
                            image_missing = True
                            missing_reason = f"File not found: {image_path}"
                    else:
                        variant_messages.append({"role": "user", "content": variant_prompt})
                    
                    if image_missing:
                         # 画像エラー時はAPI呼び出しをスキップしてエラー記録
                        for i in range(runs):
                            variant_results.append({
                                "variant_index": v_idx,
                                "run_index": i,
                                "passed": False,
                                "status": "error",
                                "ttft_ms": 0,
                                "e2e_ms": 0,
                                "prompt": variant_prompt,
                                "response": f"Image Error: {missing_reason}",
                                "eval_reason": "Image load failed",
                                "expected": variant_eval.get('expected', '')
                            })
                        continue

                    # 各バリエーションをruns回実行
                    for i in range(runs):
                        if cancel_check and cancel_check():
                            variant_results.append({
                                "variant_index": v_idx,
                                "run_index": i,
                                "passed": False,
                                "status": "skipped",
                                "ttft_ms": 0,
                                "e2e_ms": 0,
                                "prompt": variant_prompt,
                                "response": "Cancelled",
                                "eval_reason": "キャンセル",
                                "expected": variant_eval.get('expected', '')
                            })
                            continue
                        start_time = time.perf_counter()
                        ttft = None
                        full_response = ""
                        status = "ok"
                        error_type = ""
                        
                        try:
                            stream = client.chat.completions.create(
                                model=model,
                                messages=variant_messages,
                                max_tokens=meta.get('default_params', {}).get('max_tokens', 256),
                                temperature=meta.get('default_params', {}).get('temperature', 0),
                                stream=True,
                                timeout=timeout
                            )
                            
                            first_chunk = True
                            for chunk in stream:
                                if cancel_check and cancel_check():
                                    status = "skipped"
                                    error_type = "Cancelled"
                                    break
                                if chunk.choices and chunk.choices[0].delta.content:
                                    content_chunk = chunk.choices[0].delta.content
                                    if first_chunk:
                                        ttft = (time.perf_counter() - start_time) * 1000
                                        first_chunk = False
                                    full_response += content_chunk
                            
                            end_time = time.perf_counter()
                            e2e = (end_time - start_time) * 1000
                            if ttft is None: ttft = e2e

                        except Exception as e:
                            status = "error"
                            error_type = type(e).__name__
                            e2e = (time.perf_counter() - start_time) * 1000
                            full_response = str(e)
                        
                        passed = False
                        eval_details = {}
                        expected_answer = variant_eval.get('expected', '')
                        
                        if status == "ok":
                            judge_llm_client = client if use_llm_judge else None
                            judge_llm_model = judge_model if judge_model else model
                            passed, eval_details = evaluate_result(
                                full_response, 
                                variant_eval, 
                                llm_client=judge_llm_client if use_llm_judge else None,
                                judge_model=judge_llm_model if use_llm_judge else None
                            )
                        
                        variant_results.append({
                            "variant_index": v_idx,
                            "run_index": i,
                            "passed": passed,
                            "status": status,
                            "ttft_ms": ttft,
                            "e2e_ms": e2e,
                            "prompt": variant_prompt,
                            "response": full_response,
                            "eval_reason": eval_details.get('reason', ''),
                            "expected": expected_answer
                        })
                
                # 総合判定
                valid_results = [v for v in variant_results if v['status'] == 'ok']
                pass_count = sum(1 for v in valid_results if v['passed'])
                total_count = len(valid_results)
                pass_rate = pass_count / total_count if total_count > 0 else 0
                overall_passed = pass_rate >= pass_threshold
                
                # 平均レイテンシ計算
                ok_lat = [v for v in variant_results if v.get("status") == "ok"]
                avg_ttft = (sum(v['ttft_ms'] or 0 for v in ok_lat) / len(ok_lat)) if ok_lat else 0
                avg_e2e = (sum(v['e2e_ms'] or 0 for v in ok_lat) / len(ok_lat)) if ok_lat else 0
                
                # 総合結果を記録
                res = {
                    "timestamp": datetime.now().isoformat(),
                    "model": model,
                    "case_id": case['id'],
                    "case_name": case.get('name', case['id']),
                    "case_description": case.get('description', ''),
                    "category_id": case.get('category_id', ''),
                    "category_name": case.get('category_name', ''),
                    "run_index": 0,
                    "status": "ok",
                    "error_type": "",
                    "ttft_ms": avg_ttft,
                    "e2e_ms": avg_e2e,
                    "passed": overall_passed,
                    "human_override": None,
                    "eval_reason": f"合格率: {pass_count}/{total_count} = {pass_rate*100:.0f}% (閾値: {pass_threshold*100:.0f}%)",
                    "eval_matched": None,
                    "expected_answer": f"閾値 {pass_threshold*100:.0f}% 以上",
                    "test_prompt": f"[{len(variants)}個のバリエーション]",
                    "response_preview": f"合格: {pass_count}/{total_count}",
                    "full_response": json.dumps(variant_results, ensure_ascii=False, indent=2),
                    # 追加フィールド
                    "is_variant_test": True,
                    "variant_count": len(variants),
                    "variant_pass_count": pass_count,
                    "variant_total_count": total_count,
                    "variant_pass_rate": pass_rate,
                    "variant_threshold": pass_threshold,
                    "variant_details": variant_results
                }
                
                results.append(res)
                if progress_callback: progress_callback("result", res)
            
            else:
                # ========================================
                # 旧形式: 単一テストケース（後方互換性）
                # ========================================
                # Prepare Messages
                messages = case['request']['messages']
                final_messages = []
                for msg in messages:
                    new_msg = {"role": msg["role"]}
                    content = msg["content"]
                    if isinstance(content, list):
                        new_content = []
                        for item in content:
                            if item["type"] == "image_url":
                                image_path = item.get("image_path")
                                if not os.path.exists(image_path):
                                    pass
                                
                                try:
                                    b64 = encode_image(image_path)
                                    new_content.append({
                                        "type": "image_url",
                                        "image_url": {"url": f"data:image/png;base64,{b64}"}
                                    })
                                except Exception as e:
                                    print(f"Error loading image {image_path}: {e}")
                            else:
                                new_content.append(item)
                        new_msg["content"] = new_content
                    else:
                        new_msg["content"] = content
                    final_messages.append(new_msg)

                # Warmup
                for _ in range(warmup):
                    try:
                        client.chat.completions.create(
                            model=model,
                            messages=final_messages,
                            max_tokens=10,
                            stream=False
                        )
                    except: pass

                # Runs
                for i in range(runs):
                    if cancel_check and cancel_check():
                        if progress_callback: progress_callback("info", "キャンセルされました（run開始前）")
                        break
                    start_time = time.perf_counter()
                    ttft = None
                    full_response = ""
                    status = "ok"
                    error_type = ""
                    
                    try:
                        stream = client.chat.completions.create(
                            model=model,
                            messages=final_messages,
                            max_tokens=meta.get('default_params', {}).get('max_tokens', 256),
                            temperature=meta.get('default_params', {}).get('temperature', 0),
                            stream=True,
                            timeout=timeout
                        )
                        
                        first_chunk = True
                        for chunk in stream:
                            if cancel_check and cancel_check():
                                status = "skipped"
                                error_type = "Cancelled"
                                break
                            if chunk.choices and chunk.choices[0].delta.content:
                                content_chunk = chunk.choices[0].delta.content
                                if first_chunk:
                                    ttft = (time.perf_counter() - start_time) * 1000
                                    first_chunk = False
                                full_response += content_chunk
                        
                        end_time = time.perf_counter()
                        e2e = (end_time - start_time) * 1000
                        if ttft is None: ttft = e2e

                    except Exception as e:
                        status = "error"
                        error_type = type(e).__name__
                        e2e = (time.perf_counter() - start_time) * 1000
                        full_response = str(e)
                    
                    passed = False
                    eval_details = {}
                    expected_answer = ""
                    
                    if status == "ok":
                        eval_rule = case.get('eval', {})
                        expected_answer = case.get('expected_answer', '')
                        
                        if not expected_answer:
                            if eval_rule.get('expected'):
                                expected_answer = str(eval_rule['expected'])
                            elif eval_rule.get('keywords'):
                                expected_answer = f"キーワード: {', '.join(eval_rule['keywords'])}"
                            elif eval_rule.get('pattern'):
                                expected_answer = f"パターン: {eval_rule['pattern']}"
                        
                        judge_llm_client = client if use_llm_judge else None
                        judge_llm_model = judge_model if judge_model else model
                        passed, eval_details = evaluate_result(
                            full_response, 
                            eval_rule, 
                            llm_client=judge_llm_client if use_llm_judge else None,
                            judge_model=judge_llm_model if use_llm_judge else None
                        )
                    
                    # プロンプトを抽出
                    test_prompt = ""
                    for msg in case['request']['messages']:
                        role = msg.get('role', 'user')
                        content = msg.get('content', '')
                        if isinstance(content, str):
                            test_prompt += f"[{role}]\n{content}\n\n"
                        elif isinstance(content, list):
                            for item in content:
                                if item.get('type') == 'text':
                                    test_prompt += f"[{role}]\n{item.get('text', '')}\n\n"
                                elif item.get('type') == 'image_url':
                                    test_prompt += f"[{role}]\n[画像: {item.get('image_path', 'image')}]\n\n"
                    
                    res = {
                        "timestamp": datetime.now().isoformat(),
                        "model": model,
                        "case_id": case['id'],
                        "case_name": case.get('name', case['id']),
                        "case_description": case.get('description', ''),
                        "category_id": case.get('category_id', ''),
                        "category_name": case.get('category_name', ''),
                        "run_index": i,
                        "status": status,
                        "error_type": error_type,
                        "ttft_ms": ttft,
                        "e2e_ms": e2e,
                        "passed": passed,
                        "human_override": None,
                        "eval_reason": eval_details.get('reason', ''),
                        "eval_matched": eval_details.get('matched'),
                        "expected_answer": expected_answer,
                        "test_prompt": test_prompt.strip(),
                        "response_preview": full_response[:100].replace("\n", " "),
                        "full_response": full_response,
                        "is_variant_test": False
                    }
                    
                    results.append(res)
                    if progress_callback: progress_callback("result", res)

    return results

def run_bench(args):
    # Ensure suite path is absolute to resolve image paths correctly
    suite_path = Path(args.suite).resolve()
    suite = load_suite(suite_path)
    suite_dir = suite_path.parent
    
    suite = resolve_suite_asset_paths(suite, suite_path)

    meta = suite.get('meta', {})
    base_url = args.base_url or meta.get('base_url', "http://localhost:1234/v1")
    runs = args.runs or meta.get('runs', 1)
    warmup = args.warmup if args.warmup is not None else meta.get('warmup', 0)
    timeout = args.timeout or meta.get('timeout_sec', 30)
    model_pattern = args.models or ".*"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    jsonl_path = out_dir / f"results_{timestamp_str}.jsonl"

    def cli_callback(kind, data):
        if kind == "info":
            print(data)
        elif kind == "result":
            icon = "○" if data.get('passed') else "×"
            if data['status'] == "error":
                icon = "！"
            elif data['status'] == "skipped":
                icon = "－"
            
            # アイコン文字化け対策（ASCIIに固定）
            icon = "[OK]" if data.get('passed') else "[NG]"
            if data['status'] == "error":
                icon = "[ERR]"
            elif data['status'] == "skipped":
                icon = "[SKIP]"

            case_name = data.get('case_name', data['case_id'])
            category = data.get('category_name', '')
            if data['status'] == 'skipped':
                print(f"[{data['model']}] [{category}] {case_name}: {icon} ({data.get('reason')})")
            else:
                ttft = data.get('ttft_ms', 0) or 0
                e2e = data.get('e2e_ms', 0) or 0
                print(f"[{data['model']}] [{category}] {case_name} #{data.get('run_index')}: {icon} (TTFT: {ttft:.1f}ms, E2E: {e2e:.1f}ms)")
            
            # Write to file immediately
            with open(jsonl_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data) + "\n")

    results = run_bench_logic(suite, base_url, model_pattern, runs, warmup, timeout, cli_callback)
    
    generate_html_report(results, out_dir / f"report_{timestamp_str}.html")
    print(f"Done. Report saved to {out_dir}")

def generate_html_report(results, path):
    """Generate an HTML report with category-based organization and modern dark UI."""
    html = """
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>LLM Benchmark Report</title>
        <style>
            :root {
                --bg-primary: #1a1a2e;
                --bg-secondary: #16213e;
                --bg-card: #0f3460;
                --text-primary: #eee;
                --text-secondary: #aaa;
                --accent: #e94560;
                --success: #4ade80;
                --error: #f87171;
                --warning: #fbbf24;
                --border: #334155;
            }
            * { box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', 'Meiryo', sans-serif;
                background: var(--bg-primary);
                color: var(--text-primary);
                padding: 2rem;
                margin: 0;
                line-height: 1.6;
            }
            h1 { 
                color: var(--accent);
                border-bottom: 2px solid var(--accent);
                padding-bottom: 0.5rem;
                margin-bottom: 1.5rem;
            }
            h2 { 
                color: var(--text-primary);
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            h3 { color: var(--text-secondary); margin-top: 1.5rem; }
            table { 
                border-collapse: collapse;
                width: 100%;
                margin-bottom: 1.5rem;
                background: var(--bg-secondary);
                border-radius: 8px;
                overflow: hidden;
            }
            th, td { 
                border: 1px solid var(--border);
                padding: 0.75rem 1rem;
                text-align: left;
            }
            th { background-color: var(--bg-card); color: var(--text-primary); }
            tr:hover { background-color: rgba(233, 69, 96, 0.1); }
            .pass { color: var(--success); font-weight: bold; }
            .fail { color: var(--error); }
            .error { color: var(--warning); }
            .skipped { color: var(--text-secondary); font-style: italic; }
            .category-tag {
                display: inline-block;
                background: var(--accent);
                color: white;
                padding: 0.2rem 0.6rem;
                border-radius: 4px;
                font-size: 0.85rem;
                margin-right: 0.5rem;
            }
            .description { 
                font-size: 0.9rem;
                color: var(--text-secondary);
                margin-top: 0.25rem;
            }
            pre { 
                background: var(--bg-primary);
                padding: 0.5rem;
                border-radius: 4px;
                overflow-x: auto;
                font-size: 0.85rem;
                margin: 0;
                max-width: 400px;
                white-space: pre-wrap;
                word-break: break-word;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }
            .summary-card {
                background: var(--bg-secondary);
                border-radius: 8px;
                padding: 1rem;
                border-left: 4px solid var(--accent);
            }
            .summary-card h4 { margin: 0 0 0.5rem 0; color: var(--text-primary); }
            .summary-card .stats { display: flex; gap: 1rem; flex-wrap: wrap; }
            .stat { text-align: center; }
            .stat-value { font-size: 1.5rem; font-weight: bold; color: var(--accent); }
            .stat-label { font-size: 0.8rem; color: var(--text-secondary); }
        </style>
    </head>
    <body>
    <h1>🔬 LLM Benchmark Report</h1>
    """
    
    if not results:
        html += "<p>No results.</p></body></html>"
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        return

    # --- Category Summary Cards ---
    html += "<h2>📊 カテゴリ別サマリ</h2><div class='summary-grid'>"
    
    # Group by category
    by_category = {}
    for r in results:
        cat = r.get('category_name', 'Unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(r)
    
    for cat_name, cat_results in by_category.items():
        valid = [r for r in cat_results if r['status'] == 'ok']
        passed = [r for r in valid if r.get('passed')]
        pass_rate = (len(passed) / len(valid) * 100) if valid else 0
        avg_ttft = sum(r.get('ttft_ms', 0) or 0 for r in valid) / len(valid) if valid else 0
        
        html += f"""
        <div class="summary-card">
            <h4>{cat_name}</h4>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{pass_rate:.0f}%</div>
                    <div class="stat-label">正解率</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{len(valid)}</div>
                    <div class="stat-label">テスト数</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{avg_ttft:.0f}ms</div>
                    <div class="stat-label">平均TTFT</div>
                </div>
            </div>
        </div>
        """
    html += "</div>"

    # --- Summary Table by Model & Case ---
    html += "<h2>📋 モデル別詳細</h2>"
    html += "<table><tr><th>モデル</th><th>カテゴリ</th><th>テスト名</th><th>正解率</th><th>Avg TTFT</th><th>Avg E2E</th></tr>"
    
    grouped = {}
    for r in results:
        key = (r['model'], r['case_id'])
        if key not in grouped:
            grouped[key] = {
                'items': [],
                'case_name': r.get('case_name', r['case_id']),
                'category_name': r.get('category_name', ''),
                'description': r.get('case_description', '')
            }
        grouped[key]['items'].append(r)
        
    for key, data in grouped.items():
        model, case_id = key
        items = data['items']
        valid_runs = [x for x in items if x['status'] == 'ok']
        pass_runs = [x for x in valid_runs if x['passed']]
        
        valid_count = len(valid_runs)
        pass_rate = (len(pass_runs) / valid_count) * 100 if valid_count else 0
        
        ttfts = [x['ttft_ms'] for x in valid_runs if x['ttft_ms'] is not None]
        avg_ttft = sum(ttfts)/len(ttfts) if ttfts else 0
        
        e2es = [x['e2e_ms'] for x in valid_runs]
        avg_e2e = sum(e2es)/len(e2es) if e2es else 0
        
        pass_class = "pass" if pass_rate >= 80 else ("fail" if pass_rate < 50 else "")
        
        html += f"<tr><td>{html_lib.escape(model)}</td>"
        html += f"<td><span class='category-tag'>{html_lib.escape(data['category_name'])}</span></td>"
        html += f"<td>{html_lib.escape(data['case_name'])}<div class='description'>{html_lib.escape(data['description'])}</div></td>"
        html += f"<td class='{pass_class}'>{pass_rate:.1f}%</td>"
        html += f"<td>{avg_ttft:.1f}ms</td><td>{avg_e2e:.1f}ms</td></tr>"

    html += "</table>"
    
    # --- Details Table ---
    html += "<h2>📝 全結果詳細</h2>"
    html += "<table><tr><th>時刻</th><th>モデル</th><th>カテゴリ</th><th>テスト</th><th>結果</th><th>TTFT</th><th>レスポンス</th></tr>"
    
    for r in results:
        if r['status'] == 'skipped':
            status_class = 'skipped'
            result_str = "SKIP"
        elif r['status'] == 'error':
            status_class = 'error'
            result_str = "ERROR"
        elif r.get('passed'):
            status_class = 'pass'
            result_str = "✓ PASS"
        else:
            status_class = 'fail'
            result_str = "✗ FAIL"
        
        preview = html_lib.escape(r.get('response_preview', ''))
        case_name = html_lib.escape(r.get('case_name', r['case_id']))
        cat_name = html_lib.escape(r.get('category_name', ''))
        ttft = r.get('ttft_ms', 0) or 0
        
        html += f"<tr class='{status_class}'>"
        html += f"<td>{r['timestamp']}</td>"
        html += f"<td>{html_lib.escape(r['model'])}</td>"
        html += f"<td><span class='category-tag'>{cat_name}</span></td>"
        html += f"<td>{case_name}</td>"
        html += f"<td>{result_str}</td>"
        html += f"<td>{ttft:.1f}ms</td>"
        html += f"<td><pre>{preview}</pre></td></tr>"
        
    html += "</table></body></html>"
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", required=True)
    parser.add_argument("--out", default="./out")
    parser.add_argument("--base-url")
    parser.add_argument("--models") # regex
    parser.add_argument("--runs", type=int)
    parser.add_argument("--warmup", type=int)
    parser.add_argument("--timeout", type=int)
    
    args = parser.parse_args()
    run_bench(args)
