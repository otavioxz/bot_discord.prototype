import discord
from discord.ext import commands

class Apresentacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_image(self, attachment):
        if attachment.content_type:
            return attachment.content_type.startswith("image/")
        return any(attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"])

    @commands.command(name='apresentar')
    async def apresentar(self, ctx, *, apresentacao: str = None):
        if not apresentacao:
            await ctx.send(
                f"{ctx.author.mention}, você precisa digitar sua apresentação após o comando. Exemplo:\n`!apresentar Olá, eu sou o João!`"
            )
            return

        attachments = ctx.message.attachments
        files = [await attachment.to_file() for attachment in attachments]

        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass

        canal = discord.utils.get(ctx.guild.channels, name='apresentacoes') or ctx.channel
        
        embed = discord.Embed(
            title=f"Apresentação de {ctx.author.display_name}",
            description=apresentacao,
            color=discord.Color.purple()
        )
        if ctx.author.avatar:
            embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_footer(text="Seja muito bem-vindo(a) ao servidor!")

        if attachments:
            primeiro = attachments[0]
            if self.is_image(primeiro):
                embed.set_image(url=f"attachment://{primeiro.filename}")

        if files:
            await canal.send(embed=embed, files=files)
        else:
            await canal.send(embed=embed)

        if canal != ctx.channel:
            await ctx.send(f"{ctx.author.mention}, sua apresentação foi enviada em {canal.mention}!")

async def setup(bot):
    await bot.add_cog(Apresentacao(bot))
