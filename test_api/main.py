import sys
from pathlib import Path

import requests

from .take_the_key import get_key

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
modelUri = "gpt://b1gd0j1qrlj8e90tbbfp/yandexgpt"
key_for_neural_network = None

def take_the_words():
    """
    Здесь берём слова у пользователя, и возвращаем их в виде списка.
    """
    return list(words)

def request_to_neural_network(words_list):










    headers = {
        "Authorization": f"Bearer {key_for_neural_network}",
        "Content-Type": "application/json"
    }

    table = []

    for word in words_list:
        prompt = f"Дай транскрипцию с ударением и перевод слова {word}. Формат ТРАНСКРИПЦИЯ - ПЕРЕВОД"
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

        if response.status_code == 200:
            answer = response.json()
            alternatives = answer.get("result", {}).get("alternatives", [])
            if len(alternatives) > 0:
                result = alternatives[0].get("message", {}).get("text", None)
                if result == None:
                    print(f"Слово {word}: неккоректный ответ.")
                    continue
            else:
                print(f"Слово {word}: неккоректный ответ.")
                continue

            #result = answer["result"]["alternatives"][0]["message"]["text"]

            parts = result.split("-")
            if len(parts) == 2:
                transcription = parts[0].strip()
                translation = parts[1].strip()
                table.append([word, transcription, translation])
            else:
                print(f"Слово {word} неверный формат.")
        else:
            print(f"Ошибка: {response.status_code}")
            continue


    return table



if __name__ == "__main__":
    words = ["apple", "banana", "orange"]
    request_to_neural_network(words)