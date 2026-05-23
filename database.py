import sqlite3
from datetime import datetime, timedelta
import random


class Database:
    def __init__(self, db_path="calorie_tracker.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.init_tables()
        self.add_default_products()
        self.add_test_data()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        if self.conn:
            self.conn.close()

    def init_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                age INTEGER,
                gender TEXT,
                weight REAL,
                height REAL,
                activity_level TEXT,
                goal TEXT,
                daily_calories REAL,
                daily_protein REAL,
                daily_fat REAL,
                daily_carbs REAL,
                created_date TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL
            )
        ''')


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                meal_type TEXT,
                product_id INTEGER,
                weight REAL,
                calories REAL,
                protein REAL,
                fat REAL,
                carbs REAL
            )
        ''')


        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS weight_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                weight REAL,
                UNIQUE(user_id, date)
            )
        ''')

        self.conn.commit()

    def add_default_products(self):
        default_products = [
            ("Куриная грудка", 165, 31, 3.6, 0),
            ("Рис отварной", 130, 2.7, 0.3, 28),
            ("Гречка отварная", 110, 3.6, 1.1, 21),
            ("Овсянка", 88, 3.5, 1.7, 15),
            ("Яйцо куриное", 155, 12.6, 10.6, 0.8),
            ("Творог 5%", 121, 17, 5, 3),
            ("Молоко 2.5%", 52, 2.8, 2.5, 4.7),
            ("Хлеб белый", 265, 7.5, 3.6, 49),
            ("Яблоко", 52, 0.3, 0.2, 14),
            ("Банан", 89, 1.1, 0.3, 23),
            ("Лосось", 208, 20, 13, 0),
            ("Авокадо", 160, 2, 15, 9),
            ("Сыр", 350, 23, 28, 2),
            ("Картофель", 77, 2, 0.4, 17),
            ("Помидор", 18, 0.9, 0.2, 3.9),
            ("Огурец", 15, 0.7, 0.1, 3.6),
        ]
        for product in default_products:
            try:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO products (name, calories, protein, fat, carbs)
                    VALUES (?, ?, ?, ?, ?)
                ''', product)
            except:
                pass
        self.conn.commit()

    def add_test_data(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        if self.cursor.fetchone()[0] > 0:
            return
        pass


    def get_all_users(self):
        self.cursor.execute("SELECT id, name FROM users ORDER BY name")
        return self.cursor.fetchall()

    def get_user_norms(self, user_id):
        self.cursor.execute("SELECT daily_calories, daily_protein, daily_fat, daily_carbs FROM users WHERE id=?",
                            (user_id,))
        return self.cursor.fetchone()

    def get_user_weight(self, user_id):
        self.cursor.execute("SELECT weight FROM users WHERE id=?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 70

    def get_products(self, search_text=""):
        if search_text:
            self.cursor.execute("SELECT name, calories, protein, fat, carbs FROM products WHERE name LIKE ? LIMIT 30",
                                (f"%{search_text}%",))
        else:
            self.cursor.execute("SELECT name, calories, protein, fat, carbs FROM products LIMIT 30")
        return self.cursor.fetchall()

    def get_product_id(self, name):
        self.cursor.execute("SELECT id FROM products WHERE name=?", (name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_meal(self, user_id, date, meal_type, product_id, weight, calories, protein, fat, carbs):
        self.cursor.execute('''
            INSERT INTO meals (user_id, date, meal_type, product_id, weight, calories, protein, fat, carbs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, date, meal_type, product_id, weight, calories, protein, fat, carbs))
        self.conn.commit()

    def get_meals_by_date(self, user_id, date, meal_type):
        self.cursor.execute('''
            SELECT m.id, p.name, m.weight, m.calories, m.protein, m.fat, m.carbs
            FROM meals m JOIN products p ON m.product_id = p.id
            WHERE m.user_id=? AND m.date=? AND m.meal_type=?
            ORDER BY m.id
        ''', (user_id, date, meal_type))
        return self.cursor.fetchall()

    def delete_meal(self, meal_id):
        self.cursor.execute("DELETE FROM meals WHERE id=?", (meal_id,))
        self.conn.commit()

    def get_daily_totals(self, user_id, date):
        self.cursor.execute(
            "SELECT SUM(calories), SUM(protein), SUM(fat), SUM(carbs) FROM meals WHERE user_id=? AND date=?",
            (user_id, date))
        row = self.cursor.fetchone()
        return row[0] or 0, row[1] or 0, row[2] or 0, row[3] or 0

    def get_weight_history(self, user_id):
        self.cursor.execute("SELECT date, weight FROM weight_log WHERE user_id=? ORDER BY date", (user_id,))
        return self.cursor.fetchall()

    def get_pie_data(self, user_id, date):
        self.cursor.execute("SELECT SUM(protein), SUM(fat), SUM(carbs) FROM meals WHERE user_id=? AND date=?",
                            (user_id, date))
        row = self.cursor.fetchone()
        return row[0] or 0, row[1] or 0, row[2] or 0

    def get_30_days_progress(self, user_id):
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=29)
        result = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            self.cursor.execute("SELECT SUM(calories) FROM meals WHERE user_id=? AND date=?", (user_id, date_str))
            total = self.cursor.fetchone()[0] or 0
            result.append((current_date.strftime("%d.%m"), total))
            current_date += timedelta(days=1)
        return result

    def add_weight(self, user_id, date, weight):
        self.cursor.execute('''
            INSERT OR REPLACE INTO weight_log (user_id, date, weight)
            VALUES (?, ?, ?)
        ''', (user_id, date, weight))
        self.conn.commit()

    def update_user_weight(self, user_id, weight):
        self.cursor.execute("UPDATE users SET weight=? WHERE id=?", (weight, user_id))
        self.conn.commit()