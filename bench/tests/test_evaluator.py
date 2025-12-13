import pytest


from bench.main import evaluate_result


def test_exact_match_with_alternatives():
    passed, details = evaluate_result("A", {"type": "exact_match", "expected": "A", "alternatives": ["B"]})
    assert passed is True
    assert details["matched"] == "A"


def test_contains_all_basic_casefold_nfkc():
    passed, _ = evaluate_result("Ｈｅｌｌｏ", {"type": "contains_all", "keywords": ["hello"]})
    assert passed is True


def test_contains_all_loose_ignores_punct_and_spaces():
    passed, _ = evaluate_result("答えは、東京 です。", {"type": "contains_all", "keywords": ["東京です"], "normalize": "loose"})
    assert passed is True


def test_contains_any_keyword_sets():
    rule = {"type": "contains_any", "keyword_sets": [["a", "b"], ["x", "y"]]}
    passed, details = evaluate_result("A ... B", rule)
    assert passed is True
    assert details["matched"] == ["a", "b"]


def test_json_parse_from_code_block_and_must_have_keys():
    text = """以下です:
```json
{ "foo": 1, "bar": { "baz": 2 } }
```"""
    passed, details = evaluate_result(text, {"type": "json_parse", "must_have_keys": ["foo", "bar"]})
    assert passed is True
    assert "foo" in details["matched"]


def test_json_parse_array_ok_when_no_must_have():
    text = "```json\n[1,2,3]\n```"
    passed, details = evaluate_result(text, {"type": "json_parse"})
    assert passed is True
    assert "list" in str(details["matched"])


def test_numeric_first_number_commas_and_relative_tolerance():
    passed, details = evaluate_result("合計 1,001.0 円", {"type": "numeric", "expected": 1000, "relative_tolerance": 0.002})
    assert passed is True, details


def test_numeric_expected_range():
    passed, _ = evaluate_result("0.33", {"type": "numeric", "expected_range": [0.3, 0.4]})
    assert passed is True


def test_numeric_extract_regex():
    passed, _ = evaluate_result("TTFT=123ms E2E=999ms", {"type": "numeric", "expected": 123, "extract_regex": r"TTFT=\d+"})
    assert passed is True


def test_fuzzy_match_loose():
    passed, _ = evaluate_result("東京都", {"type": "fuzzy_match", "expected": "東京 都", "normalize": "loose", "threshold": 0.9})
    assert passed is True


def test_regex_fullmatch():
    passed, _ = evaluate_result("ABC12", {"type": "regex_fullmatch", "pattern": "[A-Z]{3}\\d{2}"})
    assert passed is True
