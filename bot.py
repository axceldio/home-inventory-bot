import os
import re
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import discord


TOKEN = os.getenv("DISCORD_TOKEN")

# =========================
# HTTP SERVER UNTUK RENDER
# =========================

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Home Inventory Bot is online!")

    def log_message(self, format, *args):
        return


def start_web_server():
    port = int(os.getenv("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


threading.Thread(
    target=start_web_server,
    daemon=True
).start()


# =========================
# DISCORD BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = discord.Client(intents=intents)

inventory = {}


# =========================
# FUNGSI INVENTORY
# =========================

def add_stock(item, amount):
    item = item.lower().strip()

    if item not in inventory:
        inventory[item] = 0

    inventory[item] += amount


def remove_stock(item, amount):
    item = item.lower().strip()

    if item not in inventory:
        inventory[item] = 0

    inventory[item] -= amount

    if inventory[item] < 0:
        inventory[item] = 0


def rebuild_inventory
