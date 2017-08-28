# -*- coding: utf-8 -*-
"""
Генератор текста, по цепям Маркова.

@author: Vladya

"""

import json
from re import compile as re_compile
from collections import deque
from os import makedirs
from os.path import (
    abspath,
    isfile,
    isdir,
    expanduser,
    join as os_join
)
from random import (
    choice,
    choices
)
from semver import format_version

__version__ = format_version(
    major=1,
    minor=3,
    patch=3
)

class MarkovTextExcept(Exception):
    """
    Класс исключения модуля.
    """
    pass


class MarkovTextGenerator(object):
    """
    Базовый класс, для генерации текста.
    """

    WORD_OR_MARKS = re_compile(r"\w+|[\.\!\?…,;:]+")
    ONLY_WORDS = re_compile(r"\w+")
    END_TOKENS = re_compile(r"[\.\!\?…]+")

    def __init__(self, chain_order=2, vk_object=None, *file_paths):
        """
        :chain_order: Количество звеньев цепи, для принятия решения о следующем.
        :vk_object: Объект класса Владя-бота, для интеграции. Не обязателен.
        :file_paths: Пути к текстовым файлам, для обучения модели.
        """

        if chain_order < 1:
            raise MarkovTextExcept(
                "Цепь не может быть {0}-порядка.".format(chain_order)
            )
        self.chain_order = chain_order
        self.tokens_array = ()
        self.base_dict = {}
        self.start_arrays = ()
        self.vk_object = vk_object
        self.vocabulars = {}
        self.temp_folder = expanduser("~\\textGeneratorTemp")
        if not isdir(self.temp_folder):
            makedirs(self.temp_folder)

        for _path in frozenset(filter(isfile, map(abspath, file_paths))):
            self.update(_path)

    def start_generation(self, *start_words):
        """
        Генерирует предложение.
        :start_words: Попытаться начать предложение с этих слов.
        """
        if not self.base_dict:
            raise MarkovTextExcept("База данных пуста.")
        text_array = list(self.get_start_array(*start_words))
        key_array = deque(text_array, maxlen=self.chain_order)
        while True:
            tuple_key = tuple(key_array)
            next_token = choice(self.base_dict[tuple_key])
            if next_token in "$^":
                break
            text_array.append(next_token)
            key_array.append(next_token)
        out_text = ""
        for token in text_array:
            if token in "$^":
                continue
            if self.ONLY_WORDS.search(token):
                out_text += " "
            out_text += token

        return out_text.strip().capitalize()

    def get_start_array(self, *start_words):
        """
        Генерирует начало предложения.
        :start_words: Попытаться начать предложение с этих слов.
        """
        if not self.start_arrays:
            raise MarkovTextExcept("Не с чего начинать генерацию.")
        if not start_words:
            return choice(self.start_arrays)
        _weights = []
        for tokens in self.start_arrays:
            weight = 0
            for word in start_words:
                word = word.strip().lower()
                for token in self.ONLY_WORDS.finditer(word):
                    token = token.group()
                    if token in tokens:
                        weight += 1
            _weights.append(weight)
        if not tuple(filter(bool, _weights)):
            return choice(self.start_arrays)
        return choices(self.start_arrays, weights=_weights, k=1)[0]

    def create_base(self):
        """
        Метод создаёт базовый словарь, на основе массива токенов.
        Вызывается из метода обновления.
        """
        self.base_dict = {}
        _start_arrays = []
        for tokens, word in self.chain_generator():
            if tokens not in self.base_dict.keys():
                self.base_dict[tokens] = []
            self.base_dict[tokens].append(word)
            if tokens[0] == "^": # Первые ключи, для начала генерации.
                _start_arrays.append(tokens)
        self.start_arrays = tuple(_start_arrays)

    def chain_generator(self):
        """
        Возвращает генератор, формата:
            (("токен", ...), "вариант")
            Где количество токенов определяет переменная объекта chain_order.
        """
        n_chain = self.chain_order
        if n_chain < 1:
            raise MarkovTextExcept(
                "Цепь не может быть {0}-порядка.".format(n_chain)
            )
        n_chain += 1 # Последнее значение - результат возврата.
        changing_array = deque(maxlen=n_chain)
        for token in self.tokens_array:
            changing_array.append(token)
            if len(changing_array) < n_chain:
                continue # Массив ещё неполон.
            yield (tuple(changing_array)[:-1], changing_array[-1])

    def set_vocabulary(self, peer_id, from_dialogue=None, update=False):
        """
        Получает вокабулар из функции get_vocabulary и делает его активным.
        """

        self.tokens_array = self.get_vocabulary(
            peer_id,
            from_dialogue,
            update
        )
        self.create_base()

    def create_dump(self, name=None):
        """
        Сохраняет текущую базу на жёсткий диск.
        :name: Имя файла, без расширения.
        """
        name = name or "vocabularDump"
        dump_file = os_join(
            self.temp_folder,
            "{0}.json".format(name)
        )
        with open(dump_file, "w", encoding="utf-8") as js_file:
            json.dump(self.tokens_array, js_file, ensure_ascii=False)

    def load_dump(self, name=None):
        """
        Загружает базу с жёсткого диска.
        Текущая база заменяется.
        :name: Имя файла, без расширения.

        AssertionError, если файла не существует.
        """
        name = name or "vocabularDump"
        dump_file = os_join(
            self.temp_folder,
            "{0}.json".format(name)
        )
        assert isfile(dump_file)
        with open(dump_file, "rb") as js_file:
            self.tokens_array = tuple(json.load(js_file))
        self.create_base()


    def get_vocabulary(self, peer_id, from_dialogue=None, update=False):
        """
        Возвращает запас слов, на основе переписок ВК.
        Для имитации речи конкретного человека.
        Работает только с импортом объекта "Владя-бота".

        :peer_id: id, или имя страницы человека, речь которого имитируем.
        :from_dialogue:
            Из какого диалога/конфы брать переписку.
            По умолчанию - переписка текущего профиля с человеком.
        """
        if not self.vk_object:
            raise MarkovTextExcept("Объект бота не задан.")
        if not isinstance(from_dialogue, (int, type(None))):
            raise MarkovTextExcept("Передан неверный тип данных.")
        user = self.vk_object.check_id(peer_id)
        user_id = user["id"]
        if not from_dialogue:
            from_dialogue = user_id
        json_name = "{0}_{1}".format(user_id, from_dialogue)
        json_file = os_join(
            self.temp_folder,
            "{0}.json".format(json_name)
        )
        if not update:
            if json_name in self.vocabulars.keys():
                return self.vocabulars[json_name]
            if isfile(json_file):
                with open(json_file, "rb") as js_file:
                    self.vocabulars[json_name] = tuple(json.load(js_file))
                return self.vocabulars[json_name]

        all_message_txt = " ".join(
            self.vk_object.get_all_messages_from_id(from_dialogue, user_id)
        )
        _tokens_array = tuple(self._parse_from_text(all_message_txt))
        with open(json_file, "w", encoding="utf-8") as js_file:
            json.dump(_tokens_array, js_file, ensure_ascii=False)
        self.vocabulars[json_name] = _tokens_array
        return _tokens_array

    def update(self, data, fromfile=True):
        """
        Принимает текст, или путь к файлу и обновляет существующую базу.
        """
        func = (self._parse_from_file if fromfile else self._parse_from_text)
        self.tokens_array += tuple(func(data))
        self.create_base()

    def _parse_from_text(self, text):
        """
        Возвращает генератор токенов, из текста.
        """
        if not isinstance(text, str):
            raise MarkovTextExcept("Передан не текст.")
        text = text.strip().lower()
        need_start_token = True
        for token in self.WORD_OR_MARKS.finditer(text):
            token = token.group()
            if need_start_token:
                need_start_token = False
                yield "^"
            yield token
            if self.END_TOKENS.search(token):
                need_start_token = True
                yield "$"


    def _parse_from_file(self, file_path):
        """
        см. описание _parse_from_text.
        Только на вход подаётся не текст, а путь к файлу.
        """
        file_path = abspath(file_path)
        if not isfile(file_path):
            raise MarkovTextExcept("Передан не файл.")
        with open(file_path, "rb") as txt_file:
            for line in txt_file:
                try:
                    text = line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue
                if not text:
                    continue
                yield from self._parse_from_text(text)
