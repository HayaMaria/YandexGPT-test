# Scripts/TakeTheKey.py
from pathlib import Path

# путь к файлу secret.env в корне проекта
secret_path = Path(__file__).resolve().parent.parent / "secrets.env"

# читаем содержимое файла
with open(secret_path, "r") as f:
    key = f.read().strip()  # убираем лишние пробелы и переносы строк

print("Ключ из secrets.env:", key)

