# src/clean_utils.py
# Модуль для очистки пользовательского ввода

import re
import pandas as pd


def clean_standard(std_text):
    """
    Очистка стандарта, введенного пользователем:
    - Убирает всё после скобок
    - Убирает всё после последнего дефиса (год)
    - Убирает лишние пробелы
    """
    if pd.isna(std_text) or std_text == '':
        return ''

    std = str(std_text)

    # Убираем всё после скобок (круглых, квадратных, фигурных)
    bracket_pattern = r'[\(\[\{].*$'
    std = re.sub(bracket_pattern, '', std)

    # Убираем всё после последнего дефиса (—, –, -) — это год
    last_dash = max(std.rfind('-'), std.rfind('—'), std.rfind('–'))
    if last_dash != -1:
        std = std[:last_dash].rstrip()

    # Убираем лишние пробелы
    std = re.sub(r'\s+', ' ', std).strip()

    return std


def clean_tnved(tnved_code):
    """
    Очистка кода ТНВЭД, введенного пользователем:
    - Удаляет все пробелы
    - Оставляет только цифры
    """
    if pd.isna(tnved_code) or tnved_code == '':
        return ''

    # Удаляем все пробелы
    code_clean = re.sub(r'\s+', '', str(tnved_code))

    # Проверка: только цифры
    if not code_clean.isdigit():
        code_clean = re.sub(r'[^\d]', '', code_clean)

    return code_clean


def parse_multiple_values(text, separators=[',', ';', '|', '\n']):
    """
    Парсинг значений с различными разделителями.
    Возвращает список уникальных значений в порядке появления.
    """
    if not text or not text.strip():
        return []

    # Заменяем все разделители на \n
    result_text = text
    for sep in separators:
        result_text = result_text.replace(sep, '\n')

    # Разбиваем по \n и очищаем
    values = [v.strip() for v in result_text.split('\n') if v.strip()]

    # Удаляем дубликаты, сохраняя порядок
    seen = set()
    unique_values = []
    for v in values:
        if v not in seen:
            seen.add(v)
            unique_values.append(v)

    return unique_values