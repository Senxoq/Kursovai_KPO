import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox
from tkcalendar import DateEntry
from views.user_manager import UserManagerDialog
from views.widgets import ProgressCard
from views.dialogs import ProfileDialog, StatsDialog, CustomProductDialog


class MainWindow(ctk.CTk):
    def __init__(self, db):
        super().__init__()

        self.db = db

        self.title("🥗 CalorieFlow - Калькулятор калорий")
        self.geometry("1500x850")
        self.minsize(1300, 750)

        self.colors = {
            "primary": "#10B981",
            "primary_dark": "#059669",
            "primary_light": "#34D399",
            "secondary": "#1a1a1a",
            "bg": "#0a0a0a",
            "card": "#1a1a1a",
            "card_light": "#2a2a2a",
            "text": "#FFFFFF",
            "text_secondary": "#888888",
            "error": "#EF4444",
            "selected": "#2a5a3a"
        }

        self.current_user_id = None
        self.current_user_name = None
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.meal_types = ["Завтрак", "Обед", "Ужин", "Перекус"]
        self.current_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        self.search_results = []
        self.meal_frames = {}
        self.selected_product = None
        self.selected_card = None

        self.setup_ui()

        users = self.db.get_all_users()
        if users:
            self.set_current_user(users[0][0], users[0][1])

    def get_product_icon(self, name):
        name_lower = name.lower()
        if "курица" in name_lower or "индейка" in name_lower:
            return "🐔"
        elif "говядина" in name_lower or "свинина" in name_lower:
            return "🥩"
        elif "рыба" in name_lower or "лосось" in name_lower:
            return "🐟"
        elif "рис" in name_lower:
            return "🍚"
        elif "гречка" in name_lower:
            return "🌾"
        elif "овсянка" in name_lower:
            return "🥣"
        elif "яйцо" in name_lower:
            return "🥚"
        elif "творог" in name_lower:
            return "🥛"
        elif "сыр" in name_lower:
            return "🧀"
        elif "молоко" in name_lower:
            return "🥛"
        elif "яблоко" in name_lower:
            return "🍎"
        elif "банан" in name_lower:
            return "🍌"
        elif "помидор" in name_lower:
            return "🍅"
        elif "огурец" in name_lower:
            return "🥒"
        elif "картофель" in name_lower:
            return "🥔"
        elif "хлеб" in name_lower:
            return "🍞"
        else:
            return "🍽️"

    def setup_ui(self):
        self.configure(fg_color=self.colors["bg"])

        # Верхняя панель
        top_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=self.colors["secondary"])
        top_frame.pack(fill="x", padx=0, pady=0)
        top_frame.pack_propagate(False)

        # Левая часть - логотип и имя пользователя в одной строке
        left_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        left_frame.place(relx=0.02, rely=0.5, anchor="w")

        ctk.CTkLabel(left_frame, text="🥗 CalorieFlow", font=("Segoe UI", 28, "bold"),
                     text_color=self.colors["primary"]).pack(side="left")

        self.user_label = ctk.CTkLabel(left_frame, text="", font=("Segoe UI", 14),
                                       text_color=self.colors["text_secondary"])
        self.user_label.pack(side="left", padx=(20, 0))

        # Кнопки (справа)
        btn_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        btn_frame.place(relx=0.98, rely=0.5, anchor="e")

        ctk.CTkButton(btn_frame, text="📊 Статистика", command=self.show_stats,
                      width=120, height=40, corner_radius=15, fg_color=self.colors["primary"],
                      font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="⚖️ Добавить вес", command=self.add_weight_dialog,
                      width=120, height=40, corner_radius=15, fg_color=self.colors["card_light"],
                      font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="👥 Пользователи", command=self.show_user_manager,
                      width=120, height=40, corner_radius=15, fg_color=self.colors["card_light"],
                      font=("Segoe UI", 12)).pack(side="left", padx=5)

        ctk.CTkButton(btn_frame, text="✨ Свой продукт", command=self.open_custom_product_dialog,
                      width=120, height=40, corner_radius=15, fg_color=self.colors["card_light"],
                      font=("Segoe UI", 12)).pack(side="left", padx=5)

        # Основной контент
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Левая панель
        left_panel = ctk.CTkFrame(main_frame, width=350, corner_radius=20, fg_color=self.colors["card"])
        left_panel.pack(side="left", fill="both", padx=(0, 10))
        left_panel.pack_propagate(False)
        self.setup_left_panel(left_panel)

        # Центральная панель
        center_panel = ctk.CTkFrame(main_frame, width=500, corner_radius=20, fg_color=self.colors["card"])
        center_panel.pack(side="left", fill="both", padx=10)
        center_panel.pack_propagate(False)
        self.setup_center_panel(center_panel)

        # Правая панель
        right_panel = ctk.CTkFrame(main_frame, width=500, corner_radius=20, fg_color=self.colors["card"])
        right_panel.pack(side="right", fill="both", padx=(10, 0))
        right_panel.pack_propagate(False)
        self.setup_right_panel(right_panel)

    def open_custom_product_dialog(self):
        if not self.current_user_id:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя")
            return
        CustomProductDialog(self, self.db, self.load_products_list)

    def add_weight_dialog(self):
        if not self.current_user_id:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("⚖️ Добавить замер веса")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#0a0a0a")

        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(main, text="⚖️ Добавить замер веса", font=("Segoe UI", 22, "bold"),
                     text_color="#10B981").pack(pady=(0, 20))

        date_frame = ctk.CTkFrame(main, fg_color="transparent")
        date_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(date_frame, text="📅 Дата:", font=("Segoe UI", 14)).pack(side="left", padx=10)

        self.weight_date = DateEntry(date_frame, width=14, background='darkblue',
                                     foreground='white', borderwidth=2,
                                     date_pattern='yyyy-mm-dd')
        self.weight_date.pack(side="left", padx=10)
        self.weight_date.set_date(datetime.now())

        weight_frame = ctk.CTkFrame(main, fg_color="transparent")
        weight_frame.pack(fill="x", pady=15)

        ctk.CTkLabel(weight_frame, text="⚖️ Вес (кг):", font=("Segoe UI", 14)).pack(side="left", padx=10)
        weight_entry = ctk.CTkEntry(weight_frame, width=120, height=40, font=("Segoe UI", 14))
        weight_entry.pack(side="left", padx=10)

        current_weight = self.db.get_user_weight(self.current_user_id)
        ctk.CTkLabel(weight_frame, text=f"(текущий: {current_weight:.1f} кг)",
                     font=("Segoe UI", 11), text_color="#888888").pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(25, 0))

        def save():
            try:
                new_weight = float(weight_entry.get())
                if new_weight <= 0 or new_weight > 500:
                    raise ValueError
                selected_date = self.weight_date.get()

                self.db.add_weight(self.current_user_id, selected_date, new_weight)
                self.db.update_user_weight(self.current_user_id, new_weight)
                self.update_user_norms()

                messagebox.showinfo("Успех", f"✅ Вес {new_weight:.1f} кг сохранён!")
                dialog.destroy()
            except:
                messagebox.showerror("Ошибка", "Введите корректный вес")

        ctk.CTkButton(btn_frame, text="💾 Сохранить", command=save,
                      width=150, height=45, corner_radius=20, fg_color="#10B981",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=10)

        ctk.CTkButton(btn_frame, text="❌ Отмена", command=dialog.destroy,
                      width=120, height=45, corner_radius=20, fg_color="#2a2a2a",
                      font=("Segoe UI", 14)).pack(side="right", padx=10)

    def update_user_norms(self):
        self.db.cursor.execute("SELECT age, gender, weight, height, activity_level, goal FROM users WHERE id=?",
                               (self.current_user_id,))
        user = self.db.cursor.fetchone()
        if not user:
            return

        age, gender, weight, height, activity, goal = user

        from models import Calculator
        bmr = Calculator.calculate_bmr(weight, height, age, gender)
        tdee = Calculator.calculate_tdee(bmr, activity)
        macros = Calculator.calculate_macros(tdee, goal, weight)

        self.db.cursor.execute('''
            UPDATE users SET 
                daily_calories=?, daily_protein=?, daily_fat=?, daily_carbs=?
            WHERE id=?
        ''', (macros["calories"], macros["protein"], macros["fat"], macros["carbs"], self.current_user_id))
        self.db.conn.commit()

        norms = self.db.get_user_norms(self.current_user_id)
        if norms:
            self.norm_labels["🔥 Калории"].configure(text=f"{norms[0]:.0f} ккал")
            self.norm_labels["🍗 Белки"].configure(text=f"{norms[1]:.0f} г")
            self.norm_labels["🧈 Жиры"].configure(text=f"{norms[2]:.0f} г")
            self.norm_labels["🍚 Углеводы"].configure(text=f"{norms[3]:.0f} г")

    def setup_left_panel(self, parent):
        ctk.CTkLabel(parent, text="📊 Ваша норма КБЖУ", font=("Segoe UI", 20, "bold"),
                     text_color=self.colors["text"]).pack(pady=(20, 15))

        norm_frame = ctk.CTkFrame(parent, fg_color=self.colors["card_light"], corner_radius=15)
        norm_frame.pack(fill="x", padx=15, pady=10)

        self.norm_labels = {}
        norms = [("🔥 Калории", "0 ккал"), ("🍗 Белки", "0 г"), ("🧈 Жиры", "0 г"), ("🍚 Углеводы", "0 г")]

        for name, value in norms:
            frame = ctk.CTkFrame(norm_frame, fg_color="transparent")
            frame.pack(fill="x", padx=15, pady=8)
            ctk.CTkLabel(frame, text=name, font=("Segoe UI", 13), text_color=self.colors["text_secondary"]).pack(side="left")
            self.norm_labels[name] = ctk.CTkLabel(frame, text=value, font=("Segoe UI", 16, "bold"),
                                                  text_color=self.colors["primary"])
            self.norm_labels[name].pack(side="right")

        ctk.CTkFrame(parent, height=1, fg_color="#2a2a2a").pack(fill="x", padx=15, pady=15)
        ctk.CTkLabel(parent, text="📈 Прогресс на сегодня", font=("Segoe UI", 18, "bold"),
                     text_color=self.colors["text"]).pack(pady=(10, 10))

        progress_scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=400)
        progress_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        self.progress_bars = {}
        progress_items = [("Калории", self.colors["primary"]), ("Белки", self.colors["primary_light"]),
                          ("Жиры", "#F59E0B"), ("Углеводы", "#8B5CF6")]

        for item, color in progress_items:
            card = ProgressCard(progress_scroll, item, color)
            card.pack(fill="x", padx=10, pady=8)
            self.progress_bars[item] = card

    def setup_center_panel(self, parent):
        ctk.CTkLabel(parent, text="🍽️ Выберите продукт", font=("Segoe UI", 20, "bold"),
                     text_color=self.colors["text"]).pack(pady=(20, 15))

        self.product_search = ctk.CTkEntry(parent, placeholder_text="🔍 Поиск продуктов...", height=40,
                                           corner_radius=15, fg_color=self.colors["card_light"])
        self.product_search.pack(fill="x", padx=15, pady=5)
        self.product_search.bind("<KeyRelease>", self.search_products)

        self.products_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent", height=200)
        self.products_frame.pack(fill="both", expand=True, padx=15, pady=5)

        self.selected_label = ctk.CTkLabel(parent, text="❌ Продукт не выбран", font=("Segoe UI", 12),
                                           text_color=self.colors["text_secondary"])
        self.selected_label.pack(anchor="w", padx=15, pady=(5, 5))

        clear_btn = ctk.CTkButton(parent, text="✖️ Очистить выбор", command=self.clear_selected_product,
                                  width=120, height=30, corner_radius=10,
                                  fg_color="#2a2a2a", hover_color="#3a3a3a",
                                  font=("Segoe UI", 11))
        clear_btn.pack(anchor="w", padx=15, pady=(0, 5))

        weight_label = ctk.CTkLabel(parent, text="⚖️ Вес порции", font=("Segoe UI", 13, "bold"),
                                    text_color=self.colors["text"])
        weight_label.pack(anchor="w", padx=15, pady=(10, 5))

        weight_frame = ctk.CTkFrame(parent, fg_color="transparent")
        weight_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(weight_frame, text="Вес (г):", font=("Segoe UI", 12)).pack(side="left", padx=10)
        self.weight_entry = ctk.CTkEntry(weight_frame, width=100, height=35, font=("Segoe UI", 13),
                                         fg_color=self.colors["card_light"])
        self.weight_entry.pack(side="left", padx=10)
        self.weight_entry.insert(0, "100")

        quick_weights = [50, 100, 150, 200, 250, 300]
        quick_frame = ctk.CTkFrame(weight_frame, fg_color="transparent")
        quick_frame.pack(side="left", padx=10)
        for w in quick_weights:
            btn = ctk.CTkButton(quick_frame, text=str(w), width=40, height=28, corner_radius=8,
                                fg_color=self.colors["card_light"], font=("Segoe UI", 10),
                                command=lambda val=w: self.weight_entry.delete(0, tk.END) or self.weight_entry.insert(0, str(val)))
            btn.pack(side="left", padx=2)

        meal_frame = ctk.CTkFrame(parent, fg_color="transparent")
        meal_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(meal_frame, text="🍴 Приём пищи:", font=("Segoe UI", 12)).pack(side="left", padx=10)
        self.meal_type_var = tk.StringVar(value="Завтрак")
        meal_combo = ctk.CTkComboBox(meal_frame, values=self.meal_types, variable=self.meal_type_var, width=130,
                                     fg_color=self.colors["card_light"], font=("Segoe UI", 12))
        meal_combo.pack(side="left", padx=10)

        add_btn = ctk.CTkButton(parent, text="➕ Добавить в приём", command=self.add_meal,
                                height=45, corner_radius=20, fg_color=self.colors["primary"],
                                font=("Segoe UI", 14, "bold"))
        add_btn.pack(padx=15, pady=15, fill="x")

        self.load_products_list()

    def create_product_card(self, parent, name, calories, protein, fat, carbs):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color=self.colors["card_light"])
        card.pack(fill="x", pady=3, padx=0)
        card.product_data = (name, calories, protein, fat, carbs)

        def on_click(e=None):
            self.select_product_card(card, name, calories, protein, fat, carbs)

        card.bind("<Button-1>", on_click)
        card.bind("<Enter>", lambda e: self.on_card_hover(card, enter=True))
        card.bind("<Leave>", lambda e: self.on_card_hover(card, enter=False))

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=10, pady=8)
        left.bind("<Button-1>", on_click)

        icon = self.get_product_icon(name)
        ctk.CTkLabel(left, text=icon, font=("Segoe UI", 22)).pack(side="left", padx=(0, 8))

        display_name = name[:22] + "..." if len(name) > 25 else name
        name_label = ctk.CTkLabel(left, text=display_name, font=("Segoe UI", 12, "bold"),
                                  text_color=self.colors["text"], width=160)
        name_label.pack(side="left")
        name_label.bind("<Button-1>", on_click)

        center = ctk.CTkFrame(card, fg_color="transparent")
        center.pack(side="left", expand=True, padx=5, pady=6)
        center.bind("<Button-1>", on_click)

        # Калории
        f1 = ctk.CTkFrame(center, fg_color="transparent")
        f1.pack(side="left", padx=4)
        ctk.CTkLabel(f1, text="🔥", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(f1, text=f"{calories:.0f}", font=("Segoe UI", 12, "bold"),
                     text_color=self.colors["primary"]).pack(side="left")
        ctk.CTkLabel(f1, text="ккал", font=("Segoe UI", 8), text_color=self.colors["text_secondary"]).pack(side="left")

        # Белки
        f2 = ctk.CTkFrame(center, fg_color="transparent")
        f2.pack(side="left", padx=4)
        ctk.CTkLabel(f2, text="🍗", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(f2, text=f"{protein:.0f}", font=("Segoe UI", 12, "bold"),
                     text_color="#3B82F6").pack(side="left")
        ctk.CTkLabel(f2, text="г", font=("Segoe UI", 8), text_color=self.colors["text_secondary"]).pack(side="left")

        # Жиры
        f3 = ctk.CTkFrame(center, fg_color="transparent")
        f3.pack(side="left", padx=4)
        ctk.CTkLabel(f3, text="🧈", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(f3, text=f"{fat:.0f}", font=("Segoe UI", 12, "bold"),
                     text_color="#F59E0B").pack(side="left")
        ctk.CTkLabel(f3, text="г", font=("Segoe UI", 8), text_color=self.colors["text_secondary"]).pack(side="left")

        # Углеводы
        f4 = ctk.CTkFrame(center, fg_color="transparent")
        f4.pack(side="left", padx=4)
        ctk.CTkLabel(f4, text="🍚", font=("Segoe UI", 12)).pack(side="left")
        ctk.CTkLabel(f4, text=f"{carbs:.0f}", font=("Segoe UI", 12, "bold"),
                     text_color="#8B5CF6").pack(side="left")
        ctk.CTkLabel(f4, text="г", font=("Segoe UI", 8), text_color=self.colors["text_secondary"]).pack(side="left")

        return card

    def on_card_hover(self, card, enter):
        if card is not self.selected_card:
            if enter:
                card.configure(fg_color="#3a3a3a")
            else:
                card.configure(fg_color=self.colors["card_light"])

    def select_product_card(self, card, name, calories, protein, fat, carbs):
        if self.selected_card:
            self.selected_card.configure(fg_color=self.colors["card_light"])
            self.selected_card.border_width = 0

        card.configure(fg_color=self.colors["selected"])
        card.border_width = 2
        card.border_color = self.colors["primary"]

        self.selected_card = card
        self.selected_product = (name, calories, protein, fat, carbs)
        self.selected_label.configure(text=f"✅ Выбран: {name}", text_color=self.colors["primary"])

    def clear_selected_product(self):
        if self.selected_card:
            self.selected_card.configure(fg_color=self.colors["card_light"])
            self.selected_card.border_width = 0
            self.selected_card = None

        self.selected_product = None
        self.selected_label.configure(text="❌ Продукт не выбран", text_color=self.colors["text_secondary"])

    def load_products_list(self, search_text=""):
        for widget in self.products_frame.winfo_children():
            widget.destroy()

        products = self.db.get_products(search_text)
        if not products:
            ctk.CTkLabel(self.products_frame, text="📭 Продукты не найдены",
                        font=("Segoe UI", 13), text_color=self.colors["text_secondary"]).pack(pady=20)
            return

        for name, cal, prot, fat, carbs in products:
            self.create_product_card(self.products_frame, name, cal, prot, fat, carbs)

        self.clear_selected_product()

    def search_products(self, event):
        self.load_products_list(self.product_search.get())

    def add_meal(self):
        if not self.selected_product:
            messagebox.showwarning("Внимание", "Сначала выберите продукт (кликните по карточке)")
            return

        if not self.current_user_id:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя")
            return

        try:
            weight = float(self.weight_entry.get())
            if weight <= 0:
                raise ValueError

            name, cal_per_100, prot_per_100, fat_per_100, carbs_per_100 = self.selected_product
            factor = weight / 100

            product_id = self.db.get_product_id(name)
            self.db.add_meal(self.current_user_id, self.current_date, self.meal_type_var.get(),
                             product_id, weight,
                             cal_per_100 * factor, prot_per_100 * factor,
                             fat_per_100 * factor, carbs_per_100 * factor)

            self.load_today_meals()
            self.update_stats()
            self.update_progress_bars()
            messagebox.showinfo("Успех", f"✅ {name} ({weight:.0f} г) добавлен!")

        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный вес")

    def setup_right_panel(self, parent):
        date_frame = ctk.CTkFrame(parent, fg_color="transparent")
        date_frame.pack(fill="x", padx=15, pady=(15, 10))

        ctk.CTkLabel(date_frame, text="📅 Сегодня", font=("Segoe UI", 18, "bold"),
                     text_color=self.colors["text"]).pack(side="left")

        nav_frame = ctk.CTkFrame(date_frame, fg_color="transparent")
        nav_frame.pack(side="right")

        ctk.CTkButton(nav_frame, text="◀", width=35, height=35, corner_radius=10,
                      command=self.prev_day, fg_color=self.colors["card_light"]).pack(side="left", padx=3)
        self.date_label = ctk.CTkLabel(nav_frame, text="", font=("Segoe UI", 11),
                                       text_color=self.colors["text_secondary"])
        self.date_label.pack(side="left", padx=5)
        ctk.CTkButton(nav_frame, text="▶", width=35, height=35, corner_radius=10,
                      command=self.next_day, fg_color=self.colors["card_light"]).pack(side="left", padx=3)
        ctk.CTkButton(nav_frame, text="📅", width=40, height=35, corner_radius=10,
                      command=self.go_today, fg_color=self.colors["card_light"]).pack(side="left", padx=3)

        self.meal_notebook = ctk.CTkTabview(parent, corner_radius=15)
        self.meal_notebook.pack(fill="both", expand=True, padx=15, pady=10)

        for meal in self.meal_types:
            tab = self.meal_notebook.add(meal)
            frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
            frame.pack(fill="both", expand=True)
            self.meal_frames[meal] = frame

        summary_frame = ctk.CTkFrame(parent, fg_color=self.colors["card_light"], corner_radius=15)
        summary_frame.pack(fill="x", padx=15, pady=10)

        self.summary_labels = {}
        for item in ["🥗 Всего калорий", "🍗 Всего белков", "🧈 Всего жиров", "🍚 Всего углеводов"]:
            frame = ctk.CTkFrame(summary_frame, fg_color="transparent")
            frame.pack(fill="x", padx=12, pady=5)
            ctk.CTkLabel(frame, text=item, font=("Segoe UI", 12), text_color=self.colors["text_secondary"]).pack(side="left")
            self.summary_labels[item] = ctk.CTkLabel(frame, text="0", font=("Segoe UI", 13, "bold"),
                                                     text_color=self.colors["primary"])
            self.summary_labels[item].pack(side="right")

        self.update_date_label()

    def load_today_meals(self):
        for meal_type in self.meal_types:
            frame = self.meal_frames[meal_type]
            for w in frame.winfo_children():
                w.destroy()

            if not self.current_user_id:
                continue

            meals = self.db.get_meals_by_date(self.current_user_id, self.current_date, meal_type)

            for meal_id, name, weight, cal, prot, fat, carbs in meals:
                card = ctk.CTkFrame(frame, corner_radius=10, fg_color="#2a2a2a")
                card.pack(fill="x", pady=3)

                left = ctk.CTkFrame(card, fg_color="transparent")
                left.pack(side="left", padx=10, pady=8)

                ctk.CTkLabel(left, text=self.get_product_icon(name), font=("Segoe UI", 20)).pack(side="left", padx=(0, 8))

                name_frame = ctk.CTkFrame(left, fg_color="transparent")
                name_frame.pack(side="left")
                ctk.CTkLabel(name_frame, text=name, font=("Segoe UI", 12, "bold"),
                            text_color=self.colors["text"]).pack(anchor="w")
                ctk.CTkLabel(name_frame, text=f"{weight:.0f} г", font=("Segoe UI", 9),
                             text_color=self.colors["text_secondary"]).pack(anchor="w")

                right = ctk.CTkFrame(card, fg_color="transparent")
                right.pack(side="right", padx=10, pady=8)

                ctk.CTkLabel(right, text=f"🔥 {cal:.0f} ккал", font=("Segoe UI", 11, "bold"),
                             text_color=self.colors["primary"]).pack(anchor="e")
                ctk.CTkLabel(right, text=f"🍗 {prot:.0f} г   🧈 {fat:.0f} г   🍚 {carbs:.0f} г",
                             font=("Segoe UI", 9), text_color=self.colors["text_secondary"]).pack(anchor="e")

                def delete(mid):
                    if messagebox.askyesno("Подтверждение", "Удалить?"):
                        self.db.delete_meal(mid)
                        self.load_today_meals()
                        self.update_stats()
                        self.update_progress_bars()

                ctk.CTkButton(card, text="🗑️", width=35, height=28, corner_radius=10,
                              fg_color=self.colors["error"], command=lambda mid=meal_id: delete(mid)).pack(side="right", padx=5)

    def update_stats(self):
        if not self.current_user_id:
            return
        total_cal, total_prot, total_fat, total_carbs = self.db.get_daily_totals(self.current_user_id, self.current_date)
        self.summary_labels["🥗 Всего калорий"].configure(text=f"{total_cal:.0f} ккал")
        self.summary_labels["🍗 Всего белков"].configure(text=f"{total_prot:.0f} г")
        self.summary_labels["🧈 Всего жиров"].configure(text=f"{total_fat:.0f} г")
        self.summary_labels["🍚 Всего углеводов"].configure(text=f"{total_carbs:.0f} г")
        self.current_totals = {"calories": total_cal, "protein": total_prot, "fat": total_fat, "carbs": total_carbs}

    def update_progress_bars(self):
        if not self.current_user_id:
            return
        norms = self.db.get_user_norms(self.current_user_id)
        if not norms:
            return

        items = [("Калории", "calories", norms[0]), ("Белки", "protein", norms[1]),
                 ("Жиры", "fat", norms[2]), ("Углеводы", "carbs", norms[3])]
        for name, key, target in items:
            self.progress_bars[name].update(self.current_totals.get(key, 0), target)

    def set_current_user(self, user_id, user_name):
        self.current_user_id = user_id
        self.current_user_name = user_name
        self.user_label.configure(text=f"👤 {user_name}")

        norms = self.db.get_user_norms(user_id)
        if norms:
            self.norm_labels["🔥 Калории"].configure(text=f"{norms[0]:.0f} ккал")
            self.norm_labels["🍗 Белки"].configure(text=f"{norms[1]:.0f} г")
            self.norm_labels["🧈 Жиры"].configure(text=f"{norms[2]:.0f} г")
            self.norm_labels["🍚 Углеводы"].configure(text=f"{norms[3]:.0f} г")

        self.load_today_meals()
        self.update_stats()
        self.update_progress_bars()

    def open_profile(self):
        ProfileDialog(self, self.db, on_save=self.set_current_user)

    def show_stats(self):
        if not self.current_user_id:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя")
            return
        StatsDialog(self, self.db, self.current_user_id)

    def show_user_selector(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("👥 Выбор пользователя")
        dialog.geometry("500x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#0a0a0a")

        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(main, text="👥 Выберите пользователя",
                     font=("Segoe UI", 22, "bold"),
                     text_color="#10B981").pack(pady=(0, 15))

        users_frame = ctk.CTkScrollableFrame(main, fg_color="transparent", height=300)
        users_frame.pack(fill="both", expand=True, pady=10)

        users = self.db.get_all_users()

        if not users:
            ctk.CTkLabel(users_frame, text="📭 Нет пользователей.\nСоздайте нового!",
                         font=("Segoe UI", 14), text_color="#888888").pack(pady=20)
        else:
            for user_id, name in users:
                card = ctk.CTkFrame(users_frame, corner_radius=10, fg_color="#2a2a2a")
                card.pack(fill="x", pady=5, padx=10)

                ctk.CTkLabel(card, text="👤", font=("Segoe UI", 24)).pack(side="left", padx=10, pady=10)

                info_frame = ctk.CTkFrame(card, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=5, pady=10)
                ctk.CTkLabel(info_frame, text=name, font=("Segoe UI", 14, "bold"),
                             text_color="#FFFFFF").pack(anchor="w")

                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(side="right", padx=10)

                ctk.CTkButton(btn_frame, text="Выбрать", width=80, height=30,
                              corner_radius=10, fg_color="#10B981",
                              command=lambda uid=user_id, uname=name: self.select_user(uid, uname, dialog)
                              ).pack(side="left", padx=2)

                ctk.CTkButton(btn_frame, text="✏️", width=40, height=30,
                              corner_radius=10, fg_color="#F59E0B",
                              command=lambda uid=user_id: self.edit_user_profile(uid, dialog)
                              ).pack(side="left", padx=2)

                ctk.CTkButton(btn_frame, text="🗑️", width=40, height=30,
                              corner_radius=10, fg_color="#EF4444",
                              command=lambda uid=user_id, uname=name: self.delete_user(uid, uname, dialog)
                              ).pack(side="left", padx=2)

        ctk.CTkButton(main, text="➕ Создать нового пользователя",
                      command=lambda: self.create_new_user(dialog),
                      height=45, corner_radius=20, fg_color="#10B981",
                      font=("Segoe UI", 13, "bold")).pack(fill="x", pady=10)

    def edit_user_profile(self, user_id, dialog):
        dialog.destroy()
        ProfileDialog(self, self.db, user_id, self.set_current_user)

    def delete_user(self, user_id, user_name, dialog):
        if messagebox.askyesno("Подтверждение",
                               f"Удалить пользователя '{user_name}'?\n\n"
                               f"Все данные о питании будут потеряны!"):
            self.db.cursor.execute("DELETE FROM meals WHERE user_id=?", (user_id,))
            self.db.cursor.execute("DELETE FROM weight_log WHERE user_id=?", (user_id,))
            self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.db.conn.commit()

            if self.current_user_id == user_id:
                self.current_user_id = None
                self.current_user_name = None
                self.user_label.configure(text="")
                self.norm_labels["🔥 Калории"].configure(text="0 ккал")
                self.norm_labels["🍗 Белки"].configure(text="0 г")
                self.norm_labels["🧈 Жиры"].configure(text="0 г")
                self.norm_labels["🍚 Углеводы"].configure(text="0 г")
                self.load_today_meals()
                self.update_stats()
                self.update_progress_bars()

            dialog.destroy()
            self.show_user_selector()

    def create_new_user(self, dialog):
        dialog.destroy()
        ProfileDialog(self, self.db, on_save=self.set_current_user)

    def select_user(self, user_id, user_name, dialog):
        self.set_current_user(user_id, user_name)
        dialog.destroy()

    def edit_current_profile(self):
        if not self.current_user_id:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя")
            return
        ProfileDialog(self, self.db, self.current_user_id, self.set_current_user)

    def prev_day(self):
        self.current_date = (datetime.strptime(self.current_date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        self.update_date_label()
        self.load_today_meals()
        self.update_stats()
        self.update_progress_bars()

    def next_day(self):
        nxt = datetime.strptime(self.current_date, "%Y-%m-%d") + timedelta(days=1)
        if nxt <= datetime.now():
            self.current_date = nxt.strftime("%Y-%m-%d")
            self.update_date_label()
            self.load_today_meals()
            self.update_stats()
            self.update_progress_bars()

    def go_today(self):
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.update_date_label()
        self.load_today_meals()
        self.update_stats()
        self.update_progress_bars()

    def update_date_label(self):
        self.date_label.configure(text=datetime.strptime(self.current_date, "%Y-%m-%d").strftime("%d.%m.%Y"))

    def show_user_manager(self):
        """Показать менеджер пользователей"""
        from views.user_manager import UserManagerDialog
        UserManagerDialog(self, self.db, self.set_current_user)