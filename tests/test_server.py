from typing import Any

import pytest

import server


class FakePDBeClient:
    def __init__(self, responses: dict[str, dict[str, Any]] | None = None) -> None:
        self.calls: list[tuple[str, str]] = []
        self.responses = responses or {}

    def fetch_entry(self, endpoint_key: str, pdb_id: str) -> dict[str, Any]:
        self.calls.append((endpoint_key, pdb_id))
        if pdb_id in self.responses:
            return self.responses[pdb_id]

        return {
            "ok": True,
            "source_url": f"https://example.test/{endpoint_key}/{pdb_id}",
            "pdb_id": pdb_id,
            "data": {"endpoint": endpoint_key},
            "error": None,
        }


def test_healthcheck_returns_service_status() -> None:
    assert server.healthcheck() == {"status": "ok", "service": "pdbe-mcp"}


def test_get_entry_summaries_batches_summary_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakePDBeClient()
    monkeypatch.setattr(server, "pdbe_client", fake_client)

    result = server.get_entry_summaries(["1CBS", "2HHB"])

    assert fake_client.calls == [("summary", "1CBS"), ("summary", "2HHB")]
    assert result == {
        "ok": True,
        "endpoint": "summary",
        "results": {
            "1CBS": {
                "ok": True,
                "source_url": "https://example.test/summary/1CBS",
                "pdb_id": "1CBS",
                "data": {"endpoint": "summary"},
                "error": None,
            },
            "2HHB": {
                "ok": True,
                "source_url": "https://example.test/summary/2HHB",
                "pdb_id": "2HHB",
                "data": {"endpoint": "summary"},
                "error": None,
            },
        },
        "error": None,
    }


def test_get_entry_summaries_preserves_per_entry_failures(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invalid_result = {
        "ok": False,
        "source_url": None,
        "pdb_id": None,
        "data": None,
        "error": {
            "type": "invalid_pdb_id",
            "message": "PDB ID must contain only alphanumeric characters.",
        },
    }
    fake_client = FakePDBeClient(responses={"bad!": invalid_result})
    monkeypatch.setattr(server, "pdbe_client", fake_client)

    result = server.get_entry_summaries(["1CBS", "bad!"])

    assert fake_client.calls == [("summary", "1CBS"), ("summary", "bad!")]
    assert result["ok"] is True
    assert result["endpoint"] == "summary"
    assert result["results"]["bad!"] == invalid_result
    assert result["error"] is None


def test_get_entry_summaries_rejects_empty_batches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = FakePDBeClient()
    monkeypatch.setattr(server, "pdbe_client", fake_client)

    result = server.get_entry_summaries([])

    assert fake_client.calls == []
    assert result == {
        "ok": False,
        "endpoint": "summary",
        "results": {},
        "error": {
            "type": "empty_pdb_ids",
            "message": "pdb_ids must contain at least one PDB ID.",
        },
    }


@pytest.mark.parametrize(
    ("tool_name", "endpoint_key"),
    [
        ("get_entry_summary", "summary"),
        ("get_entry_molecules", "molecules"),
        ("get_entry_ligands", "ligands"),
        ("get_entry_validation", "validation"),
        ("get_uniprot_mappings", "uniprot_mappings"),
    ],
)
def test_tool_functions_delegate_to_expected_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    tool_name: str,
    endpoint_key: str,
) -> None:
    fake_client = FakePDBeClient()
    monkeypatch.setattr(server, "pdbe_client", fake_client)

    result = getattr(server, tool_name)("1CBS")

    assert fake_client.calls == [(endpoint_key, "1CBS")]
    assert result == {
        "ok": True,
        "source_url": f"https://example.test/{endpoint_key}/1CBS",
        "pdb_id": "1CBS",
        "data": {"endpoint": endpoint_key},
        "error": None,
    }


def test_main_runs_fastmcp_server(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def fake_run() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(server.mcp, "run", fake_run)

    server.main()

    assert called is True
