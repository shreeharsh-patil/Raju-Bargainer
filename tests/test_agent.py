import pytest
from app.agent import check_inventory, INVENTORY, root_agent

def test_check_inventory_brass_lamp():
    result = check_inventory("Brass Lamp")
    assert "Brass Lamp" in result
    assert "in stock" in result
    assert "50" in result

def test_check_inventory_taj_mahal():
    result = check_inventory("Taj Mahal")
    assert "Taj Mahal" in result
    assert "OUT OF STOCK" in result

def test_check_inventory_unknown_item():
    result = check_inventory("Cyberpunk Car")
    assert "not found" in result

def test_agent_definition():
    assert root_agent.name == "raju_agent"
    assert len(root_agent.tools) == 1
    assert root_agent.tools[0].__name__ == "check_inventory"
