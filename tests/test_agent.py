import pytest
from app.agent import check_inventory, INVENTORY, root_agent, _INVENTORY_LOOKUP


# ── Exact match tests ──────────────────────────────────────────

def test_check_inventory_brass_lamp():
    result = check_inventory("Brass Lamp")
    assert "Brass Lamp" in result
    assert "in stock" in result
    assert "50" in result


def test_check_inventory_taj_mahal():
    result = check_inventory("Taj Mahal")
    assert "Taj Mahal" in result
    assert "in stock" in result


def test_check_inventory_magic_carpet():
    result = check_inventory("Magic Carpet")
    assert "Magic Carpet" in result
    assert "in stock" in result
    assert "150" in result


def test_check_inventory_crystal_ball():
    result = check_inventory("Crystal Ball")
    assert "Crystal Ball" in result
    assert "in stock" in result
    assert "800" in result


def test_check_inventory_enchanted_sword():
    result = check_inventory("Enchanted Sword")
    assert "Enchanted Sword" in result
    assert "in stock" in result
    assert "1200" in result


def test_check_inventory_royal_crown():
    result = check_inventory("Royal Crown")
    assert "Royal Crown" in result
    assert "in stock" in result
    assert "3000" in result


# ── Case-insensitive matching ──────────────────────────────────

def test_check_inventory_case_insensitive():
    result = check_inventory("brass lamp")
    assert "Brass Lamp" in result
    assert "in stock" in result


def test_check_inventory_case_mixed():
    result = check_inventory("ROYAL crown")
    assert "Royal Crown" in result
    assert "in stock" in result


# ── Fuzzy / substring matching ─────────────────────────────────

def test_check_inventory_partial_match_lamp():
    result = check_inventory("lamp")
    assert "Brass Lamp" in result
    assert "in stock" in result


def test_check_inventory_partial_match_crown():
    result = check_inventory("crown")
    assert "Royal Crown" in result
    assert "in stock" in result


def test_check_inventory_partial_match_taj():
    result = check_inventory("taj")
    assert "Taj Mahal" in result


def test_check_inventory_partial_match_sword():
    result = check_inventory("sword")
    assert "Enchanted Sword" in result


# ── Unknown / invalid items ────────────────────────────────────

def test_check_inventory_unknown_item():
    result = check_inventory("Cyberpunk Car")
    assert "not found" in result


def test_check_inventory_empty_string():
    result = check_inventory("")
    assert "specify" in result.lower() or "sell" in result.lower()


def test_check_inventory_whitespace_only():
    result = check_inventory("   ")
    assert "specify" in result.lower() or "sell" in result.lower()


def test_check_inventory_completely_unrelated():
    result = check_inventory("pineapple pizza")
    assert "not found" in result


# ── Inventory lookup cache ─────────────────────────────────────

def test_inventory_lookup_cache_keys():
    """All inventory items should be in the normalized lookup."""
    for name in INVENTORY:
        assert name.lower() in _INVENTORY_LOOKUP
        assert _INVENTORY_LOOKUP[name.lower()] == name


def test_inventory_lookup_cache_count():
    """Lookup cache should have exactly as many entries as INVENTORY."""
    assert len(_INVENTORY_LOOKUP) == len(INVENTORY)


# ── Agent definition ───────────────────────────────────────────

def test_agent_definition():
    assert root_agent.name == "raju_agent"
    assert len(root_agent.tools) == 2
    tool_names = {t.__name__ for t in root_agent.tools}
    assert "check_inventory" in tool_names
    assert "sell_item" in tool_names


def test_agent_has_instruction():
    """Agent should have a non-empty system instruction."""
    assert root_agent.instruction is not None
    assert len(root_agent.instruction) > 100


def test_inventory_completeness():
    """All items listed in the system instruction should exist in INVENTORY."""
    expected_items = ["Brass Lamp", "Silk Scarf", "Magic Carpet", "Crystal Ball", "Enchanted Sword", "Royal Crown", "Taj Mahal"]
    for item in expected_items:
        assert item in INVENTORY, f"{item} missing from INVENTORY"
