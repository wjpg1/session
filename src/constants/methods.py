import aiosqlite, discord; from datetime import datetime; from discord.errors import Forbidden

def blacklisted():
    async def predicate(ctx):
       b = await _checkblacklist(ctx.author.id, ctx.guild.id)
       if b:
          try:
             await ctx.author.send(view = Recover(f"⁉️ {ctx.author.mention}: You are unable to perform that action because you're being blacklisted in the server: {ctx.guild.name}"))
          except Forbidden:
             await ctx.send(view = Recover(f"⁉️ {ctx.author.mention}: You are unable to perform that action because you're being blacklisted in the server: {ctx.guild.name}"))
          return False
       return True
    return commands.check(predicate)

async def _blacklistedusers(guild: int):
    async with aiosqlite.connect('database/session.db') as sdb:
       c = await sdb.execute("SELECT u FROM blacklist WHERE g = ?", (guild,))
       rs = await c.fetchall()
       if not rs:
          return "There are no users that are blacklisted in this server, currently."
       return '\n'.join(str(r[0]) for r in rs)

async def _checkblacklist(guild: int, user: int):
    async with aiosqlite.connect('database/session.db') as sdb:
       cursor = await sdb.execute("SELECT u FROM blacklist WHERE g = ? AND u = ?", (guild, user))
       row = await cursor.fetchone()
       return row is not None

async def _blacklist(guild: int, user: int):
    async with aiosqlite.connect('database/session.db') as sdb:
       c = await sdb.execute("INSERT INTO blacklist (g, u) VALUES (?,?)", (guild, user))
       await sdb.commit()

async def _unblacklist(guild: int, user: int):
    async with aiosqlite.connect('database/session.db') as sdb:
       c = await sdb.execute("DELETE FROM blacklist WHERE g = ? AND u = ?", (guild, user))
       await sdb.commit()

class Recover(discord.ui.LayoutView):
    def __init__(self, message: str, default_buttons: bool = False):
       super().__init__(timeout=60.0)
       container = discord.ui.Container()
       msg = discord.ui.TextDisplay(message)
       sep = discord.ui.Separator(spacing = discord.SeparatorSpacing.large)
       footer = discord.ui.TextDisplay(datetime.now().strftime('%B %d %Y %H:%M'))
       container.add_item(msg)
       container.add_item(sep)
       container.add_item(footer)
       if default_buttons:
          button = discord.ui.Button(label="Yes")
          button2 = discord.ui.Button(label="No")
          button.callback = self.bres
          button2.callback = self.b2res
          section = discord.ui.Section(discord.ui.TextDisplay("Click the button 'Yes', if you're sure."), accessory = button)
          section2 = discord.ui.Section(discord.ui.TextDisplay("Click the button 'No', if you're unsure."), accessory = button2)
          container.add_item(section)
          container.add_item(section2)
       self.add_item(container)
    async def bres(self, interaction: discord.Interaction):
       await interaction.response.send_message(f"```{interaction.user.name}: You've confirmed the cleanup, it will be done in a few minutes.```", ephemeral=True)
       em = [emoji.delete() for emoji in interaction.guild.emojis]
       st = [sticker.delete() for sticker in interaction.guild.stickers]
       rl = [role.delete() for role in interaction.guild.roles if role < interaction.guild.me.top_role and not role.is_default()]
       cn = [member.edit(nick=None) for member in interaction.guild.members if member.top_role < interaction.guild.me.top_role]
       webhooks = await interaction.guild.webhooks()
       wb = [webhook.delete() for webhook in webhooks]
       await asyncio.gather(*em, *st, *rl, *cn, *wb, return_exceptions=True)
    async def b2res(self, interaction: discord.Interaction):
       return await interaction.response.send_message(f"```{interaction.user.name}: You've successfully canclled the cleanup. It won't happen, now. Thanks for your patience.```", ephemeral=True)
