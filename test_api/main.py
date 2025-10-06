import sys
from pathlib import Path


from .take_the_key import get_key

key_for_neural_network = None
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

def request_to_neural_network(words_list):
    global key_for_neural_network

    #проверяем, активен ли старый ключ
    if not key_is_active(key_for_neural_network):
        key_for_neural_network = get_key()  # получаем новый ключ только если нужно

    """
    Здесь запросы к нейросети. 
    И возможно формирование таблицы.
    """



if __name__ == "__main__":
    words = ["apple", "banana", "orange"]
    request_to_neural_network(words)