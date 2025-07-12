import discord
from discord.ext import commands
from discord.ui import View, Button

class RedesView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="X (Twitter)",
            emoji="<:x_:1393677794084393114>",
            url="https://x.com/suyones",
            style=discord.ButtonStyle.secondary
        ))
        self.add_item(Button(
            label="TikTok",
            emoji="<:tiktok:1393677759472996452>",
            url="https://www.tiktok.com/@daily.suyones",
            style=discord.ButtonStyle.secondary
        ))
        self.add_item(Button(
            label="Instagram",
            emoji="<:instagram:1393677745334128690>",
            url="https://www.instagram.com/daily.suyones/",
            style=discord.ButtonStyle.secondary
        ))
        self.add_item(Button(
            label="Twitch",
            emoji="<:twitch:1393677773939413113>",
            url="https://www.twitch.tv/suyones/",
            style=discord.ButtonStyle.secondary
        ))

class RedesSociais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="redes")
    @commands.has_permissions(administrator=True)  # ⛔ Apenas administradores podem usar
    async def redes(self, ctx, membro: discord.Member = None):
        alvo = membro or ctx.author

        embed = discord.Embed(
            title="✒ REDES SOCIAIS ✒",
            description="É só clicar em cima do nome da rede social para acessar o link.",
            color=discord.Color.dark_gray()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1393640980015747124/1393680010883240117/701428e8c5c7ba03303deb083cbb4e24.png")

        await ctx.send(
            content=f"Olá, você está no canal dedicado ao {alvo.mention}!\nConheça suas redes sociais:",
            embed=embed,
            view=RedesView()
        )

    @redes.error
    async def redes_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, você precisa ser administrador para usar este comando.")

async def setup(bot):
    await bot.add_cog(RedesSociais(bot))
