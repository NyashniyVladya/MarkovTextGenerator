***MarkovTextGenerator***

[![PyPI](https://pypi.python.org/pypi/MarkovTextGenerator)]


**Генератор псевдорандомного текста, посредством цепей Маркова.**

---
**Установка:**
```
$ pip install MarkovTextGenerator
```
---
**Пример использования:**
```python
from MarkovTextGenerator.markov_text_generator import MarkovTextGenerator

my_generator = MarkovTextGenerator(2, None)

my_generator.update("some_book.txt") # Обновляем базу текстовым файлом
my_generator.update("Эта фраза добавится в выборку токенов.", fromfile=False) # Или просто текстом.
my_generator.create_dump() # Сохраняем текущую выборку, чтобы потом не загружать повторно.

print(my_generator.start_generation()) # Проверяем.
```
---
