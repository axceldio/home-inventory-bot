import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import discord

TOKEN = os.getenv("DISCORD_TOKEN")
inventory = {}


# =========================
# RENDER WEB SERVER
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Home Inventory Bot is online!")

    def log_message(self, *args):
        pass


def start_web_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


threading.Thread(
    target=start_web_server,
    daemon=True
).start()


# =========================
# DISCORD
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = discord.Client(intents=intents)


# =========================
# INVENTORY
# =========================

def change_stock(item, amount):
    item = item.lower().strip()

    if item not in inventory:
        inventory[item] = 0

    inventory[item] += amount

    if inventory[item] < 0:
        inventory[item] = 0


def delete_item(item):
    item = item.lower().strip()

    if item in inventory:
        del inventory[item]


# =========================
# RESTORE DARI HISTORY
# =========================

async def restore_inventory(channel):

    inventory.clear()

    async for message in channel.history(
        limit=None,
        oldest_first=True
    ):

        if message.author.bot:
            continue

        text = message.content.strip()

        # +barang jumlah
        add = re.match(
            r"^\+(.+?)\s+(\d+)$",
            text
        )

        # -barang jumlah
        remove = re.match(
            r"^-(.+?)\s+(\d+)$",
            text
        )

        # !hapus barang
        delete = re.match(
            r"^!hapus\s+(.+)$",
            text,
            re.IGNORECASE
        )

        if add:
            item = add.group(1)
            amount = int(add.group(2))
            change_stock(item, amount)

        elif remove:
            item = remove.group(1)
            amount = int(remove.group(2))
            change_stock(item, -amount)

        elif delete:
            item = delete.group(1)
            delete_item(item)

    print("Inventory restored:", inventory)


# =========================
# BOT ONLINE
# =========================

@bot.event
async def on_ready():

    print(f"Bot online: {bot.user}")

    channel = discord.utils.find(
        lambda x:
        isinstance(x, discord.TextChannel)
        and x.name.lower() == "inventory",
        bot.get_all_channels()
    )

    if channel:
        await restore_inventory(channel)


# =========================
# SEMUA COMMAND
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if not isinstance(message.channel, discord.TextChannel):
        return

    if message.channel.name.lower() != "inventory":
        return

    text = message.content.strip()


    # =========================
    # TAMBAH / KURANGI
    # =========================

    change = re.match(
        r"^([+-])(.+?)\s+(\d+)$",
        text
    )

    if change:

        symbol = change.group(1)
        item = change.group(2).strip()
        amount = int(change.group(3))

        if symbol == "+":
            change_stock(item, amount)

            stock = inventory[item.lower()]

            await message.channel.send(
                f"✅ **{item.title()}** +{amount}\n"
                f"📦 Stok sekarang: **{stock}**"
            )

        else:
            change_stock(item, -amount)

            stock = inventory[item.lower()]

            if stock == 0:
                status = "❌ HABIS!"
            elif stock == 1:
                status = "⚠️ Tinggal 1!"
            else:
                status = ""

            await message.channel.send(
                f"✅ **{item.title()}** -{amount}\n"
                f"📦 Stok sekarang: **{stock}**\n"
                f"{status}"
            )

        return


    # =========================
    # HAPUS BARANG
    # =========================

    delete = re.match(
        r"^!hapus\s+(.+)$",
        text,
        re.IGNORECASE
    )

    if delete:

        item = delete.group(1).strip().lower()

        if item in inventory:

            del inventory[item]

            await message.channel.send(
                f"🗑️ **{item.title()}** sudah dihapus."
            )

        else:

            await message.channel.send(
                f"❌ **{item.title()}** tidak ditemukan."
            )

        return


    # =========================
    # SEMUA STOK
    # =========================

    if text.lower() == "!stok":

        if not inventory:

            await message.channel.send(
                "📦 Inventory masih kosong."
            )
            return

        lines = [
            "🏠 **HOME INVENTORY**",
            ""
        ]

        for item, stock in sorted(inventory.items()):

            if stock == 0:
                icon = "❌"
            elif stock == 1:
                icon = "⚠️"
            else:
                icon = "📦"

            lines.append(
                f"{icon} **{item.title()}** — {stock}"
            )

        await message.channel.send(
            "\n".join(lines)
        )

        return


    # =========================
    # STOK BARANG TERTENTU
    # =========================

    if text.lower().startswith("!stok "):

        item = text[6:].strip().lower()

        if item in inventory:

            stock = inventory[item]

            if stock == 0:
                icon = "❌"
            elif stock == 1:
                icon = "⚠️"
            else:
                icon = "📦"

            await message.channel.send(
                f"{icon} **{item.title()}** — {stock}"
            )

        else:

            await message.channel.send(
                f"❌ **{item.title()}** belum ada."
            )

        return


# =========================
# START
# =========================

bot.run(TOKEN)
