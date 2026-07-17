# src/data_loader.py
# Модуль для загрузки данных из Excel файла

import pandas as pd
import streamlit as st
from src.config import DATA_FILE_PATH


@st.cache_data
def load_data():
    """
    Загружает данные из Excel файла.
    Использует кэширование Streamlit для ускорения работы.
    """
    try:
        df = pd.read_excel(DATA_FILE_PATH)
        # Очищаем названия колонок от лишних пробелов
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.error(f"❌ Файл не найден: {DATA_FILE_PATH}")
        st.info("Пожалуйста, убедитесь, что файл Excel находится в папке data/")
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