import discord
from discord.ext import commands

class ListaComandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="comandos", aliases=["ajuda"])
    async def comandos(self, ctx):
        embed = discord.Embed(
            title="📜 Lista de Comandos Disponíveis",
            description="Aqui estão os comandos que você pode usar:",
            color=discord.Color.blue()
        )

        # Moderação Parte 1
        embed.add_field(
            name="👮 Moderação (1/2)",
            value=(
                "`!banir @usuário motivo` — Bane um membro do servidor\n"
                "`!desbanir ID` — Desbane um usuário pelo ID\n"
                "`!avisar @usuário motivo` — Dá um aviso e aplica o cargo Warn\n"
                "`!desavisar @usuário` — Remove o cargo Warn\n"
                "`!fban @usuário motivo` — Isola o usuário (necessita cargo 'Fake Ban')\n"
                "`!fbandes @usuário` — Remove o isolamento"
            ),
            inline=False
        )

        # Moderação Parte 2
        embed.add_field(
            name="👮 Moderação (2/2)",
            value=(
                "`!trancar` — Tranca o canal onde o comando foi usado\n"
                "`!destrancar` — Destranca o canal onde o comando foi usado\n"
                "`!mutar @usuário motivo` — Muta o usuário em todos os canais\n"
                "`!desmutar @usuário` — Desmuta o usuário em todos os canais\n"
                "`!softbanir @usuário` — Aplica softban manualmente\n"
                "`!unsoftbanir @usuário` — Remove o softban aplicado"
            ),
            inline=False
        )

        # Outros Comandos de Moderação
        embed.add_field(
            name="⚙️ Comandos Avançados / Gerais",
            value=(
                "`!setup_ticket` — Faz o setup inicial do sistema de tickets\n"
                "`!mensagem #canal` — Envia uma mensagem através do bot\n"
                "`!liveon @usuário` — Anuncia que o usuário está ao vivo\n"
                "`!redes @usuário` — Exibe todas as redes sociais do usuário\n"
                "`!instapost @usuário link` — Anuncia um post novo no Instagram"
            ),
            inline=False
        )

        # Utilidade
        embed.add_field(
            name="📢 Utilidade",
            value=(
                "`!ajuda` ou `!comandos` — Mostra esta lista de comandos\n"
                "`!apresentar mensagem + imagem` — Exibe uma apresentação personalizada"
            ),
            inline=False
        )

        embed.set_footer(text="Use os comandos com responsabilidade 🤝")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ListaComandos(bot))
