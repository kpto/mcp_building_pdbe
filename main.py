import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("PDBe MCP Server")

BASE_URL = "https://www.ebi.ac.uk/pdbe/api/pdb/entry"


def normalize_pdb_id(pdb_id: str) -> str:
    pdb_id = pdb_id.strip().lower()
    if len(pdb_id) != 4 or not pdb_id.isalnum():
        raise ValueError("pdb_id must be a 4-character alphanumeric id (e.g. 1cbs)")
    return pdb_id


@mcp.tool()
def healthcheck() -> dict:
    """Simple connectivity check."""
    return {"status": "ok", "service": "pdbe-mcp"}


@mcp.tool()
def get_summary(pdb_id: str) -> dict:
    """
    Get basic summary for a PDB entry (title, organism, method, resolution).
    """
    pdb_id = normalize_pdb_id(pdb_id)
    url = f"{BASE_URL}/summary/{pdb_id}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json().get(pdb_id, [])

    if not data:
        return {"error": "No data found"}

    entry = data[0]

    return {
        "pdb_id": pdb_id,
        "title": entry.get("title"),
        "experimental_method": entry.get("experimental_method"),
        "resolution": entry.get("resolution"),
        "organism": entry.get("organism_scientific_name"),
    }


@mcp.tool()
def get_ligands(pdb_id: str) -> list:
    """
    Get ligands (small molecules) present in a PDB structure.
    """
    pdb_id = normalize_pdb_id(pdb_id)
    url = f"{BASE_URL}/ligand_monomers/{pdb_id}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json().get(pdb_id, [])

    ligands = []
    for lig in data:
        ligands.append({
            "chem_comp_id": lig.get("chem_comp_id"),
            "name": lig.get("chem_comp_name"),
            "formula": lig.get("chem_comp_formula"),
        })

    return ligands


@mcp.tool()
def get_publications(pdb_id: str) -> list:
    """
    Get primary publications associated with a PDB entry.
    """
    pdb_id = normalize_pdb_id(pdb_id)
    url = f"{BASE_URL}/publications/{pdb_id}"
    r = requests.get(url)
    r.raise_for_status()
    data = r.json().get(pdb_id, [])

    pubs = []
    for pub in data:
        pubs.append({
            "title": pub.get("title"),
            "journal": pub.get("journal_info", {}).get("journal"),
            "year": pub.get("year"),
            "doi": pub.get("doi"),
        })

    return pubs


def main() -> None:
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    #transport = os.getenv("MCP_TRANSPORT", "http")

    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    else:
        mcp.run()


if __name__ == "__main__":
    main()