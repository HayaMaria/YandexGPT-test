from pathlib import Path
import os
import requests
from take_the_key import get_key

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
modelUri = "gpt://b1gd0j1qrlj8e90tbbfp/yandexgpt"

failed_words = []


def take_the_words():
    # Путь к файлу words.txt
    folder = os.getenv("KEY_FOLDER")
    base_path = folder or os.path.expanduser("~")
    words_path = Path(base_path) / "words.txt"

    words_list = []

    with words_path.open("r", encoding="utf-8") as f:  # Читаем файл words.txt.
        for line in f:
            line = line.strip()  # Убираем пробелы и переносы строк.
            if not line:         # Пропускаем пустые строки.
                continue

            words_in_line = line.split(",")     # Разделяем по запятым.
            for word in words_in_line:
                word = word.strip()             # Убираем пробелы вокруг слова.
                if word:                        # Пропускаем пустые.
                    words_list.append(word)     # Добавляем слово в список.

    return words_list


def handle_fail(word, reason):
    global failed_words
    failed_words.append(word)
    print(f"Слово {word}: {reason}.")
    return


def request_to_neural_network(words_list):

    key_for_neural_network = get_key()

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

        # TODO: упростить условную часть кода для лучшей читаемости (слишком громоздко и запутанно)
        if response.status_code == 200:
            answer = response.json()
            alternatives = answer.get("result", {}).get("alternatives", [])
            if len(alternatives) > 0:
                result = alternatives[0].get("message", {}).get("text", None)
                if result is None:
                    handle_fail(word, "некорректный ответ")
                    continue
            else:
                handle_fail(word, "некорректный ответ")
                continue

            parts = result.split("-")
            if len(parts) == 2:
                transcription = parts[0].strip()
                translation = parts[1].strip()
                table.append([word, transcription, translation])
            else:
                handle_fail(word, "неверный формат")
        else:
            handle_fail(word, response.status_code)
            continue

    return table


def writing_to_files(table, failed_word):
    """Зпись table в файл table_words.txt.
       Подсчет failed_words и запись о их количесве в файл table_words.txt.
       Запись failed_words в файл failed_words.txt."""
    return


if __name__ == "__main__":
    words = ["apple", "banana", "orange"]
    table_for_test = request_to_neural_network(words)
    print(table_for_test)
