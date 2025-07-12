import discord
from discord.ext import commands
import random

class Aviso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mensagem")
    @commands.has_permissions(manage_messages=True)
    async def aviso(self, ctx, *, mensagem: str = None):
        if not mensagem and not ctx.message.attachments:
            await ctx.send(
                f"{ctx.author.mention}, você precisa escrever a mensagem. Exemplo:\n"
                "`!mensagem #canal Texto do aviso` ou `!mensagem 123456789012345678 Texto do aviso`"
            )
            return

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        canal_destino = ctx.channel
        texto = mensagem or ""

        palavras = texto.split()

        # Detecta canal por menção
        if ctx.message.channel_mentions:
            canal_destino = ctx.message.channel_mentions[0]
            texto = texto[len(ctx.message.channel_mentions[0].mention):].strip()
        # Ou detecta canal por ID numérica
        elif palavras and palavras[0].isdigit():
            canal_id = int(palavras[0])
            canal_busca = ctx.guild.get_channel(canal_id)
            if canal_busca:
                canal_destino = canal_busca
                texto = texto[len(palavras[0]):].strip()

        # Gera uma cor aleatória
        cor_aleatoria = discord.Color.from_rgb(
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )

        # Prepara o embed
        embed = discord.Embed(
            title="📢 Aviso",
            description=texto if texto else " ",
            color=cor_aleatoria
        )
        embed.set_footer(text=f"Aviso enviado por {ctx.author.display_name}")
        embed.timestamp = ctx.message.created_at

        # Trata anexos, embutindo a primeira imagem (se houver)
        files = [await att.to_file() for att in ctx.message.attachments]
        if ctx.message.attachments:
            primeiro = ctx.message.attachments[0]
            if primeiro.content_type and primeiro.content_type.startswith("image/"):
                embed.set_image(url=f"attachment://{primeiro.filename}")

        try:
            if files:
                await canal_destino.send(embed=embed, files=files)
            else:
                await canal_destino.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"❌ Não tenho permissão para enviar mensagens em {canal_destino.mention}.")
        else:
            if canal_destino != ctx.channel:
                await ctx.send(f"Aviso enviado com sucesso em {canal_destino.mention} ✅")

    @aviso.error
    async def aviso_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"{ctx.author.mention}, você precisa informar a mensagem. Exemplo:\n"
                "`!mensagem #canal Texto do aviso`"
            )

async def setup(bot):
    await bot.add_cog(Aviso(bot))
