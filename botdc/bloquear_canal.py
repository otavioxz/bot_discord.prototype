import discord
from discord.ext import commands

class ChatLock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="trancar")
    @commands.has_permissions(manage_channels=True)
    async def trancar(self, ctx):
        canal = ctx.channel
        try:
            await canal.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"🔒 {canal.mention} foi trancado. Ninguém pode enviar mensagens.")
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para alterar as permissões deste canal.")

    @commands.command(name="destrancar")
    @commands.has_permissions(manage_channels=True)
    async def destrancar(self, ctx):
        canal = ctx.channel
        try:
            await canal.set_permissions(ctx.guild.default_role, send_messages=None)
            await ctx.send(f"🔓 {canal.mention} foi destrancado. Todos podem enviar mensagens novamente.")
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para alterar as permissões deste canal.")

async def setup(bot):
    await bot.add_cog(ChatLock(bot))
