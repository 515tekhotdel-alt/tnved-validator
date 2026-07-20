import pandas as pd

df = pd.read_excel('data/ИЛ Максвелл 2026 007 для кодов.xlsx')

print("=== КОЛОНКИ ===")
print(df.columns.tolist())
print()

print("=== УНИКАЛЬНЫЕ ЗНАЧЕНИЯ type2 ===")
print(df['type2'].unique())
print()

print("=== СТРОКИ С type2 == 'normDocument' ===")
norm_rows = df[df['type2'] == 'normDocument']
print(f"Количество: {len(norm_rows)}")
print(norm_rows[['indexNumber', 'name']].head(10))
print()

print("=== СТРОКИ С type2 == 'tnvedCode' ===")
tnved_rows = df[df['type2'] == 'tnvedCode']
print(f"Количество: {len(tnved_rows)}")
print(tnved_rows[['indexNumber', 'code']].head(10))
print()

print("=== ПРОВЕРКА СВЯЗЕЙ ===")
standards_dict = {}
for _, row in norm_rows.iterrows():
    idx = row['indexNumber']
    std_name = row['name']
    if pd.notna(idx) and pd.notna(std_name):
        standards_dict[idx] = std_name

print(f"Стандартов в словаре: {len(standards_dict)}")
print(f"Первые 5: {list(standards_dict.items())[:5]}")
print()

tnved_list = []
for _, row in tnved_rows.iterrows():
    idx = row['indexNumber']
    code = row['code']
    if pd.notna(idx) and pd.notna(code):
        code_clean = str(code).strip()
        tnved_list.append((idx, code_clean))

print(f"Кодов ТНВЭД в списке: {len(tnved_list)}")
print(f"Первые 5: {tnved_list[:5]}")
print()

print("=== ПРОВЕРКА ПЕРЕСЕЧЕНИЙ ===")
matched = 0
for idx, code in tnved_list:
    if idx in standards_dict:
        matched += 1
print(f"Совпавших записей: {matched} из {len(tnved_list)}")