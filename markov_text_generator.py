# -*- coding: utf-8 -*-
"""
Генератор текста, по цепям Маркова.

@author: Vladya

"""

from re import compile as re_compile
from os.path import (
    abspath,
    isfile
)
from collections import deque
from random import choice
from semver import format_version

__version__ = format_version(
    major=1,
    minor=1,
    patch=0
)

class LocutorExcept(Exception):
    """
    Класс исключения модуля.
    """
    pass


class MarkovTextGenerator(object):
    """
    Базовый класс, для генерации текста.
    """

    WORD_OR_MARKS = re_compile(r"\w+|[\.\!\?…,;]+")
    ONLY_MARKS = re_compile(r"[\.\!\?…,;]+")
    END_TOKENS = re_compile(r"[\.\!\?…]+")

    def __init__(self, chain_order=2, *file_paths):
        """
        :chain_order: Количество звеньев цепи, для принятия решения о следующем.
        :file_paths: Пути к текстовым файлам, для обучения модели.
        """

        if chain_order < 1:
            raise LocutorExcept(
                "Цепь не может быть {0}-порядка.".format(chain_order)
            )
        self.chain_order = chain_order
        self.tokens_array = ()
        self.base_dict = {}
        self.start_arrays = []

        for _path in frozenset(filter(isfile, map(abspath, file_paths))):
            self.update(_path)

    def start_generation(self, *start_words):
        """
        Генерирует предложение.
        :start_words: Попытаться начать предложение с этих слов.
        """
        text_array = list(self.get_start_array(*start_words))
        key_array = deque(text_array, maxlen=self.chain_order)
        while True:
            tuple_key = tuple(key_array)
            next_token = choice(self.base_dict[tuple_key])
            if next_token in ("$", "^"):
                break
            text_array.append(next_token)
            key_array.append(next_token)
        out_text = ""
        for token in text_array:
            if token in ("$", "^"):
                continue
            if not self.ONLY_MARKS.search(token):
                out_text += " "
            out_text += token

        return out_text.strip().capitalize()


    def get_start_array(self, *start_words):
        """
        Генерирует начало предложения.
        :start_words: Попытаться начать предложение с этих слов.
        """
        if not start_words:
            return choice(self.start_arrays)
        candidats = {}
        for tokens in self.start_arrays:
            candidats[tokens] = 0
            for word in start_words:
                word = word.strip().lower()
                for token in self.WORD_OR_MARKS.finditer(word):
                    token = token.group()
                    candidats[tokens] += tokens.count(token)
        return max(candidats.items(), key=lambda x: x[-1])[0]

    def create_base(self):
        """
        Метод создаёт базовый словарь, на основе массива токенов.
        Вызывается из метода обновления.
        """
        self.base_dict = {}
        self.start_arrays = []
        for tokens, word in self.chain_generator():
            if tokens not in self.base_dict.keys():
                self.base_dict[tokens] = []
            self.base_dict[tokens].append(word)
            if tokens[0] == "^": # Первые ключи, для начала генерации.
                self.start_arrays.append(tokens)

    def chain_generator(self):
        """
        Возвращает генератор, формата:
            (("токен", ...), "вариант")
            Где количество токенов определяет переменная объекта chain_order.
        """
        n_chain = self.chain_order
        if n_chain < 1:
            raise LocutorExcept(
                "Цепь не может быть {0}-порядка.".format(n_chain)
            )
        n_chain += 1 # Последнее значение - результат возврата.
        changing_array = deque(maxlen=n_chain)
        for token in self.tokens_array:
            changing_array.append(token)
            if len(changing_array) < n_chain:
                continue # Массив ещё неполон.
            yield (tuple(changing_array)[:-1], changing_array[-1])

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
            raise LocutorExcept("Передан не текст.")
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
            raise LocutorExcept("Передан не файл.")
        with open(file_path, "rb") as txt_file:
            for line in txt_file:
                try:
                    text = line.decode("utf-8").strip()
                except UnicodeDecodeError:
                    continue
                if not text:
                    continue
                for token in self._parse_from_text(text):
                    yield token
