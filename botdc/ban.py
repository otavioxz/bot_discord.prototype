import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
from datetime import datetime, timedelta

SOFTBAN_FILE = "softbans.json"

class Moderacao(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.softbans = {}
        self.load_softbans()
        self.check_expired_softbans.start()

    def load_softbans(self):
        if os.path.exists(SOFTBAN_FILE):
            with open(SOFTBAN_FILE, "r") as f:
                data = json.load(f)
                self.softbans = {int(k): datetime.fromisoformat(v) for k, v in data.items()}
        else:
            self.softbans = {}

    def save_softbans(self):
        with open(SOFTBAN_FILE, "w") as f:
            data = {str(k): v.isoformat() for k, v in self.softbans.items()}
            json.dump(data, f, indent=4)

    async def aplicar_softban(self, guild: discord.Guild, membro: discord.Member, duracao_horas=72):
        for canal in guild.channels:
            try:
                await canal.set_permissions(membro, read_messages=False)
            except discord.Forbidden:
                pass

        termino = datetime.utcnow() + timedelta(hours=duracao_horas)
        self.softbans[membro.id] = termino
        self.save_softbans()

    async def remover_softban(self, guild: discord.Guild, membro: discord.Member):
        sucesso = False
        for canal in guild.channels:
            perms = canal.overwrites_for(membro)
            if perms.read_messages is False:
                try:
                    await canal.set_permissions(membro, overwrite=None)
                    sucesso = True
                except discord.Forbidden:
                    pass

        if membro.id in self.softbans:
            del self.softbans[membro.id]
            self.save_softbans()

        return sucesso

    @tasks.loop(minutes=1)
    async def check_expired_softbans(self):
        agora = datetime.utcnow()
        to_remove = [user_id for user_id, fim in self.softbans.items() if fim <= agora]

        for user_id in to_remove:
            for guild in self.bot.guilds:
                membro = guild.get_member(user_id)
                if membro:
                    sucesso = await self.remover_softban(guild, membro)
                    if sucesso:
                        try:
                            await membro.send(f"✅ Seu softban no servidor **{guild.name}** foi removido automaticamente após 3 dias.")
                        except discord.Forbidden:
                            pass

    @check_expired_softbans.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()

    @commands.command(name="banir")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, membro: discord.Member, *, motivo: str = "Sem motivo informado"):
        try:
            await membro.send(
                f"🚫 Você foi banido do servidor **{ctx.guild.name}**.\nMotivo: `{motivo}`"
            )
        except discord.Forbidden:
            pass
        await membro.ban(reason=motivo)
        await ctx.send(f"{membro.mention} foi banido. Motivo: `{motivo}`")

    @commands.command(name="desbanir")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        user = discord.Object(id=user_id)
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"✅ O usuário com ID `{user_id}` foi desbanido.")
        except discord.NotFound:
            await ctx.send("❌ Este usuário não está banido.")
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para desbanir este usuário.")
        except Exception as e:
            await ctx.send(f"⚠️ Ocorreu um erro ao tentar desbanir: {e}")

    @commands.command(name="avisar")
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, membro: discord.Member, *, motivo: str = "Sem motivo informado"):
        warn_niveis = ["Warn 1", "Warn 2", "Warn 3"]
        cargos_warn = [discord.utils.get(ctx.guild.roles, name=nome) for nome in warn_niveis]
        warn_atual = None

        for i, cargo in enumerate(cargos_warn):
            if cargo in membro.roles:
                warn_atual = i
                break

        proximo_warn = (warn_atual + 1) if warn_atual is not None else 0

        if proximo_warn >= len(cargos_warn):
            await ctx.send(f"{membro.mention} já atingiu o nível máximo de aviso.")
            return

        novo_cargo = cargos_warn[proximo_warn]
        if novo_cargo is None:
            await ctx.send(f"O cargo `{warn_niveis[proximo_warn]}` não foi encontrado no servidor.")
            return

        try:
            await membro.add_roles(novo_cargo)
            if warn_atual is not None:
                await membro.remove_roles(cargos_warn[warn_atual])
        except discord.Forbidden:
            await ctx.send("❌ Não tenho permissão para atribuir/remover esse cargo.")
            return

        try:
            await membro.send(
                f"⚠️ Você recebeu um aviso no servidor **{ctx.guild.name}**.\nNível: `{warn_niveis[proximo_warn]}`\nMotivo: `{motivo}`"
            )
        except discord.Forbidden:
            pass

        await ctx.send(f"{membro.mention} recebeu `{warn_niveis[proximo_warn]}`. Motivo: `{motivo}`")

        # Se for o terceiro warn, aplicar softban automático com mensagem explicativa
        if proximo_warn == 2:  # terceiro warn
            try:
                await membro.send(
                    f"🚫 Você não foi banido, mas este é um aviso final antes de um banimento permanente.\n"
                    f"Você ficará sem acesso aos canais do servidor por 3 dias para revisão.\n"
                    f"Se precisar de mais informações, entre em contato com a equipe de moderação."
                )
            except discord.Forbidden:
                pass
            await self.aplicar_softban(ctx.guild, membro)
            await ctx.send(f"🚫 {membro.mention} foi softbanido por 3 dias: não poderá ver canais do servidor até revisão.")

    @commands.command(name="desavisar")
    @commands.has_permissions(manage_roles=True)
    async def unwarn(self, ctx, membro: discord.Member):
        warn_niveis = ["Warn 1", "Warn 2", "Warn 3"]
        for nome in reversed(warn_niveis):
            cargo = discord.utils.get(ctx.guild.roles, name=nome)
            if cargo and cargo in membro.roles:
                try:
                    await membro.remove_roles(cargo)
                    await ctx.send(f"{membro.mention} teve o cargo `{nome}` removido.")
                    return
                except discord.Forbidden:
                    await ctx.send("❌ Não consegui remover o cargo do usuário.")
                    return

        await ctx.send(f"{membro.mention} não possui nenhum nível de warn.")

    @commands.command(name="softbanir")
    @commands.has_permissions(manage_roles=True)
    async def cmd_softban(self, ctx, membro: discord.Member):
        await self.aplicar_softban(ctx.guild, membro)
        await ctx.send(f"🚫 {membro.mention} foi softbanido por 3 dias: não poderá ver canais do servidor.")

    @commands.command(name="unsoftbanir")
    @commands.has_permissions(manage_roles=True)
    async def cmd_unsoftban(self, ctx, membro: discord.Member):
        sucesso = await self.remover_softban(ctx.guild, membro)
        if sucesso:
            await ctx.send(f"✅ Softban removido de {membro.mention}. Ele já pode ver os canais novamente.")
        else:
            await ctx.send(f"ℹ️ {membro.mention} não estava softbanido ou não consegui remover as permissões.")

    # Tratamento de erros geral
    @ban.error
    @warn.error
    @unban.error
    @unwarn.error
    @cmd_softban.error
    @cmd_unsoftban.error
    async def mod_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f"{ctx.author.mention}, você não tem permissão para usar este comando.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"{ctx.author.mention}, uso correto:\n"
                           "`!banir @usuário motivo`\n"
                           "`!avisar @usuário motivo`\n"
                           "`!desbanir ID_do_usuário`\n"
                           "`!desavisar @usuário`\n"
                           "`!softbanir @usuário`\n"
                           "`!unsoftbanir @usuário`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f"{ctx.author.mention}, mencione corretamente o usuário ou forneça o ID.")

async def setup(bot):
    await bot.add_cog(Moderacao(bot))
