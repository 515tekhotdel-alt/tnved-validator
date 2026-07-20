# src/data_loader.py
# Модуль для загрузки данных из Excel файлов с поддержкой part

import pandas as pd
import streamlit as st


@st.cache_data
def load_data(file_path):
    """
    Загружает данные из Excel файла.
    Возвращает DataFrame с колонками: part, раздел_ИЛ, стандарт_ИЛ, код_ТНВЭД_ИЛ
    """
    try:
        df_raw = pd.read_excel(file_path)

        # Проверяем наличие необходимых колонок
        required_cols = ['part', 'indexNumber', 'name', 'name3', 'code']
        for col in required_cols:
            if col not in df_raw.columns:
                st.error(f"❌ В файле отсутствует колонка: {col}")
                return pd.DataFrame()

        # 1. Берем ВСЕ стандарты (normDocument)
        norm_rows = df_raw[df_raw['name'] == 'normDocument']

        # 2. Берем ВСЕ коды ТНВЭД (tnvedCode)
        tnved_rows = df_raw[df_raw['name'] == 'tnvedCode']

        # Строим словарь: (part, indexNumber) → стандарт
        standards_dict = {}
        for _, row in norm_rows.iterrows():
            part = row['part']
            idx = row['indexNumber']
            std_name = row['name3']
            if pd.notna(part) and pd.notna(idx) and pd.notna(std_name):
                key = (part, idx)
                standards_dict[key] = std_name

        # Строим словарь: (part, indexNumber) → список кодов
        codes_dict = {}
        for _, row in tnved_rows.iterrows():
            part = row['part']
            idx = row['indexNumber']
            code = row['code']
            if pd.notna(part) and pd.notna(idx) and pd.notna(code):
                key = (part, idx)
                code_clean = str(code).strip()
                if key not in codes_dict:
                    codes_dict[key] = []
                codes_dict[key].append(code_clean)

        # Собираем итоговую таблицу
        result_data = []

        # Проходим по ВСЕМ стандартам
        for key, std_name in standards_dict.items():
            part, idx = key
            # Если у стандарта есть коды — добавляем каждую строку с кодом
            if key in codes_dict:
                for code in codes_dict[key]:
                    result_data.append({
                        'part': part,
                        'раздел_ИЛ': idx,
                        'стандарт_ИЛ': std_name,
                        'код_ТНВЭД_ИЛ': code
                    })
            else:
                # Если кодов нет — добавляем одну строку с пустым кодом
                result_data.append({
                    'part': part,
                    'раздел_ИЛ': idx,
                    'стандарт_ИЛ': std_name,
                    'код_ТНВЭД_ИЛ': ''  # пустой код
                })

        df_result = pd.DataFrame(result_data)

        if df_result.empty:
            st.warning("⚠️ Не удалось собрать данные. Проверьте структуру файла.")
            return pd.DataFrame()

        return df_result

    except FileNotFoundError:
        st.error(f"❌ Файл не найден: {file_path}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Ошибка при загрузке файла: {str(e)}")
        return pd.DataFrame()


def get_data_info(df):
    """
    Возвращает информацию о загруженных данных.
    """
    if df.empty:
        return {
            "rows": 0,
            "columns": [],
            "has_data": False
        }

    return {
        "rows": len(df),
        "columns": df.columns.tolist(),
        "has_data": True
    }