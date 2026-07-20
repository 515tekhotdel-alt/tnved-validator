# src/config.py
# Конфигурация приложения

# Данные о лабораториях
LABS = {
    "ИЛ Максвелл": {
        "file": "data/ИЛ Максвелл 2026 007 для кодов.xlsx",
        "name": "ИЛ Максвелл"
    },
    "ИЛ УЛЦ": {
        "file": "data/УЛЦ АОА + РОА 20-07-26 только коды 003.xlsx",
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