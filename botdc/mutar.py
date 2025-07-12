import discord
from discord.ext import commands

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mutar")
    @commands.has_permissions(manage_roles=True)
    async def mutar(self, ctx, membro: discord.Member):
        cargo_mutado = discord.utils.get(ctx.guild.roles, name="Mutado")
        if not cargo_mutado:
            await ctx.send("❌ Cargo 'Mutado' não encontrado. Por favor, crie o cargo com as permissões apropriadas.")
            return

        if cargo_mutado in membro.roles:
            await ctx.send(f"⚠️ {membro.mention} já está mutado.")
            return

        try:
            await membro.add_roles(cargo_mutado)
            await ctx.send(f"🔇 {membro.mention} foi mutado. Não grita. 🤫")
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para adicionar o cargo de Mutado.")

    @commands.command(name="desmutar")
    @commands.has_permissions(manage_roles=True)
    async def desmutar(self, ctx, membro: discord.Member):
        cargo_mutado = discord.utils.get(ctx.guild.roles, name="Mutado")
        if not cargo_mutado:
            await ctx.send("❌ Cargo 'Mutado' não encontrado.")
            return

        if cargo_mutado not in membro.roles:
            await ctx.send(f"⚠️ {membro.mention} não está mutado.")
            return

        try:
            await membro.remove_roles(cargo_mutado)
            await ctx.send(f"🔊 {membro.mention} foi desmutado.")
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para remover o cargo de Mutado.")

async def setup(bot):
    await bot.add_cog(MuteCog(bot))
