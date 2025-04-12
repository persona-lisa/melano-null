import discord
from discord.ext import commands, tasks
import json
import datetime
import asyncio
import os
from dotenv import load_dotenv
from core import log_action, notify_owner, is_mass_caps, is_mass_mentions, is_sus_channel_creation

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.guilds = True
client = commands.Bot(command_prefix="!", intents=intents)
# Загрузить переменные окружения из .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# Логирование действий
def log_action(message):
    print(f"[{datetime.datetime.now()}] {message}")

# Хранение бекапов
def save_backup(guild):
    backup_data = {
        "channels": [{"name": channel.name, "category": channel.category.name if channel.category else None} for channel in guild.channels],
        "roles": [{"name": role.name, "permissions": role.permissions.value} for role in guild.roles],
    }
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    with open(f"{backup_dir}/{guild.id}_backup.json", "w") as f:
        json.dump(backup_data, f, indent=4)

# Проверка капса
def check_caps(message):
    return any(word.isupper() for word in message.content.split())

# Проверка на флуд (повторение одинаковых сообщений)
async def check_spam(message, last_messages):
    if message.content in last_messages:
        await message.delete()
        await message.author.ban(reason="Флуд обнаружен.")
        log_action(f"Пользователь {message.author.name} забанен за флуд.")
    last_messages.append(message.content)
    if len(last_messages) > 10:  # Храним последние 10 сообщений
        last_messages.pop(0)

# Запрещаем изменение ников
@client.event
async def on_member_update(before, after):
    if before.name != after.name:
        await after.edit(nick=before.name)
        log_action(f"Попытка изменения ника от {after.name} отклонена.")

# Запрещаем массовые капс
@client.event
async def on_message(message):
    if message.author.bot:
        return

    # Проверка на капс
    if check_caps(message):
        await message.delete()
        await message.author.ban(reason="Массовые заглавные буквы (капс) обнаружены.")
        log_action(f"Пользователь {message.author.name} забанен за использование капса.")

    # Проверка на флуд
    await check_spam(message, [])

    await client.process_commands(message)

# Запрещаем изменения ролей или прав каналов
@client.event
async def on_guild_role_update(before, after):
    if before.permissions != after.permissions:
        await after.edit(permissions=before.permissions)
        log_action(f"Попытка изменения прав роли {before.name} отклонена.")

@client.event
async def on_guild_channel_update(before, after):
    if before.overwrites != after.overwrites:
        await after.edit(overwrites=before.overwrites)
        log_action(f"Попытка изменения прав канала {before.name} отклонена.")

# Включение защиты от рейдов
@client.event
async def on_member_join(member):
    # Пример сработавшего анти-рейда (например, 5 пользователей заходят за минуту)
    if len([m for m in member.guild.members if m.joined_at > datetime.datetime.now() - datetime.timedelta(minutes=1)]) > 5:
        await member.guild.set_permissions(member, send_messages=False)
        log_action(f"Рейд обнаружен, участник {member.name} заблокирован для сообщений.")
        # Логируем действия и отправляем отчет администратору
        admin = discord.utils.get(member.guild.members, id=975381517230538854)
        await admin.send(f"Рейд обнаружен: {member.name} заблокирован.")

# Авто бэкап
@tasks.loop(hours=24)
async def auto_backup():
    for guild in client.guilds:
        save_backup(guild)

# Разморозка
@client.command()
async def unfreeze(ctx):
    if ctx.author.id == 975381517230538854:
        # Реализация разморозки
        await ctx.send("Система разморожена.")
        log_action("Система разморожена.")

# Событие, которое вызывается при запуске бота
@client.event
async def on_ready():
    """Подключает бота в изначальный голосовой канал при запуске."""
    print(f'CONSOLE ➤  Бот {client.user} подключен к Discord.')

    for guild in client.guilds:
        # Убедись, что у тебя есть переменная для VOICE_CHANNEL_ID
        channel = guild.get_channel(1346190341379854412)  # Определи свой ID канала здесь
        if channel and isinstance(channel, discord.VoiceChannel):
            if not guild.voice_client:  # Проверяем, не подключен ли уже
                await channel.connect()
                print(f"CONSOLE ➤ Бот подключился к {channel.name}")

# Запуск бота
client.run(DISCORD_TOKEN)
