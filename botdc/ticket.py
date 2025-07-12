import discord
from discord.ext import commands
from discord.ui import View, Button
import random
import os

# IDs a configurar
SUPORTE_ROLE_ID = 1386848744909307904
CATEGORIA_TICKET_ID = 1387710673647173727
LOG_CHANNEL_ID = 1389080684806803609

# === VIEWS ===

class AbrirTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🎟️ Abrir Ticket", style=discord.ButtonStyle.primary, custom_id="abrir_ticket"))

class TicketControlsView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="🔒 Bloquear Ticket", style=discord.ButtonStyle.gray, custom_id="bloquear_ticket"))
        self.add_item(Button(label="❌ Fechar Ticket", style=discord.ButtonStyle.red, custom_id="fechar_ticket"))

class ConfirmarFechamentoView(View):
    @discord.ui.button(label="✅ Sim, fechar", style=discord.ButtonStyle.danger)
    async def confirmar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Fechando o ticket e enviando mensagem no privado...", ephemeral=True)

        canal = interaction.channel
        autor = None
        partes = canal.name.split("-")
        if len(partes) >= 4:
            try:
                user_id = int(partes[2])
                autor = canal.guild.get_member(user_id)
            except:
                pass

        await TicketSystem.salvar_log(interaction, autor=autor)
        await canal.delete()

    @discord.ui.button(label="❌ Cancelar", style=discord.ButtonStyle.secondary)
    async def cancelar(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(content="Cancelado.", view=None)

# === COG ===

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}  # ← Cooldowns por usuário

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_ticket(self, ctx):
        embed = discord.Embed(
            title="Central de Suporte 📫",
            description="Clique no botão abaixo para abrir um ticket.",
            color=discord.Color.purple()
        )
        await ctx.send(embed=embed, view=AbrirTicketView())

    @commands.command()
    async def close(self, ctx):
        if "ticket" in ctx.channel.name:
            await ctx.send("Encerrando o ticket...")
            await self.salvar_log(ctx)
            await ctx.channel.delete()
        else:
            await ctx.send("Este comando só pode ser usado em canais de ticket.")

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.component:
            return

        custom_id = interaction.data.get("custom_id")

        is_admin = interaction.user.guild_permissions.administrator
        suporte_role = interaction.guild.get_role(SUPORTE_ROLE_ID)
        has_suporte = suporte_role in interaction.user.roles if suporte_role else False

        if custom_id == "abrir_ticket":
            user_id = interaction.user.id
            now = discord.utils.utcnow()

            if user_id in self.cooldowns:
                elapsed = (now - self.cooldowns[user_id]).total_seconds()
                if elapsed < 120:
                    restante = int(120 - elapsed)
                    await interaction.response.send_message(
                        f"⏳ Aguarde {restante} segundos antes de abrir outro ticket.",
                        ephemeral=True
                    )
                    return

            self.cooldowns[user_id] = now
            await self.criar_ticket(interaction)

        elif custom_id == "fechar_ticket":
            if not (is_admin or has_suporte):
                await interaction.response.send_message("❌ Você não tem permissão para fechar este ticket.", ephemeral=True)
                return
            await interaction.response.send_message("Tem certeza que deseja fechar este ticket?", view=ConfirmarFechamentoView(), ephemeral=True)

        elif custom_id == "bloquear_ticket":
            if not (is_admin or has_suporte):
                await interaction.response.send_message("❌ Você não tem permissão para bloquear este ticket.", ephemeral=True)
                return
            await self.bloquear_ticket(interaction)

    async def criar_ticket(self, interaction: discord.Interaction):
        guild = interaction.guild
        categoria = guild.get_channel(CATEGORIA_TICKET_ID)
        suporte = guild.get_role(SUPORTE_ROLE_ID)

        if not categoria or not suporte:
            await interaction.response.send_message("Erro: categoria ou cargo de suporte inválido.", ephemeral=True)
            return

        ticket_id = random.randint(1000, 9999)
        nome_usuario = interaction.user.name.lower().replace(" ", "-")
        canal_nome = f"ticket-{nome_usuario}-{interaction.user.id}-{ticket_id}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            suporte: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        canal = await guild.create_text_channel(
            name=canal_nome,
            category=categoria,
            overwrites=overwrites,
            reason="Ticket criado"
        )

        await canal.send(
            f"{interaction.user.mention}, seu ticket foi criado! Aguarde atendimento.\n"
            f"Alguém dos <@&1386848744909307904> <@&1387206715573014683> <@&1388449335188000788> <@&1269700285065072701> irá te retornar em breve.",
            view=TicketControlsView()
        )

        await interaction.response.send_message(f"✅ Seu ticket foi criado: {canal.mention}", ephemeral=True)

    async def bloquear_ticket(self, interaction: discord.Interaction):
        await interaction.channel.set_permissions(interaction.user, send_messages=False)
        await interaction.response.send_message("🔒 O ticket foi bloqueado para o autor.", ephemeral=True)

    @staticmethod
    async def salvar_log(interaction_or_ctx, autor=None):
        canal = interaction_or_ctx.channel
        mensagens = []

        async for msg in canal.history(limit=100, oldest_first=True):
            mensagens.append(f"[{msg.created_at.strftime('%Y-%m-%d %H:%M')}] {msg.author}: {msg.content}")

        conteudo = "\n".join(mensagens)
        nome_arquivo = f"{canal.name}_log.txt"
        with open(nome_arquivo, "w", encoding="utf-8") as f:
            f.write(conteudo)

        log_channel = canal.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"📄 Log do ticket `{canal.name}`",
                file=discord.File(nome_arquivo)
            )

        os.remove(nome_arquivo)

        if autor:
            try:
                embed = discord.Embed(
                    title="📪 Ticket Encerrado",
                    description=f"Seu ticket `{canal.name}` foi fechado.\nSe precisar de mais ajuda, sinta-se à vontade para abrir outro.",
                    color=discord.Color.red()
                )
                await autor.send(embed=embed)
            except discord.Forbidden:
                pass

# Função obrigatória para cogs
async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
