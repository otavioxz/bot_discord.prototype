import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import json
import os

CANAL_ID = 1326717849594630255  # ID do canal
HORARIO_FILE = "horario.json"
VIDEO_ARQUIVO = "acorda.mp4"

class MensagemHoraria(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.enviar_mensagem_todo_hora())

    def obter_proxima_execucao(self):
        if os.path.exists(HORARIO_FILE):
            try:
                with open(HORARIO_FILE, "r") as f:
                    dados = json.load(f)
                    proxima_str = dados.get("proxima_execucao")
                    return datetime.strptime(proxima_str, "%Y-%m-%d %H:%M:%S")
            except:
                pass

        agora = datetime.now()
        proxima = (agora + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
        self.salvar_proxima_execucao(proxima)
        return proxima

    def salvar_proxima_execucao(self, dt):
        with open(HORARIO_FILE, "w") as f:
            json.dump({"proxima_execucao": dt.strftime("%Y-%m-%d %H:%M:%S")}, f)

    async def enviar_mensagem_todo_hora(self):
        await self.bot.wait_until_ready()
        canal = self.bot.get_channel(CANAL_ID)

        while not self.bot.is_closed():
            proxima = self.obter_proxima_execucao()
            agora = datetime.now()

            if proxima <= agora:
                proxima = (agora + timedelta(hours=3)).replace(minute=0, second=0, microsecond=0)
                self.salvar_proxima_execucao(proxima)

            espera = (proxima - agora).total_seconds()
            print(f"⏳ Próxima mensagem às {proxima.strftime('%H:%M:%S')} ({int(espera)} segundos)")
            await asyncio.sleep(espera)

            if canal:
                try:
                    with open(VIDEO_ARQUIVO, "rb") as video:
                        await canal.send(
                            content="ACORDAAA CARAAA!! 😱😱🫣🔥❗ <@&1387312608008339457>",
                            file=discord.File(video, filename="acorda.mp4")
                        )
                except FileNotFoundError:
                    await canal.send("❌ Erro: vídeo 'acorda.mp4' não encontrado no diretório do bot.")
                proxima = proxima + timedelta(hours=3)
                self.salvar_proxima_execucao(proxima)

async def setup(bot):
    await bot.add_cog(MensagemHoraria(bot))
