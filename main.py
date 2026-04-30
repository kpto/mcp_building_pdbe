import os
import time
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

mcp = FastMCP("PDBe MCP Server")

BASE_URL = "https://www.ebi.ac.uk/pdbe/api/pdb/entry"
_LAST_LLM_CALL_TS = 0.0


def normalize_pdb_id(pdb_id: str) -> str:
    pdb_id = pdb_id.strip().lower()
    if len(pdb_id) != 4 or not pdb_id.isalnum():
        raise ValueError("pdb_id must be a 4-character alphanumeric id (e.g. 1cbs)")
    return pdb_id


def call_llm(prompt: str, system_prompt: str | None = None, temperature: float = 0.2, max_tokens: int = 500) -> dict:
    """
    Call an OpenAI-compatible chat completion endpoint.

    Required env var:
      - LLM_API_KEY

    Optional env vars:
      - LLM_BASE_URL (default: https://api.openai.com/v1)
      - LLM_MODEL (default: gpt-4o-mini)
    """
    api_key = os.getenv("LLM_API_KEY")
    if not api_key:
        raise ValueError("LLM_API_KEY is not set")

    base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    url = f"{base_url}/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    global _LAST_LLM_CALL_TS
    min_interval_seconds = 2.0
    now = time.time()
    elapsed = now - _LAST_LLM_CALL_TS
    if elapsed < min_interval_seconds:
        time.sleep(min_interval_seconds - elapsed)

    max_retries = 3
    backoff_seconds = 2

    for attempt in range(1, max_retries + 1):
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        if response.status_code != 429:
            response.raise_for_status()
            data = response.json()
            break

        retry_after = response.headers.get("Retry-After")
        wait_seconds = int(retry_after) if retry_after and retry_after.isdigit() else backoff_seconds * attempt
        if attempt == max_retries:
            raise ValueError(
                "LLM provider returned 429 Too Many Requests. "
                "Check API billing/quota and rate limits, then retry later."
            )
        time.sleep(wait_seconds)
    _LAST_LLM_CALL_TS = time.time()

    content = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    return {
        "model": data.get("model", model),
        "response": content,
        "usage": data.get("usage", {}),
    }


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


@mcp.tool()
def ask_llm(
    prompt: str,
    system_prompt: str = "You are a helpful assistant for protein structure analysis.",
    temperature: float = 0.2,
    max_tokens: int = 500,
) -> dict:
    """
    Ask an LLM through an OpenAI-compatible API.

    Example use:
      ask_llm("Explain what ligand binding site means in simple words")
    """
    if not prompt.strip():
        raise ValueError("prompt must not be empty")

    return call_llm(
        prompt=prompt.strip(),
        system_prompt=system_prompt.strip() if system_prompt else None,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def main() -> None:
    load_dotenv()
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    #transport = os.getenv("MCP_TRANSPORT", "http")

    if transport == "http":
        mcp.run(transport="http", host="0.0.0.0", port=8080)
    else:
        mcp.run()


if __name__ == "__main__":
    main()