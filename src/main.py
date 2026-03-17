import discord
import os
import aiosqlite

from discord.ext import commands
from asyncio import run 
from methods import Recover
from config import Prefix, Token

bot = commands.Bot(command_prefix=Prefix, intents=discord.Intents.all())
bot.remove_command('help')

async def setupdatabase():
    async with aiosqlite.connect("session.db") as sdb:
       await sdb.execute("CREATE TABLE IF NOT EXISTS blacklist ( g INTEGER, u INTEGER, PRIMARY KEY (g,u) )")
       await sdb.commit()

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user}")
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name="https:github.com/wjpg1"))
    await setupdatabase()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
       await ctx.send(view = Recover(f"{ctx.author.mention}: You missed an argument while using the command. Please check if the arguments given are correct."), delete_after=5)
    elif isinstance(error, commands.BadArgument):
       await ctx.send(view = Recover(f"{ctx.author.mention}: You've provided arguments that invalid! Please check if the arguments given are correct."), delete_after=5)
    elif isinstance(error, commands.BotMissingPermissions):
       await ctx.send(view = Recover(f"{ctx.author.mention}: I don't have the required permissions to execute that action. You can trust us, and consider giving administrator"), delete_after=5)
    elif isinstance(error, ocmmands.MissingPermissions):
       await ctx.send(view = Recover(f"{ctx.author.mention}: You don't have the required permissions to make me perform that action!"), delete_after=5)
    elif isinstance(error, commands.CommandOnCooldown):
       await ctx.send(view = Recover(f"{ctx.author.mention}: Slow Down! You've to wait {error.retry_after:.2f}(s) before running this, again."), delete_after=5)
    else:
        await ctx.send(view = Recover(f"{ctx.author.mention}: An unexpected error occurred, {error}"), delete_after=5)

async def main():
    async with bot:
       for file in os.listdir("./cogs"):
          if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")
       await bot.start(token)

run(main)
