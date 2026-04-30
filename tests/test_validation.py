import pytest

from pdbe.validation import normalize_pdb_id


def test_normalize_pdb_id_strips_whitespace_and_lowercases() -> None:
    assert normalize_pdb_id("  1CBS\n") == "1cbs"


@pytest.mark.parametrize("pdb_id", ["1cb", "1cbss", ""])
def test_normalize_pdb_id_rejects_values_that_are_not_four_characters(
    pdb_id: str,
) -> None:
    with pytest.raises(ValueError, match="exactly four"):
        normalize_pdb_id(pdb_id)


@pytest.mark.parametrize("pdb_id", ["1c$s", "abc_", "12 4"])
def test_normalize_pdb_id_rejects_non_alphanumeric_values(pdb_id: str) -> None:
    with pytest.raises(ValueError, match="alphanumeric"):
        normalize_pdb_id(pdb_id)


def test_normalize_pdb_id_rejects_non_string_values() -> None:
    with pytest.raises(ValueError, match="string"):
        normalize_pdb_id(None)  # type: ignore[arg-type]

