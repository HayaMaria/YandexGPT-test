from pathlib import Path
from datetime import datetime
import requests
import json
import jwt
import time
import os


def parse_expires_at(ts: str) -> datetime:  # Приводит строку с датой к формату, который принимает datetime.
    ts = ts.replace("Z", "+00:00")  # Z и +00:00 — одинаковый часовой пояс (UTC).
    # datetime не всегда понимает Z, поэтому заменяем.
    if "." in ts:  # Проверяем, есть ли в строке дробная часть секунды.
        head, tail = ts.split(".", 1)  # Делим строку на две части: до точки и после.
        # head — дата, часы, минуты, секунды; tail — дробные секунды + часовой пояс.
        if "+" in tail:  # Если есть знак +, значит есть часовой пояс.
            frac, tz = tail.split("+", 1)  # Отделяем дробную часть и часовой пояс.
            tz = "+" + tz
        elif "-" in tail:  # То же самое, если часовой пояс отрицательный.
            frac, tz = tail.split("-", 1)
            tz = "-" + tz
        else:  # Если часового пояса нет вообще.
            frac, tz = tail, ""
        # Делаем дробную часть ровно 6 знаков: если меньше — дополняем нулями, если больше — обрезаем.
        frac = (frac + "000000")[:6]
        ts = head + "." + frac + tz  # Собираем строку обратно.
    return datetime.fromisoformat(ts)  # Преобразуем строку в datetime-объект.


def get_key():
    # Путь к файлам secret.json и token_cache.
    folder = os.getenv("KEY_FOLDER")
    base_path = folder or os.path.expanduser("~")
    token_cache_path = Path(base_path) / "token_cache.txt"
    secret_path = Path(base_path) / "secrets.json"

    if not token_cache_path.exists():  # Проверяем, существует ли файл.
        token_cache_path.touch()  # Если файла нет - создаём пустой.

    # Проверяем содержимое файла token_cache.
    try:
        with token_cache_path.open("r", encoding="utf-8") as f:
            cache = json.load(f)
    except json.JSONDecodeError:
        cache = {"iam_token": "",  # заглушка
                 "expiresAt": "1970-01-01T00:00:00Z"
                 }

    iam_token = cache.get("iam_token")  # токен
    expiresAt = cache.get("expiresAt")  # срок действия

    # Буфер, чтобы успеть использовать токен до истечения срока.
    buffer_seconds = 10
    # Переводим expiresAt в формат UNIX-времени.
    expiresAt_time = int(parse_expires_at(expiresAt).timestamp())

    now = int(time.time())

    if now < expiresAt_time - buffer_seconds:  # Проверяем, активен ли старый токен.
        return iam_token

    # Если старый токен неактивен - создаем новый.

    with secret_path.open("r", encoding="utf-8") as f:  # Читаем содержимое файла secrets.
        service_key = json.load(f)

    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_key["service_account_id"],
        "iat": now,
        "exp": now + 3600  # Время жизни токена.
        }

    headers = {
        "kid": service_key["id"]
    }

    jwt_token = jwt.encode(
        payload,
        service_key["private_key"],
        algorithm="PS256",  # Единственный алгоритм, который поддерживает
        headers=headers     # ЯндексCloud при подписи JWT для получения IAM токена.
    )

    response = requests.post(  # Запрашиваем новый IAM-токен.
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"jwt": jwt_token}
    )

    if response.status_code != 200:  # Проверяем, был ли запрос успешен.
        raise RuntimeError(f"Ошибка запроса: {response.status_code}, {response.text}")

    # Извлекаем токен и срок его действия.
    iam_token = response.json()["iamToken"]
    expiresAt = response.json()["expiresAt"]
    cache = {
        "iam_token": iam_token,
        "expiresAt": expiresAt
        }

    with token_cache_path.open("w", encoding="utf-8") as f:  # Сохраняем токен и срок его действия в файл
        json.dump(cache, f)

    return iam_token


if __name__ == "__main__":  # Тестовый запуск функции.
    print("Токен: ", get_key())
