import discord
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import os
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    await tree.sync()
    print("🔧 Commands synced!")

@tree.command(name="tagsearch", description="Search tags on nelly.tools")
async def tagsearch(interaction: discord.Interaction, query: str):
    await interaction.response.defer()

    url = f"https://nelly.tools/tags?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        await interaction.followup.send(f"❌ Failed to fetch data. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    tag_cards = soup.find_all("div", class_="tag-card")

    if not tag_cards:
        await interaction.followup.send("😕 No tags found.")
        return

    results = []
    for card in tag_cards:
        name = card.find("h3").text.strip()
        link = "https://nelly.tools" + card.find("a")["href"]
        members_text = card.find("div", class_="members").text
        members = int(''.join(filter(str.isdigit, members_text)))
        results.append((name, members, link))

    results.sort(key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title=f"🔎 Results for: {query}", color=0x2f3136)
    for name, members, link in results[:5]:
        embed.add_field(name=name, value=f"[Link]({link}) – 👥 {members} members", inline=False)

    await interaction.followup.send(embed=embed)

bot.run(os.getenv("TOKEN"))
