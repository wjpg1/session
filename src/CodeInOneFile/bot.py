import aiosqlite
import discord
import asyncio
import os

from datetime import datetime
from discord.errors import Forbidden
from discord.ext import commands 
from dotenv import load_dotenv

load_dotenv('.env')
Token: str = os.getenv("TOKEN")
prefix: str = os.getenv("PREFIX")
invite: str = os.getenv("INVITE_LINK")

bot = commands.Bot(command_prefix=prefix, intents=discord.Intents.all())

async def setupdatabase():
    async with aiosqlite.connect("session.db") as sdb:
       await sdb.execute("CREATE TABLE IF NOT EXISTS blacklist ( g INTEGER, u INTEGER, PRIMARY KEY (g,u) )")
       await sdb.commit()

@bot.event
async def on_ready():
    print(f"[ + ] Logged in as: {bot.user}")
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
    elif isinstance(error, commands.MissingPermissions):
       await ctx.send(view = Recover(f"{ctx.author.mention}: You don't have the required permissions to make me perform that action!"), delete_after=5)
    elif isinstance(error, commands.CommandOnCooldown):
       await ctx.send(view = Recover(f"{ctx.author.mention}: Slow Down! You've to wait {error.retry_after:.2f}(s) before running this, again."), delete_after=5)
    else:
        await ctx.send(view = Recover(f"{ctx.author.mention}: An unexpected error occurred, {error}"), delete_after=5)

def blacklisted():
    async def predicate(ctx):
       b = await _checkblacklist(ctx.guild.id, ctx.author.id)
       if b:
          try:
             await ctx.author.send(view = Recover(f"⁉️ {ctx.author.mention}: You are unable to perform that action because you're being blacklisted in the server: {ctx.guild.name}"))
          except Forbidden:
             await ctx.send(view = Recover(f"⁉️ {ctx.author.mention}: You are unable to perform that action because you're being blacklisted in the server: {ctx.guild.name}"))
          return False
       return True
    return commands.check(predicate)

async def _blacklistedusers(guild: int):
    async with aiosqlite.connect('session.db') as sdb:
       c = await sdb.execute("SELECT u FROM blacklist WHERE g = ?", (guild,))
       rs = await c.fetchall()
       if not rs:
          return "There are no users that are blacklisted in this server, currently."
       return '\n'.join(str(r[0]) for r in rs)

async def _checkblacklist(guild: int, user: int):
    async with aiosqlite.connect('session.db') as sdb:
       cursor = await sdb.execute("SELECT u FROM blacklist WHERE g = ? AND u = ?", (guild, user))
       row = await cursor.fetchone()
       return row is not None

async def _blacklist(guild: int, user: int):
    async with aiosqlite.connect('session.db') as sdb:
       c = await sdb.execute("INSERT OR IGNORE INTO blacklist (g, u) VALUES (?,?)", (guild, user))
       await sdb.commit()

async def _unblacklist(guild: int, user: int):
    async with aiosqlite.connect('session.db') as sdb:
       c = await sdb.execute("DELETE FROM blacklist WHERE g = ? AND u = ?", (guild, user))
       await sdb.commit()

class Recover(discord.ui.LayoutView):
    def __init__(self, message: str, default_buttons: bool = False):
       super().__init__()
       container = discord.ui.Container(discord.ui.TextDisplay(message))
       sep = discord.ui.Separator(spacing = discord.SeparatorSpacing.large)
       footer = discord.ui.TextDisplay(datetime.now().strftime('%B %-d %Y %H:%M'))
       container.add_item(sep)
       container.add_item(footer) 
       if default_buttons:
          button = discord.ui.Button(label="Yes")
          button2 = discord.ui.Button(label="No")
          section  = discord.ui.Section(discord.ui.TextDisplay("Click the buttons below based on your decision"), accessory = button)
          container.add_item(section)
          container.add_item(button2)
          button.callback = self.bres
          button2.callback = self.b2res
       self.add_item(container)
    async def bres(self, interaction: discord.Interaction):
       await interaction.response.send_message(f"```{interaction.user.name}: You've confirmed the cleanup, it will be done in a few minutes.```", ephemeral=True)
       em = [emoji.delete() for emoji in interaction.guild.emojis]
       st = [sticker.delete() for sticker in interaction.guild.stickers]
       rl = [role.delete() for role in interaction.guild.roles if role < interaction.guild.me.top_role and not role.is_default()]
       cn = [member.edit(nick=None) for member in interaction.guild.members if not member.top_role > interaction.guild.me.top_role]
       webhooks = await interaction.guild.webhooks()
       wb = [webhook.delete() for webhook in webhooks]
       await asyncio.gather(*em, *st, *rl, *cn, *wb, return_exceptions=True)
    async def b2res(self, interaction: discord.Interaction):
       return await interaction.response.send_message(f"```{interaction.user.name}: You've successfully cancled the cleanup.```", ephemeral=True)

@bot.group(name="cleanup", invoke_without_subcommands=True)
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@blacklisted()
async def cleanup(ctx: commands.Context):
    try:
       await ctx.author.send(view = Recover(f"🤔 - {ctx.author.mention}: Are you sure that you want to clean {ctx.guild.name}.", True), delete_after=24 * 60)
    except Forbidden:
       await ctx.send(view = Recover(f"🤔 - {ctx.author.mention}: Are you sure that you want to clean {ctx.guild.name}.", True), delete_after=24 * 60)

@cleanup.command(name="deleteemojis", aliases=['de'])
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@blacklisted()
async def delete_emojis(ctx: commands.Context):
    em = [emoji.delete() for emoji in ctx.guild.emojis]
    await asyncio.gather(*em, return_exceptions=True)
    await ctx.message.add_reaction("👍")

@cleanup.command(name="deletestickers", aliases=['ds'])
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@blacklisted()
async def delete_stickers(ctx: commands.Context):
    st = [sticker.delete() for sticker in ctx.guild.stickers]
    await asyncio.gather(*st, return_exceptions=True)
    await ctx.message.add_reaction("👍")

@cleanup.command(name="deleteroles", aliases=['dr'])
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@blacklisted()
async def delete_roles(ctx: commands.Context):
    rl = [role.delete() for role in ctx.guild.roles if role < ctx.guild.me.top_role and not role.is_default()]
    await asyncio.gather(*rl, return_exceptions=True)
    await ctx.message.add_reaction("👍")

@cleanup.command(name='deletewebhooks', aliases=['dw', 'delweb'])
@commands.cooldown(1, 2, commands.BucketType.user)
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@blacklisted()
async def delete_webhooks(ctx: commands.Context):
    webhooks = await ctx.guild.webhooks()
    wb = [webhook.delete() for webhook in webhooks]
    await asyncio.gather(*wb, return_exceptions=True)
    await ctx.message.add_reaction('👍')

@cleanup.command(name="purge", aliases=['pg','clear'])
@commands.has_permissions(manage_messages=True)
@commands.bot_has_permissions(manage_messages=True)
@commands.cooldown(1,5, commands.BucketType.user)
@blacklisted()
async def purge(ctx: commands.Context, amount: int = 10):
    await ctx.channel.purge(limit=amount + 1)

@cleanup.command(name="clearnicks", aliases=['cn'])
@commands.has_permissions(manage_nicknames=True)
@commands.bot_has_permissions(manage_nicknames=True)
@commands.cooldown(1, 5, commands.BucketType.user)
@blacklisted()
async def clearnicknames(ctx: commands.Context):
    cn = [member.edit(nick=None) for member in ctx.guild.members if member.top_role < ctx.guild.me.top_role]
    await asyncio.gather(*cn, return_exceptions=True)
    await ctx.message.add_reaction("👍")

@bot.group(name="blacklisting", aliases=['bl'])
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 2, commands.BucketType.user)
@blacklisted()
async def blacklist(ctx: commands.Context, member: discord.Member, reason: str = "No reason is specified."):
    b = await _checkblacklist(ctx.guild.id, member.id)
    if member is ctx.guild.owner or member.top_role >= ctx.author.top_role:
       return await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot! You cannot blacklist the server's owner or someone who's higher in position than you."))
    if b:
       return await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot, {member.mention} is already blacklisted!"))
    await _blacklist(ctx.guild.id, member.id)
    await ctx.send(view = Recover(f"{ctx.author.mention}: {member.mention} has been successfully blacklisted in {ctx.guild.name}\nModerator: {ctx.author.mention}\nReason: {reason}"))

@blacklist.command(name="unblacklist", aliases=['remb','unblack'])
@commands.bot_has_permissions(administrator=True)
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 2, commands.BucketType.user)
@blacklisted()
async def unblacklist(ctx: commands.Context, member: discord.Member, reason: str = "No reason is specified."):
    b = await _checkblacklist(ctx.guild.id, member.id)
    if b:
       await _unblacklist(ctx.guild.id, member.id)
       await ctx.send(view = Recover(f"{ctx.author.mention}: {member.mention} has been successfully unblacklisted.\n Moderator: {ctx.author.mention}\nReason: {reason}"))
    else:
       await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot! {member.mention} is not blacklisted in this server."))

@bot.group(name="information", invoke_without_subcommands=True)
@commands.cooldown(1, 2, commands.BucketType.user)
async def information(ctx: commands.Context):
    await ctx.send(view = Recover(f"Information: \nServer-information: \nName: {ctx.guild.name}\nOwner: {ctx.guild.owner.mention}\n boosts: {ctx.guild.premium_subscription_count}\nRoles: {len(ctx.guild.roles)}\nMembers: {ctx.guild.member_count}\nChannels: Text - {len(ctx.guild.text_channels)} - Voice - {len(ctx.guild.voice_channels)}\nAll the informations about this bot: \nName: {bot.user.name}, Username: {bot.user}\nPrefix: {prefix}, Do {prefix}help to know about all the available commands."))

@information.command(name='serverinformation', aliases=['si'])
@commands.cooldown(1, 2, commands.BucketType.user)
async def serverinfo(ctx: commands.Context):
    await ctx.send(view = Recover(f"{ctx.guild.name}\nOverview: \nName: {ctx.guild.name}\nOwner: {ctx.guild.owner.mention}\n boosts: {ctx.guild.premium_subscription_count}\nOther: \nRoles: {len(ctx.guild.roles)}\nMembers: {ctx.guild.member_count}\nChannels: Text - {len(ctx.guild.text_channels)} - Voice - {len(ctx.guild.voice_channels)}"))

@information.command(name="blacklisted", aliases=['bls', 'utrb'])
@commands.cooldown(1,2, commands.BucketType.user)
async def usersthatareblacklisted(ctx: commands.Context):
    information = await _blacklistedusers(ctx.guild.id)
    await ctx.send(view = Recover(information))

@information.command(name="botinfo", aliases=['info', 'bi'])
@commands.cooldown(1, 2, commands.BucketType.user)
async def bot_info(ctx: commands.Context):
    await ctx.send(view = Recover(f"All the informations about this bot: \nInvite-link: [session]({invite})\nName: {bot.user.name}, Username: {bot.user}\nPrefix: {prefix}, Do {prefix}help to know all the available commands."))

@information.command(name="help", aliases=['hlp'])
@commands.cooldown(1, 2, commands.BucketType.user)
async def help(ctx: commands.Context):
    cmds = ', '.join(command.name for command in bot.commands)
    await ctx.send(view = Recover(cmds))

@information.command(name="ping", aliases=['png'])
@commands.cooldown(1, 2, commands.BucketType.user)
async def ping(ctx: commands.Context):
    await ctx.send(view = Recover(f"{round(bot.latency * 1000)}ms"))

bot.run(Token)
