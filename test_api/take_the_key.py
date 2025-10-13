from pathlib import Path
from datetime import datetime
import requests
import json
import jwt
import time


def get_key():
    # Путь к файлам secret.json и token_cache.txt в корне проекта
    secret_path = Path(__file__).resolve().parent.parent / "secrets.json"
    token_cache_path = Path(__file__).resolve().parent.parent / "token_cache.txt"

    if not token_cache_path.exists():  # Проверяем, существует ли файл
        token_cache_path.touch()       # Если файла нет - создаём пустой

    # Проверяем содержимое файла token_cache
    try:
        with open(token_cache_path, "r") as f:
            cache = json.load(f)
    except json.JSONDecodeError:
        cache = {"iam_token": "",  # Заглушка
                 "expiresAt": "1970-01-01T00:00:00Z"
                 }

    iam_token = cache.get("iam_token")  # токен
    expiresAt = cache.get("expiresAt")  # срок действия

    # Буффер, чтобы успеть использовать токен до истечения срока
    buffer_seconds = 10
    # Переводим expiresAt в формат UNIX-времени
    expiresAt_time = int(datetime.fromisoformat(expiresAt.replace("Z", "+00:00")).timestamp())

    now = int(time.time())

    if now < expiresAt_time - buffer_seconds:  # Проверяем, активен ли старый токен
        return iam_token

    # Если старый токен неактивен - создаем новый

    with open(secret_path, "r") as f:  # Читаем содержимое файла secrets
        service_key = json.load(f)

    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_key["service_account_id"],
        "iat": now,
        "exp": now + 360  # Время жизни токена
        }

    jwt_token = jwt.encode(
        payload,
        service_key["private_key"],
        algorithm=service_key["key_algorithm"]
    )

    response = requests.post(  # Запрашиваем новый IAM-токен
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"jwt": jwt_token}
    )

    if response.status_code != 200:  # Проверяем, был ли запрос успешен
        raise RuntimeError(f"Ошибка запроса: {response.status_code}, {response.text}")

    # Извлекаем токен и срок его действия
    iam_token = response.json()["iamToken"]
    expiresAt = response.json()["expiresAt"]
    cache = {
        "iam_token": iam_token,
        "expiresAt": expiresAt
        }

    with open(token_cache_path, "w") as f:  # Сохраняем токен и срок его действия в файл
        json.dump(cache, f)

    return iam_token


if __name__ == "__main__":  # Тестовый запуск функции
    print("Токен: ", get_key())
