# from discord.ext import commands
# import requests
# import random
# import discord
#
#
# class CommandEvents(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#
# # inhouse stuff from https://github.com/danishanish/inHouse/blob/main/inHouse.py
# rerolls = 2
# champ_dict = {}
# championPool = []
#
#
# def fetch_champ_names():
#     ddragonVersion = requests.get("https://ddragon.leagueoflegends.com/realms/na.json").json()['dd']
#     r = requests.get("http://ddragon.leagueoflegends.com/cdn/" + ddragonVersion + "/data/en_US/champion.json")
#     print(f"Status of ddragon: {r.status_code}")
#     if r.status_code == 200:
#         champions = r.json()
#     else:
#         return f"error:{r.status_code} ddragon server"
#
#     # shuffling champ pool
#     championPool = []
#     for key in champions['data']:
#         championPool.append(champions['data'][key]['name'])
#         random.shuffle(championPool)
#
#     # pairing champ names and ids
#     champnames = list(champions['data'].keys())
#     champ_dict = {}
#     for n in champnames:
#         champ_dict[champions['data'][n]['name']] = champions['data'][n]['id']
#     # print(champ_dict)
#     return champ_dict, championPool
#
#
# @commands.Cog.listener
# async def inhouse(self, ctx):
#     global id
#     global champ_dict, championPool
#     champ_dict, championPool = fetch_champ_names()
#     txt = 'Please react with the emoji below to obtain your champions!\nNote: This bot will only be checking for reactions for about \na minute, so react quickly!'
#     embed = discord.Embed(title="League In-Houses!", description=txt, colour=discord.Colour.teal())
#     temp = ctx.message
#     msg = await temp.channel.send(embed=embed)
#     id = msg.id
#     print(id)
#     # await ctx.send(msg)
#     await msg.add_reaction('🗿')
#
#
# async def league_roll(self, name, payload):
#     ch = payload.channel_id
#
#     for reroll in range(0, rerolls):
#         champ = championPool.pop(0)
#         champ_url = champ_dict[champ]
#
#         e = discord.Embed(title=f"{name} has rolled {champ}!", colour=discord.Colour.red())
#
#         url = "http://ddragon.leagueoflegends.com/cdn/11.11.1/img/champion/" + champ_url + ".png"
#         e.set_thumbnail(url=url)
#         # await client.get_channel(ch).send(embed=e)
#
#
# @commands.Cog.listener
# async def on_raw_reaction_add(payload):
#     global id
#     bot_id = 849793681665294358
#     react_id = payload.message_id
#     name = payload.member
#     if react_id == id and payload.user_id != bot_id:
#         await league_roll(name, payload)
#
#
#
# def setup(bot):
#     bot.add_cog(CommandEvents(bot))