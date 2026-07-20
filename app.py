import streamlit as st
import pandas as pd
import re
import os
from src.data_loader import load_data, get_data_info
from src.config import LABS

# Настройка страницы
st.set_page_config(
    page_title="Проверка ТНВЭД в ОА ИЛ",
    page_icon="🔍",
    layout="wide"
)

# Инициализация переменной для результатов
if 'results' not in st.session_state:
    st.session_state.results = []

# Инициализация переменных для полей ввода
if 'tnved_input' not in st.session_state:
    st.session_state.tnved_input = ""
if 'standards_input' not in st.session_state:
    st.session_state.standards_input = ""

# --- БОКОВАЯ ПАНЕЛЬ (определяем lab_name ПЕРВЫМ) ---
with st.sidebar:
    # Оформленный заголовок выбора ИЛ
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #ff8a5c 100%);
                padding: 12px 16px;
                border-radius: 10px;
                margin-bottom: 16px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <span style="color: white;
                     font-size: 16px;
                     font-weight: 700;
                     letter-spacing: 0.5px;
                     text-shadow: 0 1px 4px rgba(0,0,0,0.15);">
            🏢 Выберите ИЛ
        </span>
    </div>
    """, unsafe_allow_html=True)

    lab_name = st.selectbox(
        "Выберите ИЛ:",
        list(LABS.keys()),
        label_visibility="collapsed"  # скрываем стандартную метку
    )

    st.divider()

# --- ЗАГОЛОВОК ---
lab_display_name = lab_name

# Определяем градиент для нижней части в зависимости от лаборатории
if lab_name == "ИЛ УЛЦ":
    header_gradient = "linear-gradient(135deg, #00b894 0%, #00cec9 100%)"
else:
    header_gradient = "linear-gradient(135deg, #0984e3 0%, #74b9ff 100%)"

st.markdown(f"""
<div style="text-align: center; margin-bottom: 24px; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.08);">
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 30px 20px 24px 20px;
                color: white;">
        <h1 style="margin:0; font-size: 26px; font-weight: 600; letter-spacing: 0.3px;">
            🔍 Проверка наличия ТНВЭД в ОА ИЛ
        </h1>
    </div>
    <div style="background: {header_gradient};
                padding: 14px;
                color: white;
                font-size: 20px;
                font-weight: 600;
                letter-spacing: 0.2px;">
        {lab_display_name}
    </div>
</div>
""", unsafe_allow_html=True)

# --- ЗАГРУЗКА ДАННЫХ ---
with st.spinner(f"Загрузка данных для {lab_name}..."):
    df = load_data(LABS[lab_name]["file"])

if df.empty:
    st.error("❌ Данные не загружены. Проверьте наличие файла в папке data/")
    st.stop()

info = get_data_info(df)

# --- БОКОВАЯ ПАНЕЛЬ (продолжение) ---
with st.sidebar:
    # Информация о данных
    st.info(
        f"📊 Данные загружены\n\n"
        f"Записей: **{info['rows']}**\n\n"
        f"Стандартов: **{df['стандарт_ИЛ'].nunique()}**"
    )

# --- ОСНОВНАЯ ОБЛАСТЬ ---

# --- ФОРМА ВВОДА ---

# Блок загрузки файла
with st.expander("📂 Загрузить макет сертификата", expanded=False):
    uploaded_file = st.file_uploader(
        "Выберите файл макета (Word .docx)",
        type=['docx'],
        help="Загрузите файл макета, и программа автоматически заполнит поля"
    )

    if uploaded_file is not None:
        with st.spinner("Парсинг файла..."):
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                from src.parser import parse_certificate

                parsed = parse_certificate(temp_path)

                if parsed['tnved_codes']:
                    st.session_state.tnved_input = ", ".join(parsed['tnved_codes'])
                    st.success(f"✅ Найдено кодов ТНВЭД: {len(parsed['tnved_codes'])}")
                else:
                    st.warning("⚠️ Коды ТНВЭД не найдены")

                if parsed['standards']:
                    st.session_state.standards_input = "\n".join(parsed['standards'])
                    st.success(f"✅ Найдено стандартов: {len(parsed['standards'])}")
                else:
                    st.warning("⚠️ Стандарты не найдены")

                if parsed.get('product_info'):
                    with st.expander("📦 Информация о продукции"):
                        st.write(parsed['product_info'])

            except Exception as e:
                st.error(f"❌ Ошибка при парсинге: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    st.divider()

st.subheader("📝 Введите данные для проверки")

col1, col2 = st.columns(2)

with col1:
    tnved_input = st.text_area(
        "Коды ТНВЭД",
        value=st.session_state.tnved_input,
        placeholder="Введите коды ТНВЭД\nПример: 8413\n8415\n8418",
        height=200,
        help="Каждый код с новой строки или через запятую, точку с запятой, |"
    )

with col2:
    standards_input = st.text_area(
        "Стандарты",
        value=st.session_state.standards_input,
        placeholder="Введите стандарты\nПример: ГОСТ Р 12345-2021\nГОСТ 67890-2019",
        height=200,
        help="Каждый стандарт с новой строки или через запятую, точку с запятой, |"
    )

# Кнопка проверки
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    check_btn = st.button("🔍 ВЫПОЛНИТЬ ПРОВЕРКУ", type="primary", use_container_width=True)

# --- ЛОГИКА ПРОВЕРКИ ---
if check_btn:
    if not tnved_input or not standards_input:
        st.warning("⚠️ Введите и коды ТНВЭД, и стандарты")
        st.stop()


    # Парсим ввод
    def parse_values(text):
        if not text or not text.strip():
            return []
        # Заменяем разделители на \n
        for sep in [',', ';', '|']:
            text = text.replace(sep, '\n')
        values = [v.strip() for v in text.split('\n') if v.strip()]
        # Убираем дубликаты
        seen = set()
        result = []
        for v in values:
            if v not in seen:
                seen.add(v)
                result.append(v)
        return result


    tnved_list = parse_values(tnved_input)
    standards_raw = parse_values(standards_input)

    if not tnved_list or not standards_raw:
        st.warning("⚠️ Не удалось распознать введенные данные")
        st.stop()


    # --- ФУНКЦИЯ ОЧИСТКИ СТАНДАРТА (убираем год и скобки) ---
    def clean_standard(std_text):
        if not std_text:
            return ''
        std = str(std_text)
        # Убираем всё после скобок
        std = re.sub(r'[\(\[\{].*$', '', std)
        # Убираем всё после последнего дефиса (год)
        last_dash = max(std.rfind('-'), std.rfind('—'), std.rfind('–'))
        if last_dash != -1:
            std = std[:last_dash].rstrip()
        # Убираем лишние пробелы
        std = re.sub(r'\s+', ' ', std).strip()
        return std


    # --- ФУНКЦИЯ ГРУППИРОВКИ РАЗДЕЛОВ С ЧАСТЯМИ ---
    def group_sections_with_parts(sections_with_parts):
        """
        Группирует разделы по part.
        Вход: список кортежей (part, section_number)
        Выход: строка вида "ч1: 1-5, 10; ч1_2: 1-3, 8"
        """
        if not sections_with_parts:
            return ""

        # Группируем по part
        parts_dict = {}
        for part, section in sections_with_parts:
            if part not in parts_dict:
                parts_dict[part] = []
            parts_dict[part].append(section)

        # Для каждой part группируем разделы в диапазоны
        result_parts = []
        for part in sorted(parts_dict.keys()):
            sections = parts_dict[part]
            sections = sorted(list(set(sections)))

            # Группируем в диапазоны
            ranges = []
            start = sections[0]
            end = sections[0]
            for i in range(1, len(sections)):
                if sections[i] == end + 1:
                    end = sections[i]
                else:
                    ranges.append(str(start) if start == end else f"{start}-{end}")
                    start = sections[i]
                    end = sections[i]
            ranges.append(str(start) if start == end else f"{start}-{end}")

            result_parts.append(f"{part}: {', '.join(ranges)}")

        return "; ".join(result_parts)


    # --- ОСНОВНАЯ ЛОГИКА ПРОВЕРКИ ---

    # Очищаем стандарты
    standards_clean = [clean_standard(std) for std in standards_raw]

    # Результаты
    results = []

    for idx, clean_std in enumerate(standards_clean):
        original_std = standards_raw[idx]

        # Если после очистки стандарт пустой
        if not clean_std:
            results.append({
                'Стандарт в СС': original_std,
                'Результаты': []
            })
            for tnved in tnved_list:
                results[-1]['Результаты'].append({
                    'Код ТН ВЭД': tnved,
                    'Разделы с наличием': '',
                    'Разделы с отсутствием': '',
                    'Статус': '⚠️ Пустой стандарт после очистки'
                })
            continue

        # Ищем стандарт в базе (все строки с этим стандартом)
        mask = df['стандарт_ИЛ'].fillna('').str.contains(
            re.escape(clean_std),
            case=False,
            na=False,
            regex=True
        )
        matching_rows = df[mask]

        # Если стандарт не найден
        if matching_rows.empty:
            results.append({
                'Стандарт в СС': original_std,
                'Результаты': []
            })
            for tnved in tnved_list:
                results[-1]['Результаты'].append({
                    'Код ТН ВЭД': tnved,
                    'Разделы с наличием': '',
                    'Разделы с отсутствием': '',
                    'Статус': '☢️ НЕТ СТАНДАРТА'
                })
            continue

        # Стандарт найден — проверяем для каждого ТНВЭД
        standard_result = {
            'Стандарт в СС': original_std,
            'Результаты': []
        }

        for tnved in tnved_list:
            # Очищаем код ТНВЭД от пробелов
            tnved_clean = re.sub(r'\s+', '', str(tnved))
            if not tnved_clean.isdigit():
                tnved_clean = re.sub(r'[^\d]', '', tnved_clean)

            sections_present = []  # теперь храним (part, section)
            sections_absent = []  # теперь храним (part, section)

            # Получаем уникальные комбинации (part, раздел) для этого стандарта
            unique_sections = matching_rows[['part', 'раздел_ИЛ']].dropna().drop_duplicates()

            # Для каждого раздела проверяем наличие кода
            for _, row in unique_sections.iterrows():
                part = row['part']
                section = row['раздел_ИЛ']

                # Все строки для этого part, раздела и стандарта
                section_rows = matching_rows[
                    (matching_rows['part'] == part) &
                    (matching_rows['раздел_ИЛ'] == section)
                    ]

                # Проверяем, есть ли код хотя бы в одной строке этого раздела
                found = False
                for _, r in section_rows.iterrows():
                    # Коды ТНВЭД в ИЛ (разделитель ;)
                    il_codes_raw = str(r['код_ТНВЭД_ИЛ']).split(';') if pd.notna(r['код_ТНВЭД_ИЛ']) else []
                    il_codes_clean = []
                    for code in il_codes_raw:
                        code_clean = re.sub(r'\s+', '', code.strip())
                        if code_clean.isdigit():
                            il_codes_clean.append(code_clean)

                    # Проверяем совпадение
                    for il_code in il_codes_clean:
                        if len(tnved_clean) >= len(il_code):
                            if tnved_clean[:len(il_code)] == il_code:
                                found = True
                                break
                    if found:
                        break

                if found:
                    sections_present.append((part, section))
                else:
                    sections_absent.append((part, section))

            # Определяем статус
            if sections_present and sections_absent:
                status = '✅ ПРИСУТСТВУЕТ (частично)'
            elif sections_present and not sections_absent:
                status = '✅ ПРИСУТСТВУЕТ'
            elif not sections_present and sections_absent:
                status = '❌ НЕТ КОДА'
            else:
                status = '⚠️ Нет данных о разделах'

            # Группируем разделы с частями
            present_str = group_sections_with_parts(sections_present)
            absent_str = group_sections_with_parts(sections_absent)

            standard_result['Результаты'].append({
                'Код ТН ВЭД': tnved,
                'Разделы с наличием': present_str,
                'Разделы с отсутствием': absent_str,
                'Статус': status
            })

        results.append(standard_result)

    # Сохраняем в session_state для отображения
    st.session_state.results = results

# --- ВЫВОД РЕЗУЛЬТАТОВ ---
if st.session_state.results:
    st.markdown("---")
    st.subheader("📊 РЕЗУЛЬТАТЫ ПРОВЕРКИ")

    # Преобразуем данные в плоскую таблицу
    table_data = []
    for std_result in st.session_state.results:
        standard_name = std_result['Стандарт в СС']
        for res in std_result['Результаты']:
            # Заменяем статусы на единообразные
            status = res['Статус']
            if status == '✅ ПРИСУТСТВУЕТ (частично)':
                status_display = '⚠️ ПРИСУТСТВУЕТ ЧАСТИЧНО'
            elif status == '✅ ПРИСУТСТВУЕТ':
                status_display = '✅ ПРИСУТСТВУЕТ'
            elif status == '❌ НЕТ КОДА':
                status_display = '❌ НЕТ КОДА'
            elif status == '☢️ НЕТ СТАНДАРТА':
                status_display = '☢️ НЕТ СТАНДАРТА'
            else:
                status_display = status

            table_data.append({
                'Стандарт': standard_name,
                'Код ТН ВЭД': res['Код ТН ВЭД'],
                'Разделы с наличием': res['Разделы с наличием'] if res['Разделы с наличием'] else '—',
                'Разделы с отсутствием': res['Разделы с отсутствием'] if res['Разделы с отсутствием'] else '—',
                'Статус': status_display
            })

    df_results = pd.DataFrame(table_data)

    # Отображаем таблицу с автошириной
    st.data_editor(
        df_results,
        column_config={
            'Стандарт': st.column_config.TextColumn('Стандарт', width=None),
            'Код ТН ВЭД': st.column_config.TextColumn('Код ТН ВЭД', width=None),
            'Разделы с наличием': st.column_config.TextColumn('Разделы с наличием', width=None),
            'Разделы с отсутствием': st.column_config.TextColumn('Разделы с отсутствием', width=None),
            'Статус': st.column_config.TextColumn('Статус', width=None),
        },
        hide_index=True,
        use_container_width=True,
        disabled=True,
        key=f"table_{len(df_results)}"
    )
else:
    if not check_btn:
        st.info("👆 Введите данные и нажмите «ВЫПОЛНИТЬ ПРОВЕРКУ»")

# --- БОКОВАЯ ПАНЕЛЬ (продолжение) ---
with st.sidebar:
    # Информация о данных
    st.info(
        f"📊 Данные загружены\n\n"
        f"Записей: **{info['rows']}**\n\n"
        f"Стандартов: **{df['стандарт_ИЛ'].nunique()}**"
    )

    # Разделитель
    st.divider()

    # Плашка "Сказать спасибо" внизу боковой панели
    st.markdown("""
    <div style="text-align: center; 
                padding: 8px;
                margin-top: 10px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 8px;">
        <span style="font-size: 12px; color: #555;">
            🙏 Сказать спасибо:<br>
            <a href="mailto:515@tekhotdel.com?subject=Проверка наличия ТНВЭД в ОА ИЛ&body=Спасибо! Отличное приложение! 🚀" 
               style="color: #3498db; 
                      text-decoration: none; 
                      font-weight: 500;
                      font-size: 13px;">
                515@tekhotdel.com
            </a>
            😊
        </span>
    </div>
    """, unsafe_allow_html=True)