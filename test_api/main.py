import sys
from pathlib import Path

# путь к папке scripts
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))
from take_the_key import get_key

key = None
def key_is_active(key):
    """
    Здесь проверяем активен ли ключ.
    """
    return bool(key)

def take_the_words():
    """
    Здесь берём слова у пользователя, и возвращаем их в виде списка.
    """
    return list(words)

def main(words_list):
    global key

    #проверяем, активен ли старый ключ
    if not key_is_active(key):
        key = get_key()  # получаем новый ключ только если нужно

    """
    Здесь запросы к нейросети. 
    И возможно формирование таблицы.
    """



if __name__ == "__main__":
    words = ["apple", "banana", "orange"]
    main(words)