import json
import datetime
import os

# Функция для сохранения бекапов
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

# Функция для загрузки бекапа
def load_backup(guild):
    backup_file = f"backups/{guild.id}_backup.json"
    if os.path.exists(backup_file):
        with open(backup_file, "r") as f:
            return json.load(f)
    return None
