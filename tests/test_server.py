from typing import Any

import pytest

import server


class FakePDBeClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str]] = []

    def fetch_entry(self, endpoint_key: str, pdb_id: str) -> dict[str, Any]:
        self.calls.append((endpoint_key, pdb_id))
        return {
            "ok": True,
            "source_url": f"https://example.test/{endpoint_key}/{pdb_id}",
            "pdb_id": pdb_id,
            "data": {"endpoint": endpoint_key},
            "error": None,
        }


def test_healthcheck_returns_service_status() -> None:
    assert server.healthcheck() == {"status": "ok", "service": "pdbe-mcp"}


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
