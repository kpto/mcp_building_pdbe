"""HTTP client for selected PDBe v2 endpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx

from pdbe.validation import normalize_pdb_id


PDBeResult = dict[str, Any]


@dataclass(frozen=True)
class PDBeEndpoint:
    """A selected PDBe v2 endpoint."""

    key: str
    path_template: str


ENDPOINTS: dict[str, PDBeEndpoint] = {
    "summary": PDBeEndpoint("summary", "/pdb/entry/summary/{pdb_id}"),
    "molecules": PDBeEndpoint("molecules", "/pdb/entry/molecules/{pdb_id}"),
    "ligands": PDBeEndpoint("ligands", "/pdb/entry/ligand_monomers/{pdb_id}"),
    "validation": PDBeEndpoint(
        "validation",
        "/validation/summary_quality_scores/entry/{pdb_id}",
    ),
    "uniprot_mappings": PDBeEndpoint(
        "uniprot_mappings",
        "/mappings/uniprot/{pdb_id}",
    ),
}


class PDBeClient:
    """Small client for selected PDBe v2 read-only endpoints."""

    def __init__(
        self,
        base_url: str = "https://www.ebi.ac.uk/pdbe/api/v2",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def build_url(self, endpoint_key: str, pdb_id: str) -> str:
        """Build a full PDBe v2 URL for an endpoint and PDB ID."""
        endpoint = self._endpoint(endpoint_key)
        normalized_pdb_id = normalize_pdb_id(pdb_id)
        return f"{self.base_url}{endpoint.path_template.format(pdb_id=normalized_pdb_id)}"

    def fetch_entry(self, endpoint_key: str, pdb_id: str) -> PDBeResult:
        """Fetch a selected PDBe endpoint for a PDB ID."""
        endpoint = self._endpoint(endpoint_key)
        try:
            normalized_pdb_id = normalize_pdb_id(pdb_id)
        except ValueError as error:
            return self._error_result(
                source_url=None,
                pdb_id=None,
                error_type="invalid_pdb_id",
                message=str(error),
            )

        source_url = (
            f"{self.base_url}"
            f"{endpoint.path_template.format(pdb_id=normalized_pdb_id)}"
        )
        try:
            with httpx.Client(timeout=self.timeout) as http_client:
                response = http_client.get(source_url)
        except httpx.TimeoutException:
            return self._error_result(
                source_url=source_url,
                pdb_id=normalized_pdb_id,
                error_type="timeout",
                message="PDBe request timed out.",
            )
        except httpx.RequestError as error:
            return self._error_result(
                source_url=source_url,
                pdb_id=normalized_pdb_id,
                error_type="request_error",
                message=f"PDBe request failed: {error}",
            )

        if not response.is_success:
            return self._error_result(
                source_url=source_url,
                pdb_id=normalized_pdb_id,
                error_type="http_error",
                message=f"PDBe returned HTTP {response.status_code}.",
                status_code=response.status_code,
                body=response.text,
            )

        try:
            data = response.json()
        except ValueError:
            return self._error_result(
                source_url=source_url,
                pdb_id=normalized_pdb_id,
                error_type="invalid_json",
                message="PDBe response was not valid JSON.",
            )

        return {
            "ok": True,
            "source_url": source_url,
            "pdb_id": normalized_pdb_id,
            "data": data,
            "error": None,
        }

    def _endpoint(self, endpoint_key: str) -> PDBeEndpoint:
        try:
            return ENDPOINTS[endpoint_key]
        except KeyError as error:
            raise ValueError(f"Unknown PDBe endpoint: {endpoint_key}") from error

    @staticmethod
    def _error_result(
        *,
        source_url: str | None,
        pdb_id: str | None,
        error_type: str,
        message: str,
        **details: Any,
    ) -> PDBeResult:
        return {
            "ok": False,
            "source_url": source_url,
            "pdb_id": pdb_id,
            "data": None,
            "error": {
                "type": error_type,
                "message": message,
                **details,
            },
        }

