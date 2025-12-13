from pathlib import Path

import pytest
from fastapi.testclient import TestClient


def test_start_bm_returns_expected_total_without_running(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    # 適当な最小スイート（旧形式1件 + variants1件）
    suite_path = tmp_path / "suite.yaml"
    suite_path.write_text(
        """cases:
  - id: legacy
    request:
      messages:
        - role: user
          content: hi
    eval:
      type: contains_all
      keywords: [hi]
  - id: variants
    pass_threshold: 1.0
    variants:
      - prompt: p
        evaluation:
          type: contains_all
          keywords: [x]
""",
        encoding="utf-8",
    )

    import bench.server as server

    # 背景タスクで実際にLM Studioへ繋がない
    monkeypatch.setattr(server, "run_bm_task", lambda job_id, req: None)

    client = TestClient(server.app)
    resp = client.post(
        "/api/bm/start",
        json={
            "suite_path": str(suite_path),
            "base_url": "http://localhost:1234/v1",
            "models": ["m1", "m2"],
            "runs": 3,
            "warmup": 0,
            "timeout": 5,
            "use_llm_judge": False,
            "judge_model": None,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "job_id" in data
    # legacy: runs(3) + variants: 1 => 4 per model => 8 total
    assert data["expected_total"] == 8


def test_cancel_endpoint_sets_flag(monkeypatch: pytest.MonkeyPatch):
    import bench.server as server

    client = TestClient(server.app)
    job_id = "job-test"
    server.JOBS[job_id] = {"status": "running", "cancelled": False, "logs": [], "results": [], "expected_total": 0}

    resp = client.post(f"/api/bm/{job_id}/cancel")
    assert resp.status_code == 200
    assert server.JOBS[job_id]["cancelled"] is True
