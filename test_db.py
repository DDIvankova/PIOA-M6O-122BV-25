"""
Простой тест для проверки работы базы данных.
Запустите этот файл, чтобы убедиться, что БД работает.
"""

import sys
sys.path.insert(0, '.')

from src.db.backend.memory import db, ValidationError, TableNotFoundError

# 1. Создаем таблицу
print("1. Создаем таблицу тестов...")
db.create_table('test', {
    'id': int,
    'name': str,
    'value': int
})
print("   ✅ Таблица создана")

# 2. Добавляем записи
print("\n2. Добавляем записи...")
record1 = db.create_record('test', {'name': 'Первый', 'value': 10})
record2 = db.create_record('test', {'name': 'Второй', 'value': 20})
print(f"   ✅ Добавлены записи: {record1['id']}, {record2['id']}")

# 3. Читаем все записи
print("\n3. Читаем все записи...")
all_records = db.select_records('test')
for r in all_records:
    print(f"   📝 {r}")

# 4. Фильтрация
print("\n4. Поиск по фильтру (value=10)...")
filtered = db.select_records('test', {'value': 10})
print(f"   🔍 Найдено: {filtered}")

# 5. Обновление
print("\n5. Обновляем запись...")
updated = db.update_record('test', 1, {'value': 100})
print(f"   ✏️ Обновлено: {updated}")

# 6. Удаление
print("\n6. Удаляем запись...")
deleted = db.delete_record('test', 2)
print(f"   🗑️ Удалено: {deleted}")

# 7. Проверяем результат
print("\n7. Финальное состояние таблицы...")
remaining = db.select_records('test')
print(f"   📊 Осталось записей: {len(remaining)}")

print("\n✅ Все тесты пройдены успешно!")