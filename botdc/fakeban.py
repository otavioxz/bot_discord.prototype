import discord
from discord.ext import commands

class FakeBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="fban")
    @commands.has_permissions(manage_roles=True)
    async def fakeban(self, ctx, membro: discord.Member, *, motivo: str = "Sem motivo informado"):
        cargo_fakeban = discord.utils.get(ctx.guild.roles, name="Fake Ban")

        if not cargo_fakeban:
            await ctx.send("❌ O cargo `Fake Ban` não existe. Crie-o nas configurações do servidor.")
            return

        # Guarda os cargos do usuário (exceto @everyone e cargos acima do bot)
        cargos_removiveis = [
            cargo for cargo in membro.roles
            if cargo != ctx.guild.default_role and cargo.position < ctx.author.top_role.position
        ]

        try:
            await membro.edit(roles=[cargo_fakeban])
            try:
                await membro.send(
                    f"🚫 Você foi colocado em modo de isolamento (`Fake Ban`) no servidor **{ctx.guild.name}**.\nMotivo: `{motivo}`"
                )
            except discord.Forbidden:
                pass

            await ctx.send(f"{membro.mention} foi colocado em isolamento. Motivo: `{motivo}`")

        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para editar os cargos deste usuário.")

    @commands.command(name="fdesbanir")
    @commands.has_permissions(manage_roles=True)
    async def unfakeban(self, ctx, membro: discord.Member):
        cargo_fakeban = discord.utils.get(ctx.guild.roles, name="Fake Ban")

        if cargo_fakeban in membro.roles:
            try:
                await membro.remove_roles(cargo_fakeban)
                await ctx.send(f"{membro.mention} foi removido do modo de isolamento.")
            except discord.Forbidden:
                await ctx.send("❌ Não consegui remover o cargo `Fake Ban` deste usuário.")
        else:
            await ctx.send(f"{membro.mention} não está com o cargo `Fake Ban`.")

async def setup(bot):
    await bot.add_cog(FakeBan(bot))
