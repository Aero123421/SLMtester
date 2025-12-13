from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
from typing import Optional, List, Dict, Any
import json
import os
from pathlib import Path
import httpx
import traceback
import re

# Fix imports to work from both root and bench dir
try:
    from bench.main import (
        run_bench_logic,
        load_suite,
        get_models as get_models_sync,
        resolve_suite_asset_paths,
        expected_total_results,
    )
except ImportError:
    from main import (
        run_bench_logic,
        load_suite,
        get_models as get_models_sync,
        resolve_suite_asset_paths,
        expected_total_results,
    )

app = FastAPI()

# Make sure static dir exists
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
os.makedirs(STATIC_DIR, exist_ok=True)

# State
JOBS = {}

class BenchRequest(BaseModel):
    suite_path: str = "bench/suite.yaml"
    base_url: str = "http://localhost:1234/v1"
    models: List[str] = []  # Explicit list of model IDs
    runs: int = 1
    warmup: int = 0
    timeout: int = 60
    use_llm_judge: bool = False  # LLMジャッジを使用するか
    judge_model: Optional[str] = None  # ジャッジに使用するモデル（Noneの場合はテスト対象と同じ）


@app.get("/api/models")
async def get_models(base_url: str = "http://localhost:1234/v1"):
    """
    Fetch models from LM Studio using REST API v0.
    Returns model list with type (llm/vlm) and state (loaded/not-loaded).
    """
    try:
        # Use LM Studio's native REST API for richer info
        api_v0_url = base_url.replace("/v1", "/api/v0/models")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(api_v0_url)
            
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    # Filter out embedding models
                    if m.get("type") == "embeddings":
                        continue
                    models.append({
                        "id": m.get("id"),
                        "type": m.get("type", "llm"),  # llm or vlm
                        "state": m.get("state", "not-loaded"),
                        "quantization": m.get("quantization"),
                        "arch": m.get("arch")
                    })
                return {"models": models}
            else:
                # Fallback to OpenAI-compatible endpoint
                return await get_models_fallback(base_url)
                
    except httpx.ConnectError:
        return {"error": "LM Studioに接続できません。サーバーが起動しているか確認してください。", "models": []}
    except Exception as e:
        return {"error": str(e), "models": []}


async def get_models_fallback(base_url: str):
    """Fallback to OpenAI-compatible /v1/models endpoint"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{base_url}/models")
            if resp.status_code == 200:
                data = resp.json()
                models = []
                for m in data.get("data", []):
                    model_id = m.get("id", "")
                    # Heuristic: VLM detection by name
                    is_vlm = any(kw in model_id.lower() for kw in ["vl", "vision", "llava", "qwen2-vl"])
                    models.append({
                        "id": model_id,
                        "type": "vlm" if is_vlm else "llm",
                        "state": "loaded"  # If returned by /v1/models, assume loaded
                    })
                return {"models": models}
    except:
        pass
    return {"error": "モデル一覧の取得に失敗しました", "models": []}

def run_lms_command_sync(args: list, timeout: int = 60) -> dict:
    """Run lms command synchronously and return result dict"""
    import subprocess
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='replace',
            shell=False
        )
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        if result.returncode == 0:
            return {"success": True, "output": stdout or "完了"}
        else:
            return {"success": False, "output": stderr or stdout or "コマンドが失敗しました"}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "タイムアウト: 処理に時間がかかりすぎています"}
    except FileNotFoundError:
        return {"success": False, "output": "'lms' コマンドが見つかりません。LM Studio CLIをインストールしてください。"}
    except Exception as e:
        return {"success": False, "output": f"エラー: {str(e)}"}


def list_models_v0_sync(base_url: str) -> Optional[List[Dict[str, Any]]]:
    """LM Studio REST API v0 /api/v0/models からモデル一覧を取得（同期）。失敗時は None。"""
    try:
        api_v0_url = base_url.replace("/v1", "/api/v0/models")
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(api_v0_url)
            if resp.status_code != 200:
                return None
            data = resp.json()
            return data.get("data", [])
    except Exception:
        return None


def ensure_single_loaded_model(base_url: str, target_model_id: str, job: dict) -> bool:
    """
    できるだけ「ロード済みは最大1つ」を保証する。
    - 先に他のロード済みモデルをアンロード
    - target が未ロードならロード
    - 最後に target がロード済みか軽く確認
    Returns: 成功なら True
    """
    models = list_models_v0_sync(base_url)
    if models is None:
        job["logs"].append({"type": "warn", "msg": "モデル状態の取得に失敗しました（/api/v0/models）。単一ロードを完全に保証できない可能性があります。"})
    else:
        loaded = [m.get("id") for m in models if m.get("state") == "loaded" and m.get("id")]
        for mid in loaded:
            if mid != target_model_id:
                job["logs"].append({"type": "info", "msg": f"アンロード: {mid}"})
                r = run_lms_command_sync(["lms", "unload", mid], timeout=60)
                if not r.get("success"):
                    job["logs"].append({"type": "warn", "msg": f"アンロード失敗: {mid} ({r.get('output')})"})

    # load target if needed
    models_after = list_models_v0_sync(base_url) or []
    is_loaded = any(m.get("id") == target_model_id and m.get("state") == "loaded" for m in models_after)
    if not is_loaded:
        job["logs"].append({"type": "info", "msg": f"ロード: {target_model_id}（数分かかる場合があります）"})
        r = run_lms_command_sync(["lms", "load", target_model_id], timeout=300)
        if not r.get("success"):
            job["logs"].append({"type": "error", "msg": f"ロード失敗: {target_model_id} ({r.get('output')})"})
            return False

    # best-effort wait until loaded
    for _ in range(60):  # up to ~60s
        models_wait = list_models_v0_sync(base_url)
        if models_wait is None:
            return True
        if any(m.get("id") == target_model_id and m.get("state") == "loaded" for m in models_wait):
            return True
        import time
        time.sleep(1)

    job["logs"].append({"type": "warn", "msg": f"ロード確認がタイムアウトしました: {target_model_id}"})
    return True


@app.get("/api/suite")
def get_suite_info(suite_path: str = "bench/suite.yaml"):
    """Get test suite information with categories and test cases"""
    try:
        suite = load_suite(Path(suite_path).resolve())
        
        # カテゴリ情報を整理
        categories = suite.get('categories', [])
        cases = suite.get('cases', [])
        meta = suite.get("meta", {}) or {}
        
        # カテゴリ別にテストをグループ化
        by_category = {}
        for case in cases:
            cat_id = case.get('category_id', 'unknown')
            if cat_id not in by_category:
                by_category[cat_id] = {
                    'id': cat_id,
                    'name': case.get('category_name', 'Unknown'),
                    'tests': []
                }
                by_category[cat_id]['tests'].append({
                    'id': case.get('id'),
                    'name': case.get('name', case.get('id')),
                    'description': case.get('description', ''),
                    'modality': case.get('modality', 'text'),
                    'weight': case.get('weight', 3)
                })
        
        return {
            'total_tests': len(cases),
            'categories': list(by_category.values()),
            'meta': meta,
            'suite_path': Path(suite_path).as_posix()
        }
    except Exception as e:
        return {'error': str(e), 'categories': [], 'total_tests': 0, 'meta': {}, 'suite_path': Path(suite_path).as_posix()}


@app.post("/api/bm/start")
async def start_bm(req: BenchRequest, background_tasks: BackgroundTasks):
    """Start a benchmark job"""
    if not req.models:
        return {"error": "モデルが選択されていません"}
    
    job_id = str(uuid.uuid4())
    
    # Load suite to validate
    try:
        suite = load_suite(req.suite_path)
    except Exception as e:
        return {"error": f"スイートファイルの読み込みに失敗: {str(e)}"}
    
    JOBS[job_id] = {
        "status": "running",
        "cancelled": False,
        "logs": [],
        "results": [],
        "expected_total": expected_total_results(suite, len(req.models), req.runs),
        "suite_path": req.suite_path,
        "suite_meta": suite.get("meta", {}) or {},
    }
    
    background_tasks.add_task(run_bm_task, job_id, req)
    return {"job_id": job_id, "expected_total": JOBS[job_id]["expected_total"]}


@app.post("/api/bm/{job_id}/cancel")
def cancel_bm(job_id: str):
    """Cancel a running benchmark job (best-effort)."""
    if job_id not in JOBS:
        return JSONResponse({"error": "ジョブが見つかりません"}, status_code=404)
    JOBS[job_id]["cancelled"] = True
    JOBS[job_id]["logs"].append({"type": "warn", "msg": "キャンセル要求を受け付けました"})
    return {"success": True}


@app.get("/api/bm/{job_id}")
def get_bm_status(job_id: str):
    """Get benchmark job status"""
    if job_id not in JOBS:
        return JSONResponse({"error": "ジョブが見つかりません"}, status_code=404)
    return JOBS[job_id]


class OverrideRequest(BaseModel):
    result_index: int
    new_passed: bool
    
    class Config:
        protected_namespaces = ()


@app.post("/api/bm/{job_id}/override")
def override_result(job_id: str, req: OverrideRequest):
    """
    人間が結果の合格/不合格を手動で変更する
    """
    if job_id not in JOBS:
        return JSONResponse({"error": "ジョブが見つかりません"}, status_code=404)
    
    job = JOBS[job_id]
    
    if req.result_index < 0 or req.result_index >= len(job["results"]):
        return JSONResponse({"error": "結果インデックスが無効です"}, status_code=400)
    
    result = job["results"][req.result_index]
    old_passed = result.get("passed")
    
    # 人間による上書き
    result["human_override"] = req.new_passed
    result["passed"] = req.new_passed
    
    action = "合格に変更" if req.new_passed else "不合格に変更"
    job["logs"].append({
        "type": "info", 
        "msg": f"[手動変更] {result['case_name']}: {action}"
    })
    
    return {
        "success": True, 
        "message": f"結果を{action}しました",
        "old_passed": old_passed,
        "new_passed": req.new_passed
    }

def run_bm_task(job_id: str, req: BenchRequest):
    """Background task to run benchmark"""
    job = JOBS[job_id]
    
    def callback(kind, data):
        if kind == "info":
            job["logs"].append({"type": "info", "msg": data})
        elif kind == "error":
            job["logs"].append({"type": "error", "msg": data})
        elif kind == "result":
            job["results"].append(data)
            
            # Create log message with test name and category
            case_name = data.get('case_name', data['case_id'])
            category = data.get('category_name', '')
            model_short = data['model'][:20]
            
            if data["status"] == "skipped":
                icon = "－"
                msg = f"[{model_short}] [{category}] {case_name}: {icon} ({data.get('reason', 'スキップ')})"
            else:
                icon = "○" if data.get("passed") else "×"
                if data["status"] == "error":
                    icon = "！"
                ttft = data.get("ttft_ms", 0) or 0
                e2e = data.get("e2e_ms", 0) or 0
                msg = f"[{model_short}] [{category}] {case_name} #{data.get('run_index', 0)}: {icon} (TTFT: {ttft:.0f}ms, E2E: {e2e:.0f}ms)"
            job["logs"].append({"type": "log", "msg": msg})

    try:
        suite_path = Path(req.suite_path).resolve()
        suite = load_suite(suite_path)
        suite = resolve_suite_asset_paths(suite, suite_path)

        selected_models = list(req.models or [])
        job["expected_total"] = expected_total_results(suite, len(selected_models), req.runs)
        job["logs"].append({"type": "info", "msg": f"対象モデル（逐次実行）: {', '.join(selected_models) if selected_models else 'なし'}"})

        # GPUメモリ節約のため、モデルは必ず1つずつロードして実行する
        for model_id in selected_models:
            if job.get("cancelled"):
                break

            if not ensure_single_loaded_model(req.base_url, model_id, job):
                raise RuntimeError(f"モデルのロードに失敗しました: {model_id}")

            model_pattern = f"^{re.escape(model_id)}$"
            run_bench_logic(
                suite=suite,
                base_url=req.base_url,
                model_pattern=model_pattern,
                runs=req.runs,
                warmup=req.warmup,
                timeout=req.timeout,
                progress_callback=callback,
                use_llm_judge=req.use_llm_judge,
                judge_model=req.judge_model,
                cancel_check=lambda: bool(job.get("cancelled"))
            )

            # 実行後はアンロードして次へ（常に最大1つロードを維持）
            job["logs"].append({"type": "info", "msg": f"アンロード: {model_id}"})
            run_lms_command_sync(["lms", "unload", model_id], timeout=60)
        
        job["expected_total"] = len(job["results"]) or job.get("expected_total", 0)
        if job.get("cancelled"):
            job["status"] = "cancelled"
            job["logs"].append({"type": "warn", "msg": "ベンチマークをキャンセルしました"})
        else:
            job["status"] = "done"
            job["logs"].append({"type": "success", "msg": "ベンチマーク完了"})
        
    except Exception as e:
        job["status"] = "failed"
        error_msg = f"エラー: {str(e)}\n{traceback.format_exc()}"
        job["logs"].append({"type": "error", "msg": error_msg})


# Mount static files AFTER API routes
app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
