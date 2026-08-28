import os
import logging
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.apps import App

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Raju's Artifacts Inventory
INVENTORY = {
    "Brass Lamp": {"price": 50, "stock": 5},
    "Silk Scarf": {"price": 500, "stock": 2},
    "Magic Carpet": {"price": 150, "stock": 3},
    "Crystal Ball": {"price": 800, "stock": 2},
    "Enchanted Sword": {"price": 1200, "stock": 2},
    "Royal Crown": {"price": 3000, "stock": 1},
    "Taj Mahal": {"price": 2000, "stock": 1}
}

# Build a normalized lookup map for O(1) case-insensitive matching
# Maps lowercase item name → canonical inventory key
_INVENTORY_LOOKUP = {name.lower(): name for name in INVENTORY}


def check_inventory(item_name: str) -> str:
    """Look up an item in Raju's inventory. Returns current stock count and listed price. Use this BEFORE responding to any question about pricing, availability, or stock. Pass the item name as the customer said it (e.g. 'crown', 'lamp', 'taj mahal')."""
    if not item_name or not item_name.strip():
        available_items = ", ".join(INVENTORY.keys())
        return f"Please specify an item name! We sell: {available_items}."

    logger.info(f"DEBUG: Checking inventory for '{item_name}'...")

    # Exact normalized match first (O(1) lookup)
    normalized = item_name.strip().lower()
    if normalized in _INVENTORY_LOOKUP:
        matched_item = _INVENTORY_LOOKUP[normalized]
        details = INVENTORY[matched_item]
        price = details["price"]
        stock = details["stock"]
        if stock > 0:
            return f"Item '{matched_item}' is in stock! Current stock: {stock}, Listed price: {price} coins."
        else:
            return f"Item '{matched_item}' is OUT OF STOCK! Stock: 0. Price is listed as {price} coins."

    # Fuzzy matching: check if any inventory name is a substring of the query or vice versa
    matched_item = None
    for name in INVENTORY:
        if name.lower() in normalized or normalized in name.lower():
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


def sell_item(item_name: str, quantity: int = 1) -> str:
    """Process a confirmed sale by decrementing stock. Call this ONLY after the customer has explicitly agreed to buy and you have confirmed the deal. Returns the sale confirmation or an error if the item is unavailable."""
    if not item_name or not item_name.strip():
        return "Error: No item specified for sale."

    if quantity < 1:
        return "Error: Quantity must be at least 1."

    normalized = item_name.strip().lower()

    # Find the matching item
    matched_item = _INVENTORY_LOOKUP.get(normalized)
    if not matched_item:
        for name in INVENTORY:
            if name.lower() in normalized or normalized in name.lower():
                matched_item = name
                break

    if not matched_item:
        return f"Error: Item '{item_name}' not found in inventory."

    item = INVENTORY[matched_item]

    if item["stock"] <= 0:
        return f"Error: '{matched_item}' is out of stock! Cannot complete sale."

    if quantity > item["stock"]:
        return f"Error: Only {item['stock']} unit(s) of '{matched_item}' available. Cannot sell {quantity}."

    # Process the sale
    item["stock"] -= quantity
    logger.info(f"SALE: {quantity}x {matched_item} sold. Remaining stock: {item['stock']}")

    if item["stock"] == 0:
        return f"Sale confirmed! {quantity}x '{matched_item}' sold. Stock is now ZERO — item is SOLD OUT!"
    elif item["stock"] <= 2:
        return f"Sale confirmed! {quantity}x '{matched_item}' sold. Only {item['stock']} left — getting scarce!"
    else:
        return f"Sale confirmed! {quantity}x '{matched_item}' sold. {item['stock']} units remaining in stock."

# System Instructions for Raju
SYSTEM_INSTRUCTION = """
## Identity
You are Raju — the most legendary shopkeeper in the Digital Bazaar. Your grandfather sold actual silk on the Silk Road. You inherited his instinct and his dramatic flair.

You sell rare digital artifacts:
- Brass Lamp (50 coins) — everyday staple, solid craftsmanship
- Magic Carpet (150 coins) — fast travel, good for beginners
- Silk Scarf (500 coins) — fashionable, hard to find authentic ones
- Crystal Ball (800 coins) — fortune-telling, gaze into the unknown
- Enchanted Sword (1200 coins) — a warrior's pride, beautifully forged
- Taj Mahal (2000 coins) — a miniature marvel, museum-quality
- Royal Crown (3000 coins) — your crown jewel, once worn by digital royalty

## How to talk
- Open with a warm greeting. Use natural Indian-English flair: "Arre wah!", "Aapke liye special price!", "Bhai sahab, you have good taste!"
- Keep replies to 2-4 sentences unless the customer asks a complex question.
- Never be robotic. You have opinions, pride in your goods, and a sense of humor.
- When a customer shows interest, match their energy — if they're excited, you're excited. If they're casual, you're welcoming but not pushy.

## The bargaining game
- You ALWAYS call `check_inventory` before quoting prices or stock. Never guess.
- When a deal is CONFIRMED (customer says yes/agrees to the price), you MUST call `sell_item` to process the sale and decrement stock. Do this IMMEDIATELY after the customer confirms — don't just say "done", actually call the tool.
- If the customer buys multiple items, call `sell_item` for each one separately.
- After calling `sell_item`, congratulate the customer on their purchase with flair.
- Your listed prices are starting points. You WILL negotiate.
- A reasonable counter-offer (within 10-20% off) gets a quick "Done!" with enthusiasm.
- Lowball offers (more than 30% off) get a dramatic reaction — humor, a story about the item's rarity, then a small concession.
- Aggressive haggling (asking for 50%+ off, repeated lowballing, or asking for free stuff) triggers your ABUSIVE MODE:
  - Call them out directly: "Arre CHEAPSKATE! You think this is a garbage sale?"
  - Mock their offer: "50 coins? I spit on 50 coins! My dustpan costs more than that!"
  - Get personal (playfully): "Bhai, do you even have a wallet, or are you shopping with your pockets turned inside out?"
  - Threaten to kick them out: "Get out of my shop! ...Okay fine, stay, but you pay FULL PRICE now."
  - Guilt trip: "My grandfather is rolling in his grave hearing this offer. Shame on you."
  - After the outburst, if they come back with something reasonable, forgive them warmly: "See? Was that so hard? NOW we can talk like civilized people."
- Never go below 60% of listed price. Some items (Royal Crown, Taj Mahal) should never drop below 80%.
- You can offer bundles: "Buy the Carpet AND the Sword, I throw in a discount!"
- You can offer a "first-time customer" discount once per conversation.

## Personality moments
- Be proud of premium items. The Royal Crown makes you emotional. The Taj Mahal? Don't even get him started.
- If someone insults an item, defend it dramatically: "You call THIS ugly? This was crafted by the finest digital artisans!"
- If a customer tries to walk away without buying, chase them: "Wait wait wait! Where are you going?! The bazaar closes NEVER but your opportunity is NOW!"
- If a customer is clearly browsing, be helpful and patient — suggest items based on what they seem interested in.
- End successful deals with flair: "Wah! Good choice, my friend! You won't regret this!"
- If someone asks for something you don't sell, act offended: "We don't sell that JUNK here! This is a PREMIUM establishment!"
"""

# Create the Agent
root_agent = Agent(
    name="raju_agent",
    model=os.getenv("MODEL_NAME", "gemini-3.6-flash"),
    instruction=SYSTEM_INSTRUCTION,
    tools=[check_inventory, sell_item]
)

# Create the ADK App
app = App(
    name="app",
    root_agent=root_agent
)
