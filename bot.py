import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord

TOKEN = os.getenv("DISCORD_TOKEN")
inventory = {}

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, *args):
        pass

def web_server():
    port = int(os.getenv("PORT", "10000"))
    HTTPServer(("0.0.0.0", port), Health).serve_forever()

threading.Thread(target=web_server, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
bot = discord.Client(intents=intents)

def change(item, amount):
    item = item.lower().strip()
    inventory[item] = max(0, inventory.get(item, 0) + amount)

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")
    ch = discord.utils.find(
        lambda x: isinstance(x, discord.TextChannel)
        and x.name.lower() == "inventory",
        bot.get_all_channels()
    )
    if ch:
        async for m in ch.history(limit=None, oldest_first=True):
            if m.author.bot:
                continue
            x = re.match(r"^([+-])(.+?)\s+(\d+)$", m.content.strip())
            if x:
                change(x.group(2), int(x.group(3)) * (1 if x.group(1) == "+" else -1))
        print("Inventory restored:", inventory)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if not isinstance(message.channel, discord.TextChannel):
        return
    if message.channel.name.lower() != "inventory":
        return

    text = message.content.strip()

    x = re.match(r"^([+-])(.+?)\s+(\d+)$", text)
    if x:
        item = x.group(2).strip()
        amount = int(x.group(3))
        change(item, amount * (1 if x.group(1) == "+" else -1))
        stock = inventory[item.lower()]
        await message.channel.send(
            f"✅ **{item.title()}** → {stock}\n"
            + ("❌ HABIS!" if stock == 0 else "⚠️ Tinggal 1!" if stock == 1 else "")
        )
        return

    if text.lower() == "!stok":
        if not inventory:
            await message.channel.send("📦 Inventory kosong.")
            return
        lines = ["🏠 **HOME INVENTORY**", ""]
        for item, stock in sorted(inventory.items()):
            icon = "❌" if stock == 0 else "⚠️" if stock == 1 else "📦"
            lines.append(f"{icon} **{item.title()}** — {stock}")
        await message.channel.send("\n".join(lines))
        return

    if text.lower().startswith("!stok "):
        item = text[6:].strip().lower()
        stock = inventory.get(item)
        if stock is None:
            await message.channel.send(f"❌ **{item.title()}** belum ada.")
        else:
            await message.channel.send(f"📦 **{item.title()}** — {stock}")

bot.run(TOKEN)
