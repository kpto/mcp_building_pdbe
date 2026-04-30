"""Validation helpers for PDBe identifiers."""

from __future__ import annotations


def normalize_pdb_id(pdb_id: str) -> str:
    """Return a normalized four-character PDB ID."""
    if not isinstance(pdb_id, str):
        raise ValueError("PDB ID must be a string.")

    normalized = pdb_id.strip().lower()
    if len(normalized) != 4:
        raise ValueError("PDB ID must be exactly four characters.")
    if not normalized.isalnum():
        raise ValueError("PDB ID must contain only alphanumeric characters.")

    return normalized

