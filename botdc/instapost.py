import discord
from discord.ext import commands
from discord.ui import View, Button

class InstaView(View):
    def __init__(self, instagram_url):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="Ver publicação",
            emoji="<:instagram:1393677745334128690>",
            url=instagram_url,
            style=discord.ButtonStyle.link
        ))

class InstaPost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="instapost")
    @commands.has_permissions(administrator=True)
    async def instapost(self, ctx, membro: discord.Member = None, link: str = None):
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass  # Silencia erro se não puder apagar
        
        alvo = membro if isinstance(membro, discord.Member) else ctx.author

        # Corrige caso o primeiro argumento seja o link e não @membro
        if isinstance(membro, str) and membro.startswith("http"):
            link = membro
            alvo = ctx.author

        instagram_url = link or "https://www.instagram.com/daily.suyones/"

        # Trata anexos (imagem da publicação)
        files = [await att.to_file() for att in ctx.message.attachments]
        image_url = None
        if ctx.message.attachments:
            primeiro = ctx.message.attachments[0]
            if primeiro.content_type and primeiro.content_type.startswith("image/"):
                image_url = f"attachment://{primeiro.filename}"

        embed = discord.Embed(
            title="<:instagram:1393677745334128690> NOVA PUBLICAÇÃO NO INSTAGRAM!",
            description=f"{alvo.mention} acabou de postar no Instagram! 📷\nClique no botão abaixo para conferir.",
            color=discord.Color.from_rgb(193, 53, 132)
        )
        if image_url:
            embed.set_image(url=image_url)
        else:
            embed.set_image(url="https://cdn.discordapp.com/attachments/1393640980015747124/1393680010883240117/701428e8c5c7ba03303deb083cbb4e24.png")

        embed.set_footer(text="Deixe seu like e compartilhe!")
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed, view=InstaView(instagram_url), files=files if files else None)

    @instapost.error
    async def instapost_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, você precisa ser administrador para usar este comando.")

async def setup(bot):
    await bot.add_cog(InstaPost(bot))
