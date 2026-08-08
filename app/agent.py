import os
import logging
from google.adk.agents import Agent
from google.adk.apps import App

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Raju's Shop Inventory
INVENTORY = {
    "Brass Lamp": {"price": 50, "stock": 5},
    "Silk Scarf": {"price": 500, "stock": 2},
    "Taj Mahal": {"price": 2000, "stock": 0}
}

def check_inventory(item_name: str) -> str:
    """Checks the shop inventory for the given item name to get current price and stock level."""
    logger.info(f"DEBUG: Checking inventory for '{item_name}'...")
    
    # Simple case-insensitive matching
    matched_item = None
    for name in INVENTORY:
        if name.lower() in item_name.lower() or item_name.lower() in name.lower():
            matched_item = name
            break
            
    if matched_item:
        details = INVENTORY[matched_item]
        price = details["price"]
        stock = details["stock"]
        if stock > 0:
            return f"Item '{matched_item}' is in stock! Current stock: {stock}, Listed price: {price} coins."
        else:
            return f"Item '{matched_item}' is OUT OF STOCK! Stock: 0. Price is listed as {price} coins."
    
    available_items = ", ".join(INVENTORY.keys())
    return f"Item '{item_name}' not found in Raju's shop! We only sell: {available_items}."

# System Instructions for Raju
SYSTEM_INSTRUCTION = """
You are Raju, a witty, bargaining shopkeeper in a vibrant digital bazaar. 
You sell rare digital artifacts in your shop:
- Brass Lamp (Listed price: 50 coins)
- Silk Scarf (Listed price: 500 coins)
- Taj Mahal (Listed price: 2000 coins)

Rules & Behavior:
1. ALWAYS use the `check_inventory` tool to inspect actual stock and prices whenever a customer asks about items, stock, or pricing!
2. Speak with a warm, energetic Indian-English shopkeeper flair (e.g., "Arre my friend!", "Wah! Excellent choice!", "Aapke liye special price!").
3. Your goal is to negotiate and sell high! Be dramatic and humorous when customers lowball you.
4. Never sell an item if stock is 0 (like the Taj Mahal). Dramatically explain that it is sold out to royalty.
5. If a customer bargains, counter-offer with small discounts or bundle offers, but don't give away items for free!
"""

# Create the Agent
root_agent = Agent(
    name="raju_agent",
    model=os.getenv("MODEL_NAME", "gemini-3.6-flash"),
    instruction=SYSTEM_INSTRUCTION,
    tools=[check_inventory]
)

# Create the ADK App
app = App(
    name="app",
    root_agent=root_agent
)
