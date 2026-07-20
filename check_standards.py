import pandas as pd

# Загружаем файл
file_path = "data/УЛЦ АОА + РОА 20-07-26 только коды 002.xlsx"
df = pd.read_excel(file_path)

# 1. Сколько всего строк
print(f"Всего строк в файле: {len(df)}")
print()

# 2. Сколько строк с normDocument
norm_rows = df[df['name'] == 'normDocument']
print(f"Строк с normDocument: {len(norm_rows)}")

# 3. Уникальные стандарты (по комбинации part + name3)
print(f"Уникальных комбинаций (part, name3): {len(norm_rows[['part', 'name3']].drop_duplicates())}")

# 4. Уникальные стандарты (только name3, без part)
print(f"Уникальных name3 (названий стандартов): {norm_rows['name3'].nunique()}")

# 5. Уникальные part (части)
print(f"Уникальных частей (part): {norm_rows['part'].nunique()}")
print(f"Части: {norm_rows['part'].unique().tolist()}")
print()

# 6. Сколько стандартов в каждой части
print("=== Стандартов по частям ===")
part_stats = norm_rows.groupby('part')['name3'].nunique()
for part, count in part_stats.items():
    print(f"  {part}: {count} стандартов")
print()

# 7. Проверка: есть ли строки normDocument с пустым name3
empty_norm = norm_rows[norm_rows['name3'].isna() | (norm_rows['name3'] == '')]
print(f"Строк normDocument с пустым name3: {len(empty_norm)}")
if len(empty_norm) > 0:
    print(empty_norm[['part', 'indexNumber', 'name3']])

# 8. Проверка: есть ли дубликаты стандартов в одной части
print("\n=== Дубликаты стандартов в одной части ===")
duplicates = norm_rows[norm_rows.duplicated(subset=['part', 'name3'], keep=False)]
if len(duplicates) > 0:
    print(f"Найдено дубликатов: {len(duplicates)}")
    print(duplicates[['part', 'indexNumber', 'name3']])
else:
    print("Дубликатов нет")

# 9. Проверка: что программа считает стандартами
print("\n=== Что программа считает стандартом ===")
print("Программа берет строки где name == 'normDocument' и берет name3")
print("Программа считает уникальные комбинации (part, name3)")

# 10. Вывод первых 10 стандартов
print("\n=== Первые 10 стандартов в программе ===")
for i, (idx, row) in enumerate(norm_rows.iterrows()):
    if i >= 10:
        break
    print(f"  {i+1}. {row['part']} -> {row['name3']}")