import os
import datetime

# === ЛОГИРОВАНИЕ ===

def log_action(guild_id, message):
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{guild_id}.log", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] {message}\n")

async def notify_owner(bot, guild_id, message):
    guild = bot.get_guild(guild_id)
    if not guild:
        return
    owner = guild.owner
    if owner:
        try:
            await owner.send(f"[Оповещение от анти-рейд бота]\n{message}")
        except:
            pass

# === АНАЛИЗ СООБЩЕНИЙ ===

def is_mass_caps(text):
    if len(text) < 10:
        return False
    cap_count = sum(1 for c in text if c.isupper())
    return cap_count / len(text) > 0.7

def is_mass_mentions(message):
    return message.mention_everyone or len(message.mentions) > 5

def is_sus_channel_creation(channel_name):
    return any(char.isdigit() for char in channel_name) or len(channel_name) < 3
