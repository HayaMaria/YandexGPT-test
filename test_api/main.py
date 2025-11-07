from pathlib import Path
import os
import requests
from test_api.take_the_key import get_key
import csv

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

folder = os.getenv("KEY_FOLDER")
PATH_TO_FILES = folder or os.path.expanduser("~")

failed_words = []


def take_the_words():
    words_path = Path(PATH_TO_FILES) / "words.txt"

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


def parse_response(word, response):
    # Парсит ответ от API для одного слова.
    # Возвращает [transcription, translation] или None при ошибке.

    if response.status_code != 200:
        handle_fail(word, response.status_code)
        return None

    try:
        answer = response.json()  # Превращаем ответ сервера в словарь Python.
        alternatives = answer.get("result", {}).get("alternatives", [])
        # result - ключ в словаре answer, его значение - словарь.
        # alternatives - ключ в словаре result, его значение список вариантов ответа.
    except Exception as e:  # На случай, если ответ не в JSON-формате.
        handle_fail(word, f"ошибка JSON: {e}")
        return None

    if not alternatives:
        handle_fail(word, "некорректный ответ")
        return None

    result = alternatives[0].get("message", {}).get("text")
    # Берём первый элемент списка alternatives - словарь.
    # message - ключ в словаре alternatives[0], его значение - словарь.
    # text - ключ в словаре message, его значение - нужный нам ответ от нейросети.

    if not result:
        handle_fail(word, "некорректный ответ")
        return None

    parts = result.split("!", 1)
    if len(parts) == 2:
        parts[0] = parts[0].strip()
        parts[1] = parts[1].strip()
    else:
        handle_fail(word, "неверный формат")
        return None

    return parts


def request_to_neural_network(words_list):

    key_for_neural_network = get_key()

    ID_folder_path = Path(PATH_TO_FILES) / "ID_folder.txt"
    with ID_folder_path.open("r", encoding="utf-8") as y:
        ID_folder = y.read()
        modelUri = f"gpt://{ID_folder}/yandexgpt"

    headers = {
        "Authorization": f"Bearer {key_for_neural_network}",
        "Content-Type": "application/json"
    }

    table = []

    for word in words_list:
        prompt = f"Дай транскрипцию русскими буквами с ударением и перевод слова {word}. Формат: транскрипция ! перевод"
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

        parsed = parse_response(word, response)
        if parsed:
            table.append([word, *parsed])

    return table


def writing_to_files(table, failed_word):
    if not table:
        raise ValueError("Таблица пуста.")

    table_words_path = Path(PATH_TO_FILES) / "table_words.tsv"

    if not table_words_path.exists():  # Проверяем, существует ли файл.
        table_words_path.touch()  # Если файла нет - создаём пустой.

    error_count = len(failed_word)
    error_line = f"Количество ошибок: {error_count}"

    # Записываем в TSV.
    with table_words_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter="\t")  # Табуляция как разделитель.
        writer.writerow(["Слово", "Транскрипция", "Перевод"])
        writer.writerows(table)
        writer.writerow([error_line])

    if error_count > 0:
        failed_words_path = Path(PATH_TO_FILES) / "failed_words.txt"
        if not failed_words_path.exists():  # Проверяем, существует ли файл.
            failed_words_path.touch()  # Если файла нет - создаём пустой.
        with failed_words_path.open("a", encoding="utf-8") as f:
            for word in failed_word:
                f.write(word + "\n")

    return print("Программа завершена успешно. Проверьте результат в файле table_words.tsv.")


if __name__ == "__main__":
    words_for_test = take_the_words()
    table_for_test = request_to_neural_network(words_for_test)
    writing_to_files(table_for_test, failed_words)
