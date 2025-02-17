from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Obtener el token de Discord desde las variables de entorno
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

# Verifica que el token se cargó correctamente
print(DISCORD_TOKEN)  # Esto imprimirá el token en la consola para que puedas verificarlo

import discord
from discord.ext import commands
from collections import defaultdict
import asyncio

# Configurar intents
intents = discord.Intents.default()
intents.message_content = True  # Habilitar contenido de los mensajes
intents.members = True  # Habilitar eventos de miembros
intents.voice_states = True  # Habilitar eventos de voz

# Crear el bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Diccionario para almacenar el tiempo de los usuarios
user_activity = defaultdict(int)  # {user_id: tiempo en segundos}

# Variable para guardar el momento de entrada
user_join_time = {}

# ID del canal de voz que quieres monitorear
voice_channel_id = 1263200163640381531  # Cambia esto por el ID de tu canal de voz

@bot.event
async def on_ready():
    print(f'{bot.user} está conectado a Discord.')

@bot.event
async def on_voice_state_update(member, before, after):
    if after.channel and after.channel.id == voice_channel_id:  # Cuando el usuario entra a tu canal de voz
        if member.id not in user_join_time:
            user_join_time[member.id] = asyncio.get_event_loop().time()  # Marca el momento en que entra
        print(f'{member.name} se ha unido al canal de voz.')
    elif before.channel and before.channel.id == voice_channel_id:  # Cuando el usuario sale del canal de voz
        if member.id in user_join_time:
            join_time = user_join_time.pop(member.id)  # Obtén la hora de entrada
            active_time = asyncio.get_event_loop().time() - join_time  # Calcula el tiempo activo
            user_activity[member.id] += active_time  # Suma el tiempo al total de actividad
        print(f'{member.name} ha salido del canal de voz.')

@bot.command()
async def leaderboard(ctx):
    # Crear una lista ordenada de usuarios por su tiempo de actividad
    leaderboard = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
    
    # Mostrar los primeros 10 usuarios más activos
    leaderboard_message = "Leaderboard de Actividad en EVENTO:\n"
    for idx, (user_id, activity_time) in enumerate(leaderboard[:10], 1):
        user = await bot.fetch_user(user_id)
        leaderboard_message += f"{idx}. {user.name} - {round(activity_time, 2)} segundos\n"
    
    await ctx.send(leaderboard_message)

# Comando para ver estadísticas de un usuario
@bot.command()
async def estadisticas(ctx, member: discord.Member = None):
    # Si no se especifica un usuario, mostrar las estadísticas del que ejecuta el comando
    if member is None:
        member = ctx.author

    # Obtener el tiempo de actividad del usuario
    activity_time = user_activity.get(member.id, 0)

    # Enviar el mensaje con las estadísticas
    await ctx.send(f"**Estadísticas de {member.name}:**\nTiempo total en voz: {round(activity_time, 2)} segundos")

# Ejecutar el bot
bot.run(DISCORD_TOKEN)  # Reemplaza 'tu_token_aqui' con tu token real