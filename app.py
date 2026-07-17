import streamlit as st
import pandas as pd
import re
from src.data_loader import load_data, get_data_info

# Настройка страницы
st.set_page_config(
    page_title="Проверка ТНВЭД в ОА ИЛ",
    page_icon="🔍",
    layout="wide"
)

# Инициализация переменной для результатов
if 'results' not in st.session_state:
    st.session_state.results = []

# Заголовок
st.markdown("""
<div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            text-align: center;
            margin-bottom: 30px;">
    <h1 style="margin:0; font-size: 28px;">🔍 Проверка наличия ТНВЭД в ОА ИЛ</h1>
    <p style="margin:5px 0 0 0; opacity:0.9;">Испытательная лаборатория «Максвел»</p>
</div>
""", unsafe_allow_html=True)

# Загрузка данных
with st.spinner("Загрузка данных..."):
    df = load_data()

if df.empty:
    st.error("❌ Данные не загружены. Проверьте наличие файла в папке data/")
    st.stop()

info = get_data_info(df)

# --- БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 15px;">
        <h2 style="margin:0; font-size: 18px; color: #2c3e50;">⚙️ Настройки</h2>
    </div>
    """, unsafe_allow_html=True)

    # Выбор лаборатории (пока одна)
    st.selectbox(
        "Выберите ИЛ:",
        ["ИЛ Максвел 2026"],
        disabled=True,
        help="В текущей версии доступна только одна лаборатория"
    )

    st.divider()

    # Информация о данных
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
        <p style="margin:0; font-size: 13px; color: #555;">
            <b>📊 Данные загружены</b><br>
            Записей: <b>{info['rows']}</b><br>
            Стандартов: <b>{df['стандарт_ИЛ'].nunique()}</b>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Краткая инструкция
    with st.expander("📖 Инструкция", expanded=False):
        st.markdown("""
        1. Введите коды ТНВЭД (каждый с новой строки)
        2. Введите стандарты (каждый с новой строки)
        3. Нажмите «ВЫПОЛНИТЬ ПРОВЕРКУ»

        **Разделители:** запятая, точка с запятой, |, перенос строки
        """)

# --- ОСНОВНАЯ ОБЛАСТЬ ---

# Форма ввода
st.subheader("📝 Введите данные для проверки")

col1, col2 = st.columns(2)

with col1:
    tnved_input = st.text_area(
        "Коды ТНВЭД",
        placeholder="Введите коды ТНВЭД\nПример: 8413\n8415\n8418",
        height=200,
        help="Каждый код с новой строки или через запятую, точку с запятой, |"
    )

with col2:
    standards_input = st.text_area(
        "Стандарты",
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

    st.success(f"✅ Найдено кодов ТНВЭД: {len(tnved_list)}, стандартов: {len(standards_raw)}")


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


    # --- ФУНКЦИЯ ГРУППИРОВКИ РАЗДЕЛОВ В ДИАПАЗОНЫ ---
    def group_sections(sections_list):
        if not sections_list:
            return ""
        try:
            sections = []
            for s in sections_list:
                if pd.notna(s):
                    try:
                        sections.append(int(float(s)))
                    except:
                        continue
            sections = sorted(list(set(sections)))
            if not sections:
                return ""
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
            return ", ".join(ranges)
        except:
            return "ошибка"


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

        # Ищем стандарт в базе
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
                    'Статус': '❌ Нет стандарта в ОА ИЛ'
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

            sections_present = []
            sections_absent = []

            # Проверяем каждую строку с этим стандартом
            for _, row in matching_rows.iterrows():
                # Коды ТНВЭД в ИЛ (разделитель ;)
                il_codes_raw = str(row['код_ТНВЭД_ИЛ']).split(';') if pd.notna(row['код_ТНВЭД_ИЛ']) else []
                il_codes_clean = []
                for code in il_codes_raw:
                    code_clean = re.sub(r'\s+', '', code.strip())
                    if code_clean.isdigit():
                        il_codes_clean.append(code_clean)

                # Проверяем совпадение
                found = False
                for il_code in il_codes_clean:
                    if len(tnved_clean) >= len(il_code):
                        if tnved_clean[:len(il_code)] == il_code:
                            found = True
                            break

                # Собираем разделы
                section = row['раздел_ИЛ'] if pd.notna(row['раздел_ИЛ']) else None
                if section is not None:
                    if found:
                        sections_present.append(section)
                    else:
                        sections_absent.append(section)

            # Определяем статус
            if sections_present and sections_absent:
                status = '✅ ПРИСУТСТВУЕТ (частично)'
            elif sections_present and not sections_absent:
                status = '✅ ПРИСУТСТВУЕТ'
            elif not sections_present and sections_absent:
                status = '⚠️ ОТСУТСТВУЕТ'
            else:
                status = '⚠️ Нет данных о разделах'

            # Группируем разделы
            present_str = group_sections(sections_present)
            absent_str = group_sections(sections_absent)

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
            elif status == '⚠️ ОТСУТСТВУЕТ':
                status_display = '❌ ОТСУТСТВУЕТ'
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
    st.dataframe(
        df_results,
        column_config={
            'Стандарт': st.column_config.TextColumn('Стандарт', width='medium'),
            'Код ТН ВЭД': st.column_config.TextColumn('Код ТН ВЭД', width='small'),
            'Разделы с наличием': st.column_config.TextColumn('Разделы с наличием', width='small'),
            'Разделы с отсутствием': st.column_config.TextColumn('Разделы с отсутствием', width='small'),
            'Статус': st.column_config.TextColumn('Статус', width='small'),
        },
        hide_index=True,
        use_container_width=True
    )
else:
    if not check_btn:
        st.info("👆 Введите данные и нажмите «ВЫПОЛНИТЬ ПРОВЕРКУ»")