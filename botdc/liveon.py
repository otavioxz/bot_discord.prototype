import discord
from discord.ext import commands
from discord.ui import View, Button

class LiveView(View):
    def __init__(self, twitch_link):
        super().__init__(timeout=None)
        self.add_item(Button(
            label="Assistir agora",
            emoji="<:twitch:1393677773939413113>",
            url=twitch_link,
            style=discord.ButtonStyle.link
        ))

class LiveOn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="liveon")
    @commands.has_permissions(administrator=True)
    async def liveon(self, ctx, membro: discord.Member = None):
        # Tenta deletar a mensagem do comando
        try:
            await ctx.message.delete()
        except (discord.Forbidden, discord.NotFound):
            pass  # Silencia erro se não puder apagar

        alvo = membro or ctx.author
        twitch_url = "https://www.twitch.tv/suyones"

        embed = discord.Embed(
            title="<:twitch:1393677773939413113> LIVE AO VIVO AGORA!",
            description=f"{alvo.mention} está transmitindo ao vivo na Twitch! 🎥\nClique no botão abaixo para assistir agora.",
            color=discord.Color.purple()
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1393640980015747124/1393680010883240117/701428e8c5c7ba03303deb083cbb4e24.png")
        embed.set_footer(text="Vamos dar aquela força na live!")
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed, view=LiveView(twitch_url))

    @liveon.error
    async def liveon_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, você precisa ser administrador para usar este comando.")

async def setup(bot):
    await bot.add_cog(LiveOn(bot))
