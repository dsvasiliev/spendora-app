import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from infrastructure.tools.define_error import define_error


class DBManager:
    def __init__(self, db_path: Path):
        try:
            self._connection = sqlite3.connect(db_path)
        except sqlite3.OperationalError as error:
            define_error(
                "База данных",
                "Невозможно открыть базу данных",
                error,
                True
            )
            return
        self._init_db()

    def _init_db(self):
        # Регистрируем адаптер: datetime в строку
        sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
        # Регистрируем конвертер: строку в datetime
        sqlite3.register_converter("TIMESTAMP", lambda s: datetime.fromisoformat(s.decode('utf-8')))

        self._connection.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                product_name TEXT UNIQUE,
                category_name TEXT,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self._connection.commit()

    def get_category_name(self, product_name: str) -> str | None:
        """Получить название категории"""
        cur = self._connection.execute("SELECT category_name FROM products WHERE product_name = ?", (product_name,))
        row = cur.fetchone()
        return row[0] if row else None

    def set_category(self, product_name: str, category_name: str):
        """Добавляем новую запись или обновляем существующую"""
        self._connection.execute('''
            INSERT OR REPLACE INTO products
            (product_name, category_name, last_used)
            VALUES (?, ?, ?)
        ''', (product_name, category_name, datetime.now()))
        self._connection.commit()

    def cleanup_old_data(self):
        """Удаление данных старше указанного количества дней"""
        try:
            cutoff_date = datetime.now() - timedelta(days=365)
            self._connection.execute(
                "DELETE FROM products WHERE last_used < ?",
                (cutoff_date.isoformat(),)
            )
            self._connection.commit()
            self._connection.close()
        except sqlite3.OperationalError:
            define_error("База данных", "Не удалось очистить базу данных")

    def close(self):
        self._connection.commit()
        self._connection.close()



# dbmanager = DBManager(db_path="categories1.memory")
# dbmanager.set_category("Батон Горчичный нарезка 370г поли/уп(Атрус)", "Хлеб")
# print(dbmanager.get_category_name("Продукт 2"))
# dbmanager.cleanup_old_data()
# dbmanager.close()