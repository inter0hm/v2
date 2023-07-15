import datetime
import json
import os
import traceback
import guilded
from guilded.ext import commands
import config
import requests
import pathlib

client = commands.Bot(command_prefix="gc!")


@client.event
async def on_message_delete(message: guilded.Message):
    print(1)
    endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.server.id}.json", "r")
    endpoint = json.load(endpoint_file)["discord"]
    if message.channel.id == \
            requests.get(f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"]["guilded"]:
        embed = guilded.Embed(title=f"{message.author.name} - Deleted", description=message.content, colour=0xf5c400)
        embed.add_field(name="Created at",
                        value=f'{datetime.datetime.strftime(message.created_at, "%Y-%m-%d %H:%M.%S")} UTC')
        channel = await client.fetch_channel(
            requests.get(f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["logs"][
                "guilded"])
        await channel.send(embed=embed)


@client.event
async def on_message_edit(before: guilded.Message, after: guilded.Message):
    print(2)
    endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{before.server.id}.json", "r")
    endpoint = json.load(endpoint_file)["discord"]
    if before.channel.id == \
            requests.get(f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"]["guilded"]:
        embed = guilded.Embed(title=f"{before.author.name} - Edited", description=after.content, colour=0xf5c400)
        embed.add_field(name="Jump", value=f"[Jump]({after.jump_url})")
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)

        channel = await client.fetch_channel(
            requests.get(f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["logs"][
                "guilded"])
        await channel.send(embed=embed)


@client.event
async def on_message(message: guilded.Message):
    if message.content.startswith("gc!"):
        global endpoint
        if message.content.startswith("gc!register"):
            try:
                endpoint = int(message.content.replace("gc!register ", ""))
            except ValueError:
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
                return
            print(endpoint)
            if endpoint == "":
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID`")
            else:
                try:
                    data = {"discord": endpoint}
                    json.dump(data,
                              open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.guild.id}.json",
                                   "x"))
                except FileExistsError:
                    await message.channel.send(f"Enpoint exists already: http://api.guildcord.deutscher775.de/{endpoint}")
                    return
                webhook = await message.channel.create_webhook(name="Guildcord")
                requests.post(
                    f"http://api.guildcord.deutscher775.de/update/{endpoint}?channel_guilded={message.channel.id}&"
                    f"webhook_guilded={webhook.url}&token={config.MASTER_TOKEN}")
                await message.channel.send(f"Updated enpoint: http://api.guildcord.deutscher775.de/{endpoint}")
        if message.content.startswith("gc!help"):
            embed = guilded.Embed(title="Guildcord", description="API Docs: http://api.guildcord.deutscher775.de/docs")
            embed.add_field(name="register",
                            value="Register you server.\nNote: First register your discord server, then guilded.",
                            inline=False)
            await message.channel.send(embed=embed)
        if message.content.startswith("gc!set-log"):
            try:
                endpoint = int(message.content.replace("gc!register ", ""))
            except ValueError:
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
                return
            channelid = message.content.replace("gc!set-log ", "").split(" ")[1]
            if endpoint == "" or channelid == "":
                await message.channel.send("Invalid Format: `gc!register DISCORD_SERVER_ID GUILDED_CHANNEL_ID`")
            else:
                requests.post(
                    f"http://api.guildcord.deutscher775.de/update/{endpoint}?channel_guilded={message.channel.id}&"
                    f"log_guilded={channelid}&token={config.MASTER_TOKEN}")
                await message.channel.send(f"Updated enpoint: http://api.guildcord.deutscher775.de/{endpoint}")
    else:
        try:
            endpoint_file = open(f"{pathlib.Path(__file__).parent.resolve()}/guilded_servers/{message.server.id}.json",
                                 "r")
            endpoint = json.load(endpoint_file)["discord"]
            if message.channel.id == requests.get(
                    f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                "config"]["channels"][
                "guilded"]:
                try:
                    blacklist = requests.get(
                        f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                        "config"]["blacklist"]
                    for word in blacklist:
                        if word is not None:
                            if word.lower() in message.content.lower():
                                embed = guilded.Embed(title=f"{message.author.name} - Flagged",
                                                      description=message.content, colour=0xf5c400)
                                channel = await client.fetch_channel(str(requests.get(
                                    f"http://api.guildcord.deutscher775.de/{endpoint}?token={config.MASTER_TOKEN}").json()[
                                                                             "config"]["logs"][
                                                                             "guilded"]))
                                await channel.send(embed=embed)
                                return
                        else:
                            pass
                    else:
                        if not message.author.bot:
                            if not message.attachments:
                                requests.post(
                                    f"http://api.guildcord.deutscher775.de/update/{endpoint}?message_content={message.content}&"
                                    f"message_author_name={message.author.name}&message_author_avatar={message.author.avatar.url}&"
                                    f"message_author_id={message.author.id}&trigger=true&sender=guilded&token={config.MASTER_TOKEN}")

                except requests.exceptions.JSONDecodeError:
                    print(2)
                    pass
        except FileNotFoundError:
            pass


client.run(config.GUILDED_TOKEN)