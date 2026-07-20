# src/config.py
# Конфигурация приложения

# Данные о лабораториях
# Данные о лабораториях
LABS = {
    "ИЛ Максвелл": {
        "file": "data/IL_Maxwell_2026_007.xlsx",
        "name": "ИЛ Максвелл"
    },
    "ИЛ УЛЦ": {
        "file": "data/ULC_003.xlsx",
        "name": "ИЛ УЛЦ"
    }
}

# Настройки Streamlit
STREAMLIT_TITLE = "Проверка ТНВЭД в ОА ИЛ"
STREAMLIT_ICON = "🔍"

# Цветовая схема для результатов
COLORS = {
    "success": "#d4edda",
    "danger": "#f8d7da",
    "missing": "#e6ccff",
    "warning": "#fff3cd",
}