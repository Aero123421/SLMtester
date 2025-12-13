from pathlib import Path

import pytest

from bench.main import load_suite, resolve_suite_asset_paths, expected_total_results


def test_load_suite_detects_duplicate_case_ids(tmp_path: Path):
    suite_path = tmp_path / "suite.yaml"
    suite_path.write_text(
        """cases:
  - id: dup
    request:
      messages:
        - role: user
          content: hi
    eval:
      type: contains_all
      keywords: [hi]
  - id: dup
    request:
      messages:
        - role: user
          content: hi2
    eval:
      type: contains_all
      keywords: [hi2]
""",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_suite(suite_path)


def test_resolve_suite_asset_paths_handles_legacy_and_variants(tmp_path: Path):
    img = tmp_path / "images" / "x.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    img.write_bytes(b"fakepng")

    suite_path = tmp_path / "suite.yaml"
    suite = {
        "cases": [
            {
                "id": "legacy",
                "request": {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "image_url", "image_path": "images/x.png"}],
                        }
                    ]
                },
            },
            {
                "id": "variants",
                "variants": [{"prompt": "p", "image_path": "images/x.png", "evaluation": {"type": "contains_all", "keywords": ["x"]}}],
            },
        ]
    }
    resolved = resolve_suite_asset_paths(suite, suite_path)
    p1 = resolved["cases"][0]["request"]["messages"][0]["content"][0]["image_path"]
    p2 = resolved["cases"][1]["variants"][0]["image_path"]
    assert Path(p1).is_absolute()
    assert Path(p2).is_absolute()


def test_expected_total_results_counts_variant_as_one():
    suite = {
        "cases": [
            {"id": "v", "variants": [{"prompt": "x", "evaluation": {"type": "contains_all", "keywords": ["x"]}}]},
            {"id": "l", "request": {"messages": [{"role": "user", "content": "hi"}]}, "eval": {"type": "contains_all", "keywords": ["hi"]}},
        ]
    }
    assert expected_total_results(suite, models_count=2, runs=3) == (1 + 3) * 2


def test_suite_auto_loads_and_is_auto_evaluable():
    suite = load_suite(Path("bench/suite_auto.yaml"))
    cases = suite.get("cases") or []
    assert len(cases) >= 50

    variants = 0
    eval_types = set()
    for c in cases:
        if "variants" in c:
            for v in c.get("variants") or []:
                variants += 1
                eval_types.add((v.get("evaluation") or {}).get("type"))
        else:
            variants += 1
            eval_types.add((c.get("eval") or {}).get("type"))

    assert variants >= 1000
    assert "semantic_match" not in eval_types
