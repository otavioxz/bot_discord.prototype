import discord
from discord.ext import commands
import json
import os
import time  # Import necessário para o controle de tempo

XP_FILE = "xp.json"
LEVEL_UP_CHANNEL_ID = 1387212160870125660  # Canal para avisos de level up

class XpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if os.path.exists(XP_FILE):
            with open(XP_FILE, "r") as f:
                self.xp_data = json.load(f)
        else:
            self.xp_data = {}

        self.last_message_time = {}  # Dicionário para controle de cooldown

        self.level_roles = {
            1: 1369233687123722310,
            5: 1387208333303349302,
            10: 1387231485760635013,
            20: 1387229822245277706,
            30: 1387229845343305779,
            50: 1387229846773432530
        }

    def save_xp(self):
        with open(XP_FILE, "w") as f:
            json.dump(self.xp_data, f, indent=4)

    def get_level(self, xp):
        return xp // 1000

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        now = time.time()
        last_time = self.last_message_time.get(user_id, 0)

        if now - last_time < 15:  # Delay de 60 segundos por usuário
            return

        self.last_message_time[user_id] = now

        xp_anterior = self.xp_data.get(user_id, 0)
        novo_xp = xp_anterior + 3
        self.xp_data[user_id] = novo_xp
        self.save_xp()

        level_antigo = self.get_level(xp_anterior)
        level_novo = self.get_level(novo_xp)

        member = message.author
        guild = message.guild

        if level_novo > level_antigo:
            canal_levelup = guild.get_channel(LEVEL_UP_CHANNEL_ID)
            if canal_levelup:
                await canal_levelup.send(
                    f"🆙 {member.mention} subiu para o nível {level_novo}! Parabéns! 🎉"
                )
            else:
                await message.channel.send(
                    f"🆙 {member.mention} subiu para o nível {level_novo}! Parabéns! 🎉"
                )

        niveis_definidos = sorted(self.level_roles.keys())
        nivel_chave = 0
        for lvl in niveis_definidos:
            if level_novo >= lvl:
                nivel_chave = lvl
            else:
                break

        for lvl, role_id in self.level_roles.items():
            role = guild.get_role(role_id)
            if role is None:
                continue
            if lvl != nivel_chave and role in member.roles:
                await member.remove_roles(role)

        cargo_chave = guild.get_role(self.level_roles[nivel_chave])
        if cargo_chave and cargo_chave not in member.roles:
            await member.add_roles(cargo_chave)

    @commands.command()
    async def nivel(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        xp = self.xp_data.get(str(member.id), 0)
        level = self.get_level(xp)
        await ctx.send(f"{member.mention} está no nível {level} com {xp} XP.")

    @commands.command()
    async def ranking(self, ctx):
        """Mostra o top 10 usuários com mais XP"""
        if not self.xp_data:
            await ctx.send("Nenhum dado de XP encontrado.")
            return

        ranking = sorted(self.xp_data.items(), key=lambda x: x[1], reverse=True)
        top_10 = ranking[:10]

        embed = discord.Embed(title="🏆 Ranking de XP", color=discord.Color.gold())
        for i, (user_id, xp) in enumerate(top_10, start=1):
            user = ctx.guild.get_member(int(user_id))
            nome = user.mention if user else f"ID {user_id}"
            nivel = self.get_level(xp)
            embed.add_field(name=f"{i}º lugar", value=f"{nome} — Nível {nivel} ({xp} XP)", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(XpCog(bot))
