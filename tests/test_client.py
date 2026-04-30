import httpx
import pytest

from pdbe.client import ENDPOINTS, PDBeClient


@pytest.mark.parametrize(
    ("endpoint_key", "expected_path"),
    [
        ("summary", "/pdb/entry/summary/1cbs"),
        ("molecules", "/pdb/entry/molecules/1cbs"),
        ("ligands", "/pdb/entry/ligand_monomers/1cbs"),
        ("validation", "/validation/summary_quality_scores/entry/1cbs"),
        ("uniprot_mappings", "/mappings/uniprot/1cbs"),
    ],
)
def test_build_url_uses_documented_pdbe_v2_paths(
    endpoint_key: str,
    expected_path: str,
) -> None:
    client = PDBeClient()

    assert client.build_url(endpoint_key, " 1CBS ") == (
        f"https://www.ebi.ac.uk/pdbe/api/v2{expected_path}"
    )


def test_fetch_entry_returns_successful_pdbe_json(httpx_mock) -> None:
    client = PDBeClient()
    url = client.build_url("summary", "1cbs")
    payload = {"1cbs": [{"title": "Cellular retinoic-acid-binding protein"}]}
    httpx_mock.add_response(url=url, json=payload)

    result = client.fetch_entry("summary", "1CBS")

    assert result == {
        "ok": True,
        "source_url": url,
        "pdb_id": "1cbs",
        "data": payload,
        "error": None,
    }


def test_fetch_entry_returns_validation_error_without_network_call(httpx_mock) -> None:
    result = PDBeClient().fetch_entry("summary", "bad!")

    assert result["ok"] is False
    assert result["source_url"] is None
    assert result["pdb_id"] is None
    assert result["data"] is None
    assert result["error"]["type"] == "invalid_pdb_id"
    assert "alphanumeric" in result["error"]["message"]
    assert httpx_mock.get_requests() == []


def test_fetch_entry_returns_http_error_for_non_success_status(httpx_mock) -> None:
    client = PDBeClient()
    url = client.build_url("summary", "1cbs")
    httpx_mock.add_response(url=url, status_code=404, text="missing")

    result = client.fetch_entry("summary", "1cbs")

    assert result["ok"] is False
    assert result["source_url"] == url
    assert result["pdb_id"] == "1cbs"
    assert result["data"] is None
    assert result["error"] == {
        "type": "http_error",
        "message": "PDBe returned HTTP 404.",
        "status_code": 404,
        "body": "missing",
    }


def test_fetch_entry_returns_timeout_error(httpx_mock) -> None:
    client = PDBeClient()
    url = client.build_url("summary", "1cbs")
    httpx_mock.add_exception(httpx.TimeoutException("slow", request=httpx.Request("GET", url)))

    result = client.fetch_entry("summary", "1cbs")

    assert result["ok"] is False
    assert result["source_url"] == url
    assert result["error"]["type"] == "timeout"
    assert "timed out" in result["error"]["message"]


def test_fetch_entry_returns_invalid_json_error(httpx_mock) -> None:
    client = PDBeClient()
    url = client.build_url("summary", "1cbs")
    httpx_mock.add_response(url=url, text="not-json")

    result = client.fetch_entry("summary", "1cbs")

    assert result["ok"] is False
    assert result["source_url"] == url
    assert result["error"]["type"] == "invalid_json"
    assert "valid JSON" in result["error"]["message"]


def test_unknown_endpoint_key_is_rejected() -> None:
    assert "summary" in ENDPOINTS

    with pytest.raises(ValueError, match="Unknown PDBe endpoint"):
        PDBeClient().build_url("unknown", "1cbs")

