
import discord
import asyncio

from datetime import datetime
from methods import Recover, _unblacklist, _blacklist, _blacklistedusers, blacklisted, _checkblacklist
from discord.ext import commands
from discord.errors import Forbidden
from config import Prefix
from typing import Final

prefix: Final[str] = Prefix

class Session(commands.Cog):
    def __init__(self, bot):
       self.bot = bot
    @commands.command(name="cleanup", aliases=['cln', 'clean', 'wipe']))
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @blacklisted()
    async def cleanup(self, ctx: commands.Context):
       try:
          await ctx.author.send(view = Recover(f"🤔 - {ctx.author.mention}: Are you sure that you want to clean {ctx.guild.name}.", True), delete_after=24 * 60)
       except Forbidden:
          await ctx.send(view = Recover(f"🤔 - {ctx.author.mention}: Are you sure that you want to clean {ctx.guild.name}.", True), delete_after=24 * 60)
    @commands.command(name="deletemojis", aliases=['de', 'delemo'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @blacklisted()
    async def delete_emojis(self, ctx: commands.Context):
          em = [emoji.delete() for emoji in ctx.guild.emojis]
          await asyncio.gather(*em, return_exceptions=True)
          await ctx.message.add_reaction("👍")
    @commands.command(name="deletestickers", aliases=['ds', 'delroles'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @blacklisted()
    async def delete_stickers(self, ctx: commands.Context):
          st = [sticker.delete() for sticker in ctx.guild.stickers]
          await asyncio.gather(*st, return_exceptions=True)
          await ctx.message.add_reaction("👍")
    @commands.command(name="deleteroles", aliases=['dr'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @blacklisted()
    async def delete_roles(self, ctx: commands.Context):
       rl = [role.delete() for role in ctx.guild.roles if role < ctx.guild.me.top_role and not role.is_default()]
       await asyncio.gather(*rl, return_exceptions=True)
       await ctx.message.add_reaction("👍")
    @commands.command(name='deletewebhooks', aliases=['dw', 'delweb'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @blacklisted()
    async def delete_webhooks(self, ctx: commands.Context):
       webhooks = await ctx.guild.webhooks()
       wb = [webhook.delete() for webhook in webhooks]
       await asyncio.gather(*wb, return_exceptions=True)
       await ctx.message.add_reaction('👍')
    @commands.command(name="purge", aliases=['pg','clear'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    @commands.cooldown(1,5, commands.BucketType.user)
    @blacklisted()
    async def purge(self, ctx: commands.Context, amount: int = 10):
        amount = min(amount, 100)
        await ctx.channel.purge(limit=amount + 1)
    @commands.command(name="clearnicks", aliases=['cn', 'clrnicks'])
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1,5, commands.BucketType.user)
    @blacklisted()
    async def clearnicknames(self, ctx: commands.Context):
       cn = [member.edit(nick=None) for member in ctx.guild.members if member.top_role < ctx.guild.me.top_role]
       await asyncio.gather(*cn, return_exceptions=True)
       await ctx.message.add_reaction("👍")
    @commands.command(ame="blacklist", aliases=['bl', 'addblacklist'])
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1,2, commands.BucketType.user)
    @blacklisted()
    async def blacklist(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason was specified."):
       b = await _checkblacklist(ctx.guild.id, member.id)
       if member is ctx.guild.owner or member.top_role >= ctx.author.top_role:
          return await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot! You cannot blacklist the server's owner or someone who's higher in position than you."))
       if b:
          return await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot, {member.mention} is already blacklisted!"))
       await _blacklist(ctx.guild.id, member.id)
       await ctx.send(view = Recover(f"{ctx.author.mention}: {member.mention} has been successfully blacklisted in {ctx.guild.name}\nModerator: {ctx.author.mention}\nReason: {reason}"))
    @commands.command(name="unblacklist", aliases=['remb','unblack'])
    @commands.bot_has_permissions(administrator=True)
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1,2, commands.BucketType.user)
    @blacklisted()
    async def unblacklist(self, ctx: commands.Context, member: discord.Member, reason: str = "No reason is specified."):
       b = await _checkblacklist(ctx.guild.id, member.id)
       if b:
          await _unblacklist(ctx.guild.id, member.id)
          await ctx.send(view = Recover(f"{ctx.author.mention}: {member.mention} has been successfully unblacklisted.\nModerator: {ctx.author.mention}\nReason: {reason}"))
       else:
          await ctx.send(view = Recover(f"{ctx.author.mention}: Idiot! {member.mention} is not blacklisted in this server."))
    @commands.command(name="information", aliases=['info'])
    @commands.cooldown(1,2, commands.BucketType.user)
    async def information(self, ctx: commands.Context):
       await ctx.send(view = Recover(f"Information: \nServer-information: \nName: {ctx.guild.name}\nOwner: {ctx.guild.owner.mention}\nBoosts: {ctx.guild.premium_subscription_count}\nOther: \nRoles: {len(ctx.guild.roles)}\nMembers: {ctx.guild.member_count}\nChannels: Text - {len(ctx.guild.text_channels)} - Voice - {len(ctx.guild.voice_channels)}\n\nAll the informations about this bot: \n\nName: {self.bot.user.name}\nUsername: {self.bot.user}\nPrefix: {prefix} \nDo {prefix}help to know about all the available commands."))
    @commands.command(name='serverinformation', aliases=['si', 'serverinfo'])
    @commands.cooldown(1,2, commands.BucketType.user)
    async def serverinformation(self, ctx: commands.Context):
       await ctx.send(view = Recover(f"{ctx.guild.name}\nOverview: \nName: {ctx.guild.name}\nOwner: {ctx.guild.owner.mention}\nBoosts: {ctx.guild.premium_subscription_count}\nOther: \nRoles: {len(ctx.guild.roles)}\nMembers: {ctx.guild.member_count}\nChannels: Text - {len(ctx.guild.text_channels)} - Voice - {len(ctx.guild.voice_channels)}"))
    @commands.command(name="blacklisted", aliases=['bls', 'utrb'])
    @commands.cooldown(1,2, commands.BucketType.user)
    async def userthatarebacklisted(self, ctx: commands.Context):
       information = await _blacklistedusers(ctx.guild.id)
       await ctx.send(view = Recover(information))
    @commands.command(name="botinfo", aliases=['info', 'bi'])
    async def bot_info(self, ctx: commands.Context):
       await ctx.send(view = Recover(f"All the informations about this bot: \nInvite-link: [session]({invitelink})\nName: {self.bot.user.name}\nUsername: {self.bot.user}\nPrefix: {prefix}, Do {prefix}help to know all the available commands."))
    @commands.command(name="help", aliases=['hlp', 'cmds'])
    @commands.cooldown(1,2, commands.BucketType.user)
    async def help(self, ctx: commands.Context):
       cmds = ', '.join(command.name for command in self.bot.commands)
       await ctx.send(view = Recover(cmds))
    @commands.command(name="ping", aliases=['png', 'latency'])
    @commands.cooldown(1,2, commands.BucketType.user)
    async def ping(self, ctx: commands.Context):
       await ctx.send(view = Recover(f"{round(self.bot.latency * 1000)}ms"))
async def setup(bot):
    await bot.add_cog(Session(bot))
