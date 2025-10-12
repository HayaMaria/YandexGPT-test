from pathlib import Path
import requests
import json
import jwt
import time

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
modelUri = "gpt://b1gd0j1qrlj8e90tbbfp/yandexgpt"

def get_key():
    # путь к файлам secret. и token_cache. в корне проекта
    secret_path = Path(__file__).resolve().parent.parent / "secrets.env"
    token_cache_path = Path(__file__).resolve().parent.parent / "token_cache.txt"

    if not token_cache_path.exists(): # проверяем существует ли файл
        token_cache_path.touch()      # если нет - создаём пустой файл

    # читаем содержимое файла token_cache.
    with open(token_cache_path, "r") as f:
        cache = json.load(f)

    iam_token = cache.get("iamToken") # токен
    expires_At = cache.get("expiresAt") # срок действия

    # тестовый запрос к нейросети, позже нужно заменить проверку на expires_At!!!
    headers = {
        "Authorization": f"Bearer {iam_token}",
        "Content-Type": "application/json"
    }

    prompt = "Скажи привет."

    data = {
        "modelUri": modelUri,
        "completionOptions": {
            "temperature": 0.3,
            "maxTokens": 100
        },
        "messages": [{"role": "user", "text": prompt}]
    }

    response = requests.post(
        url=url,
        headers=headers,
        json=data
    )

    if response.status_code == 200: # если запрос успешен - старый токен еще активен, возвращаем его
        return iam_token

    # если старый токен неактивен, создаем новый
    # читаем содержимое файла secrets.
    with open(secret_path, "r") as f:
        service_key = json.load(f)

    now = int(time.time())
    payload = {
        "aud": "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        "iss": service_key["service_account_id"],
        "iat": now,
        "exp": now + 360  # токен живёт 6 минут
        }

    jwt_token = jwt.encode(
        payload,
        service_key["private_key"],
        algorithm=service_key["key_algorithm"]
    )

    response = requests.post(
        "https://iam.api.cloud.yandex.net/iam/v1/tokens",
        json={"jwt": jwt_token}
    )

    iam_token = response.json()["iamToken"]
    expires_At = response.json()["expiresAt"]
    cashe = {
        "iam_token": iam_token,
        "expiresAt": expires_At
        }

    with open(token_cache_path, "w") as f:
        json.dump(cashe, f)

    return iam_token


if __name__ == "__main__":
    #для проверок
    print("Токен: ", get_key())


