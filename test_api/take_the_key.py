from pathlib import Path

def get_key():
    #путь к файлу secret.env в корне проекта
    secret_path = Path(__file__).resolve().parent.parent / "secrets.env"

    #читаем содержимое файла
    with open(secret_path, "r") as f:
        key = f.read().strip()  # убираем лишние пробелы и переносы строк

    return key

if __name__ == "__main__":
    #для проверок
    print("Ключ из secrets.env: ", get_key())


