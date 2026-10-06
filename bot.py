import os
import re
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Barang yang sedang tersimpan
inventory = {}


def change_stock(item, amount):
    item = item.lower().strip()

    if item not in inventory:
        inventory[item] = 0

    inventory[item] += amount

    if inventory[item] < 0:
        inventory[item] = 0


@bot.event
async def on_ready():
    print(f"Bot online sebagai {bot.user}")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    text = message.content.strip()

    # +barang jumlah
    match_add = re.match(r"^\+(.+?)\s+(\d+)$", text)

    # -barang jumlah
    match_remove = re.match(r"^-(.+?)\s+(\d+)$", text)

    if match_add:
        item = match_add.group(1)
        amount = int(match_add.group(2))

        change_stock(item, amount)

        await message.channel.send(
            f"✅ **{item.title()}** +{amount}\n"
            f"📦 Stok sekarang: **{inventory[item.lower().strip()]}**"
        )

    elif match_remove:
        item = match_remove.group(1)
        amount = int(match_remove.group(2))

        change_stock(item, -amount)

        await message.channel.send(
            f"✅ **{item.title()}** -{amount}\n"
            f"📦 Stok sekarang: **{inventory[item.lower().strip()]}**"
        )

    elif text.lower() == "!stok":
        if not inventory:
            await message.channel.send("📦 Inventory masih kosong.")
        else:
            lines = ["🏠 **HOME INVENTORY**", ""]

            for item, amount in sorted(inventory.items()):
                if amount == 0:
                    icon = "❌"
                elif amount == 1:
                    icon = "⚠️"
                else:
                    icon = "📦"

                lines.append(
                    f"{icon} **{item.title()}** — {amount}"
                )

            await message.channel.send("\n".join(lines))

    elif text.lower().startswith("!stok "):
        item = text[6:].lower().strip()

        if item in inventory:
            await message.channel.send(
                f"📦 **{item.title()}**: {inventory[item]}"
            )
        else:
            await message.channel.send(
                f"❌ **{item.title()}** belum ada di inventory."
            )

    await bot.process_commands(message)


bot.run(TOKEN)
