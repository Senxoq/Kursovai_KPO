import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import calendar
from tkcalendar import DateEntry
import sqlite3


class ProfileDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, user_id=None, on_save=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self.on_save = on_save
        self.is_edit_mode = user_id is not None

        if self.is_edit_mode:
            self.title("✏️ Редактирование профиля")
        else:
            self.title("➕ Создание нового профиля")

        self.geometry("550x650")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#0a0a0a")

        self.setup_ui()

        if self.is_edit_mode:
            self.load_user_data()

    def setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)

        if self.is_edit_mode:
            title_text = "✏️ Редактирование профиля"
        else:
            title_text = "➕ Создание нового профиля"

        ctk.CTkLabel(main, text=title_text, font=("Segoe UI", 24, "bold"),
                     text_color="#10B981").pack(pady=(0, 15))

        scroll_frame = ctk.CTkScrollableFrame(main, fg_color="transparent", height=450)
        scroll_frame.pack(fill="both", expand=True, pady=10)


        ctk.CTkLabel(scroll_frame, text="Имя:", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(scroll_frame, width=450, height=40, corner_radius=15,
                                       fg_color="#1a1a1a")
        self.name_entry.pack(fill="x", pady=(5, 15))


        ctk.CTkLabel(scroll_frame, text="Пол:", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w", pady=(0, 5))
        self.gender_var = tk.StringVar(value="male")
        gender_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        gender_frame.pack(fill="x", pady=(0, 15))
        ctk.CTkRadioButton(gender_frame, text="👨 Мужской", variable=self.gender_var, value="male",
                           text_color="#ffffff").pack(side="left", padx=10)
        ctk.CTkRadioButton(gender_frame, text="👩 Женский", variable=self.gender_var, value="female",
                           text_color="#ffffff").pack(side="left", padx=10)


        ctk.CTkLabel(scroll_frame, text="Возраст (лет):", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w")
        self.age_entry = ctk.CTkEntry(scroll_frame, width=200, height=40, corner_radius=15,
                                      fg_color="#1a1a1a")
        self.age_entry.pack(anchor="w", pady=(5, 15))


        ctk.CTkLabel(scroll_frame, text="Вес (кг):", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w")
        self.weight_entry = ctk.CTkEntry(scroll_frame, width=200, height=40, corner_radius=15,
                                         fg_color="#1a1a1a")
        self.weight_entry.pack(anchor="w", pady=(5, 15))


        ctk.CTkLabel(scroll_frame, text="Рост (см):", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w")
        self.height_entry = ctk.CTkEntry(scroll_frame, width=200, height=40, corner_radius=15,
                                         fg_color="#1a1a1a")
        self.height_entry.pack(anchor="w", pady=(5, 15))


        ctk.CTkLabel(scroll_frame, text="Уровень активности:", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w", pady=(0, 5))
        self.activity_var = tk.StringVar(value="moderate")
        acts = [
            ("🛋️ Сидячий", "sedentary"),
            ("🚶 Легкая 1-2 дня тренировок", "light"),
            ("🏃 Средняя 2-3 дня тренировок", "moderate"),
            ("💪 Высокая 3-4 дня тренировок", "active"),
            ("⚡ Очень высокая 4+ дня тренировок", "very_active")
        ]
        for text, val in acts:
            ctk.CTkRadioButton(scroll_frame, text=text, variable=self.activity_var, value=val,
                               text_color="#ffffff").pack(anchor="w", pady=4)


        ctk.CTkLabel(scroll_frame, text="Цель:", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w", pady=(10, 5))
        self.goal_var = tk.StringVar(value="maintain")
        goals = [
            ("⚖️ Поддержание веса", "maintain"),
            ("⬇️ Похудение", "lose"),
            ("⬆️ Набор массы", "gain")
        ]
        for text, val in goals:
            ctk.CTkRadioButton(scroll_frame, text=text, variable=self.goal_var, value=val,
                               text_color="#ffffff").pack(anchor="w", pady=4)

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        if self.is_edit_mode:
            ctk.CTkButton(btn_frame, text="💾 СОХРАНИТЬ", command=self.save_profile,
                          width=160, height=45, corner_radius=20, fg_color="#10B981",
                          font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)
        else:
            ctk.CTkButton(btn_frame, text="✅ СОЗДАТЬ", command=self.save_profile,
                          width=160, height=45, corner_radius=20, fg_color="#10B981",
                          font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)

        ctk.CTkButton(btn_frame, text="❌ ОТМЕНА", command=self.destroy,
                      width=130, height=45, corner_radius=20, fg_color="#2a2a2a",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)

    def load_user_data(self):

        self.db.cursor.execute("""
            SELECT name, age, gender, weight, height, activity_level, goal
            FROM users WHERE id=?
        """, (self.user_id,))
        user = self.db.cursor.fetchone()

        if user:
            name, age, gender, weight, height, activity, goal = user
            self.name_entry.insert(0, name)
            self.age_entry.insert(0, str(age))
            self.weight_entry.insert(0, str(weight))
            self.height_entry.insert(0, str(height))
            self.gender_var.set(gender)
            self.activity_var.set(activity)
            self.goal_var.set(goal)

            self.title(f"✏️ Редактирование: {name}")

    def save_profile(self):

        try:
            name = self.name_entry.get().strip()
            if not name:
                raise ValueError("Введите имя")

            age = int(self.age_entry.get())
            weight = float(self.weight_entry.get())
            height = float(self.height_entry.get())

            if age <= 0 or weight <= 0 or height <= 0:
                raise ValueError("Значения должны быть положительными")

            gender = self.gender_var.get()
            activity = self.activity_var.get()
            goal = self.goal_var.get()

            from models import Calculator
            bmr = Calculator.calculate_bmr(weight, height, age, gender)
            tdee = Calculator.calculate_tdee(bmr, activity)
            macros = Calculator.calculate_macros(tdee, goal, weight)

            if self.is_edit_mode:
                self.db.cursor.execute('''
                    UPDATE users SET 
                        name=?, age=?, gender=?, weight=?, height=?,
                        activity_level=?, goal=?, daily_calories=?,
                        daily_protein=?, daily_fat=?, daily_carbs=?
                    WHERE id=?
                ''', (name, age, gender, weight, height, activity, goal,
                      macros["calories"], macros["protein"], macros["fat"], macros["carbs"],
                      self.user_id))
                msg = f"✅ Профиль '{name}' обновлён!"
            else:
                self.db.cursor.execute('''
                    INSERT INTO users (name, age, gender, weight, height,
                                      activity_level, goal, daily_calories,
                                      daily_protein, daily_fat, daily_carbs, created_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, age, gender, weight, height, activity, goal,
                      macros["calories"], macros["protein"], macros["fat"], macros["carbs"],
                      datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.user_id = self.db.cursor.lastrowid
                msg = f"✅ Профиль '{name}' создан!"

            self.db.conn.commit()

            messagebox.showinfo("Успех", msg)

            if self.on_save:
                self.on_save(self.user_id, name)

            self.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", str(e))


class StatsDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, user_id):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.user_id = user_id
        self.title("📊 Статистика")
        self.geometry("1000x850")
        self.resizable(True, True)
        self.grab_set()
        self.configure(fg_color="#0a0a0a")

        self.setup_ui()

    def setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(main, text="📊 Статистика питания", font=("Segoe UI", 26, "bold"),
                     text_color="#10B981").pack(pady=(0, 15))

        notebook = ctk.CTkTabview(main, corner_radius=15)
        notebook.pack(fill="both", expand=True)


        pie_tab = notebook.add("🥧 КБЖУ за день")
        self.setup_pie_tab(pie_tab)


        weight_tab = notebook.add("📈 Динамика веса")
        self.setup_weight_tab(weight_tab)


        progress_tab = notebook.add("📊 Прогресс по дням")
        self.setup_progress_tab(progress_tab)


        heatmap_tab = notebook.add("🔥 Календарь активности")
        self.setup_heatmap_tab(heatmap_tab)

    def setup_pie_tab(self, parent):
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(pady=15, fill="x")

        ctk.CTkLabel(control_frame, text="📅 Выберите дату:", font=("Segoe UI", 14)).pack(side="left", padx=10)

        self.pie_date = DateEntry(control_frame, width=15, background='darkblue',
                                  foreground='white', borderwidth=2,
                                  date_pattern='yyyy-mm-dd')
        self.pie_date.pack(side="left", padx=10)
        self.pie_date.set_date(datetime.now())

        ctk.CTkButton(control_frame, text="Обновить", command=self.update_pie_chart,
                      width=120, height=35, corner_radius=15, fg_color="#10B981",
                      font=("Segoe UI", 13, "bold")).pack(side="left", padx=10)

        self.pie_info_card = ctk.CTkFrame(parent, fg_color="#1a1a3e", corner_radius=15)
        self.pie_info_card.pack(fill="x", padx=15, pady=(0, 10))
        self.pie_info_label = ctk.CTkLabel(self.pie_info_card, text="", font=("Segoe UI", 12),
                                           text_color="#888888")
        self.pie_info_label.pack(pady=15)

        self.pie_frame = ctk.CTkFrame(parent, fg_color="#1a1a3e", corner_radius=15)
        self.pie_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.update_pie_chart()

    def update_pie_chart(self):
        for widget in self.pie_frame.winfo_children():
            widget.destroy()

        if not self.user_id:
            return

        date = self.pie_date.get()
        protein, fat, carbs = self.db.get_pie_data(self.user_id, date)
        total = protein + fat + carbs

        norms = self.db.get_user_norms(self.user_id)
        norm_cal = norms[0] if norms else 2000

        self.db.cursor.execute("SELECT SUM(calories) FROM meals WHERE user_id=? AND date=?",
                               (self.user_id, date))
        total_cal = self.db.cursor.fetchone()[0] or 0

        percent_of_norm = (total_cal / norm_cal * 100) if norm_cal > 0 else 0
        self.pie_info_label.configure(
            text=f"📊 За {date} | Всего калорий: {total_cal:.0f} / {norm_cal:.0f} ккал ({percent_of_norm:.0f}% от нормы)"
        )

        if total == 0:
            ctk.CTkLabel(self.pie_frame, text="📭 Нет данных за выбранную дату",
                         font=("Segoe UI", 16), text_color="#888888").pack(expand=True)
            return

        fig, ax = plt.subplots(figsize=(7, 5.5), facecolor="#1a1a3e")
        ax.set_facecolor("#1a1a3e")

        labels = ['🥩 Белки', '🍗 Жиры', '🍚 Углеводы']
        sizes = [protein, fat, carbs]
        colors = ['#10B981', '#F59E0B', '#8B5CF6']
        explode = (0.05, 0.05, 0.05)

        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                          autopct='%1.1f%%', shadow=True, startangle=90,
                                          textprops={'fontsize': 12})

        for text in texts:
            text.set_color('white')
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')

        ax.set_title(f'🥗 Соотношение КБЖУ за {date}', color='white', fontsize=14, pad=20)

        legend_text = f"🥩 Белки: {protein:.1f} г\n🍗 Жиры: {fat:.1f} г\n🍚 Углеводы: {carbs:.1f} г\n━━━━━━━━━━━━━\n🥗 Всего: {total:.1f} г"
        ax.text(1.25, 0.85, legend_text, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#2a2a2a', alpha=0.9),
                color='white', fontweight='bold')

        canvas = FigureCanvasTkAgg(fig, master=self.pie_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def setup_weight_tab(self, parent):

        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(info_frame, text="📈 График динамики веса", font=("Segoe UI", 16, "bold"),
                     text_color="#10B981").pack(side="left", padx=10)


        refresh_btn = ctk.CTkButton(info_frame, text="🔄 Обновить", command=self.update_weight_graph,
                                    width=100, height=32, corner_radius=15, fg_color="#3B82F6",
                                    font=("Segoe UI", 12))
        refresh_btn.pack(side="right", padx=10)


        self.weight_frame = ctk.CTkFrame(parent, fg_color="#1a1a3e", corner_radius=15)
        self.weight_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.update_weight_graph()

    def update_weight_graph(self):

        for widget in self.weight_frame.winfo_children():
            widget.destroy()

        if not self.user_id:
            ctk.CTkLabel(self.weight_frame, text="⚠️ Сначала выберите пользователя",
                         font=("Segoe UI", 16)).pack(expand=True)
            return


        self.db.cursor.execute("""
            SELECT date, weight FROM weight_log 
            WHERE user_id=? ORDER BY date
        """, (self.user_id,))
        data = self.db.cursor.fetchall()


        if not data:
            self.db.cursor.execute("SELECT weight FROM users WHERE id=?", (self.user_id,))
            current_weight = self.db.cursor.fetchone()
            if current_weight:
                data = [(datetime.now().strftime("%Y-%m-%d"), current_weight[0])]
            else:
                ctk.CTkLabel(self.weight_frame, text="📭 Нет данных о весе.\nДобавьте замеры в разделе 'Добавить вес'",
                             font=("Segoe UI", 16), text_color="#888888").pack(expand=True)
                return

        dates = [row[0] for row in data]
        weights = [row[1] for row in data]


        fig, ax = plt.subplots(figsize=(9, 5), facecolor="#1a1a3e")
        ax.set_facecolor("#1a1a3e")


        x = range(len(dates))


        ax.plot(x, weights, marker='o', linewidth=2.5, markersize=8, color="#10B981",
                markerfacecolor='white', markeredgewidth=2, markeredgecolor="#10B981")

        # Заполняем область под графиком
        ax.fill_between(x, weights, alpha=0.3, color="#10B981")

        # Настройка подписей
        ax.set_xlabel('Дата', color='white', fontsize=11)
        ax.set_ylabel('Вес (кг)', color='white', fontsize=11)
        ax.set_title('Динамика изменения веса', color='white', fontsize=13, pad=15)


        ax.grid(True, alpha=0.2, color='white', linestyle='--')
        ax.yaxis.grid(True, alpha=0.3)


        ax.tick_params(axis='x', colors='#888888', labelsize=9)
        ax.tick_params(axis='y', colors='#888888', labelsize=10)


        step = max(1, len(dates) // 10)
        ax.set_xticks(x[::step])
        ax.set_xticklabels([dates[i][5:] for i in range(0, len(dates), step)], rotation=45, ha='right')


        for spine in ax.spines.values():
            spine.set_color('#888888')
            spine.set_linewidth(0.5)


        for i, (date, weight) in enumerate(zip(dates, weights)):
            ax.annotate(f'{weight:.1f}', (i, weight), textcoords="offset points",
                        xytext=(0, 10), ha='center', color='white', fontsize=8)


        if len(weights) > 1:
            from numpy import polyfit
            try:
                coeffs = polyfit(range(len(weights)), weights, 1)
                trend_line = [coeffs[0] * i + coeffs[1] for i in range(len(weights))]
                ax.plot(x, trend_line, '--', linewidth=1.5, color='#F59E0B', alpha=0.7, label='Линия тренда')
                ax.legend(loc='upper right', facecolor='#1a1a3e', labelcolor='white', fontsize=10)


                if len(weights) >= 2:
                    first_weight = weights[0]
                    last_weight = weights[-1]
                    change = last_weight - first_weight
                    if change > 0:
                        trend_text = f"📈 Изменение: +{change:.1f} кг"
                        trend_color = "#EF4444"
                    elif change < 0:
                        trend_text = f"📉 Изменение: {change:.1f} кг"
                        trend_color = "#10B981"
                    else:
                        trend_text = f"➖ Изменение: 0 кг"
                        trend_color = "#888888"


                    ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, fontsize=10,
                            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='#1a1a3e', alpha=0.8),
                            color=trend_color)
            except:
                pass

        canvas = FigureCanvasTkAgg(fig, master=self.weight_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def setup_progress_tab(self, parent):
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(pady=15, fill="x")

        ctk.CTkLabel(control_frame, text="📊 Прогресс за последние 30 дней", font=("Segoe UI", 18, "bold"),
                     text_color="#10B981").pack(side="left", padx=10)

        period_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        period_frame.pack(side="right", padx=10)

        ctk.CTkLabel(period_frame, text="Период:", font=("Segoe UI", 12)).pack(side="left", padx=5)
        self.period_var = tk.StringVar(value="30")
        period_combo = ctk.CTkComboBox(period_frame, values=["7", "14", "30", "60", "90"],
                                       variable=self.period_var, width=80,
                                       command=lambda x: self.update_progress_chart())
        period_combo.pack(side="left", padx=5)

        self.progress_frame = ctk.CTkFrame(parent, fg_color="#1a1a3e", corner_radius=15)
        self.progress_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.update_progress_chart()

    def update_progress_chart(self):
        for widget in self.progress_frame.winfo_children():
            widget.destroy()

        if not self.user_id:
            return

        days = int(self.period_var.get())
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days - 1)

        dates = []
        calories_data = []

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            self.db.cursor.execute("SELECT SUM(calories) FROM meals WHERE user_id=? AND date=?",
                                   (self.user_id, date_str))
            total = self.db.cursor.fetchone()[0] or 0
            dates.append(current_date.strftime("%d.%m"))
            calories_data.append(total)
            current_date += timedelta(days=1)

        norm = self.db.get_user_norms(self.user_id)
        norm_cal = norm[0] if norm else 2000

        fig, ax = plt.subplots(figsize=(10, 5), facecolor="#1a1a3e")
        ax.set_facecolor("#1a1a3e")

        under_norm = [min(cal, norm_cal) for cal in calories_data]
        over_norm = [max(0, cal - norm_cal) for cal in calories_data]

        bars1 = ax.bar(range(len(dates)), under_norm, color="#3B82F6", alpha=0.8,
                       edgecolor='white', linewidth=0.5, label='В пределах нормы')
        bars2 = ax.bar(range(len(dates)), over_norm, bottom=under_norm, color="#EF4444", alpha=0.8,
                       edgecolor='white', linewidth=0.5, label='Превышение нормы')

        ax.axhline(y=norm_cal, color='#F59E0B', linestyle='--', linewidth=2.5,
                   label=f'🎯 Норма: {norm_cal} ккал')

        ax.set_xlabel('Дата', color='white', fontsize=11)
        ax.set_ylabel('Калории', color='white', fontsize=11)
        ax.set_title(f'Ежедневное потребление калорий за {days} дней', color='white', fontsize=13, pad=15)
        ax.set_xticks(range(0, len(dates), max(1, len(dates) // 10)))
        ax.set_xticklabels([dates[i] for i in range(0, len(dates), max(1, len(dates) // 10))],
                           rotation=45, ha='right', color='#888888', fontsize=9)
        ax.tick_params(axis='y', colors='#888888', labelsize=10)
        ax.legend(loc='upper right', facecolor='#1a1a3e', labelcolor='white', fontsize=10)

        ax.yaxis.grid(True, alpha=0.2, color='white', linestyle='--')
        ax.xaxis.grid(False)

        for spine in ax.spines.values():
            spine.set_color('#888888')
            spine.set_linewidth(0.5)

        for i, (bar, val) in enumerate(zip(bars1, calories_data)):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                        f'{int(val)}', ha='center', va='bottom', color='white', fontsize=8)

        canvas = FigureCanvasTkAgg(fig, master=self.progress_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def setup_heatmap_tab(self, parent):
        control_frame = ctk.CTkFrame(parent, fg_color="transparent")
        control_frame.pack(pady=15, fill="x")

        ctk.CTkLabel(control_frame, text="🔥 Календарь активности",
                     font=("Segoe UI", 18, "bold"), text_color="#10B981").pack(side="left", padx=10)

        year_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        year_frame.pack(side="right", padx=10)

        ctk.CTkLabel(year_frame, text="Год:", font=("Segoe UI", 12)).pack(side="left", padx=5)
        current_year = datetime.now().year
        self.heatmap_year_var = tk.StringVar(value=str(current_year))
        year_combo = ctk.CTkComboBox(year_frame, values=[str(y) for y in range(current_year - 2, current_year + 1)],
                                     variable=self.heatmap_year_var, width=80,
                                     command=lambda x: self.update_heatmap())
        year_combo.pack(side="left", padx=5)

        self.heatmap_frame = ctk.CTkFrame(parent, fg_color="#1a1a3e", corner_radius=15)
        self.heatmap_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.update_heatmap()

    def update_heatmap(self):
        for widget in self.heatmap_frame.winfo_children():
            widget.destroy()

        if not self.user_id:
            ctk.CTkLabel(self.heatmap_frame, text="⚠️ Сначала выберите пользователя",
                         font=("Segoe UI", 16)).pack(expand=True)
            return

        year = int(self.heatmap_year_var.get())

        heat_scroll = ctk.CTkScrollableFrame(self.heatmap_frame, fg_color="transparent", height=500)
        heat_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(heat_scroll, text=f"📅 Календарь активности за {year} год",
                     font=("Segoe UI", 16, "bold"), text_color="#10B981").pack(pady=10)

        self.db.cursor.execute("""
            SELECT date, SUM(calories) as total_calories
            FROM meals 
            WHERE user_id=? AND strftime('%Y', date)=?
            GROUP BY date
        """, (self.user_id, str(year)))

        meals_data = {row[0]: row[1] for row in self.db.cursor.fetchall()}

        norms = self.db.get_user_norms(self.user_id)
        daily_norm = norms[0] if norms else 2000

        def get_color_for_day(date_str):
            if date_str not in meals_data:
                return "#2a2a2a"
            calories = meals_data[date_str]
            percent = (calories / daily_norm) * 100 if daily_norm > 0 else 0

            if percent >= 100:
                return "#10B981"
            elif percent >= 75:
                return "#34D399"
            elif percent >= 50:
                return "#F59E0B"
            elif percent >= 25:
                return "#F97316"
            else:
                return "#EF4444"

        months_frame = ctk.CTkFrame(heat_scroll, fg_color="transparent")
        months_frame.pack(fill="both", expand=True)

        for month in range(1, 13):
            month_frame = ctk.CTkFrame(months_frame, fg_color="#1a1a3e", corner_radius=10)
            row = (month - 1) // 3
            col = (month - 1) % 3
            month_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            month_name = calendar.month_name[month]
            ctk.CTkLabel(month_frame, text=month_name, font=("Segoe UI", 14, "bold"),
                         text_color="#10B981").pack(pady=(10, 5))

            days_grid = ctk.CTkFrame(month_frame, fg_color="transparent")
            days_grid.pack(pady=5, padx=10)

            weekdays = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            for i, wd in enumerate(weekdays):
                ctk.CTkLabel(days_grid, text=wd, font=("Segoe UI", 9, "bold"),
                             text_color="#888888", width=30).grid(row=0, column=i, padx=2, pady=2)

            cal = calendar.monthcalendar(year, month)

            for week_idx, week in enumerate(cal):
                for day_idx, day in enumerate(week):
                    if day == 0:
                        empty_btn = ctk.CTkButton(days_grid, text="", width=30, height=30,
                                                  state="disabled", fg_color="#1a1a3e")
                        empty_btn.grid(row=week_idx + 1, column=day_idx, padx=2, pady=2)
                    else:
                        date_str = f"{year}-{month:02d}-{day:02d}"
                        color = get_color_for_day(date_str)

                        day_btn = ctk.CTkButton(days_grid, text=str(day), width=30, height=30,
                                                fg_color=color, hover_color=color,
                                                font=("Segoe UI", 10, "bold"))
                        day_btn.grid(row=week_idx + 1, column=day_idx, padx=2, pady=2)

                        day_btn.bind("<Button-1>",
                                     lambda e, d=date_str, c=meals_data.get(date_str, 0):
                                     self.show_day_details(d, daily_norm, c))

            month_days = 0
            month_completed = 0
            for day in range(1, calendar.monthrange(year, month)[1] + 1):
                date_str = f"{year}-{month:02d}-{day:02d}"
                if date_str in meals_data:
                    month_days += 1
                    if meals_data[date_str] >= daily_norm:
                        month_completed += 1

            if month_days > 0:
                percent = (month_completed / month_days) * 100
                stats_text = f"✅ {month_completed}/{month_days} дней ({percent:.0f}%)"
                stats_color = "#10B981" if percent >= 70 else "#F59E0B" if percent >= 40 else "#EF4444"
            else:
                stats_text = "📭 Нет данных"
                stats_color = "#888888"

            ctk.CTkLabel(month_frame, text=stats_text, font=("Segoe UI", 10),
                         text_color=stats_color).pack(pady=(5, 10))

        legend_frame = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
        legend_frame.pack(pady=10, fill="x")

        ctk.CTkLabel(legend_frame, text="Выполнение плана:", font=("Segoe UI", 12, "bold"),
                     text_color="#FFFFFF").pack(side="left", padx=10)

        legend_items = [
            ("#10B981", "✅ Выполнено (≥100%)"),
            ("#34D399", "🟢 Хорошо (75-99%)"),
            ("#F59E0B", "🟡 Средне (50-74%)"),
            ("#F97316", "🟠 Ниже среднего (25-49%)"),
            ("#EF4444", "🔴 Плохо (<25%)"),
            ("#2a2a2a", "⚫ Нет данных")
        ]

        for color, label in legend_items:
            frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            frame.pack(side="left", padx=15)
            box = ctk.CTkFrame(frame, width=20, height=20, corner_radius=4, fg_color=color)
            box.pack(side="left", padx=2)
            ctk.CTkLabel(frame, text=label, font=("Segoe UI", 10),
                         text_color="#888888").pack(side="left", padx=2)

        total_days = len(meals_data)
        completed_days = sum(1 for date_str, cal in meals_data.items() if cal >= daily_norm)
        if total_days > 0:
            total_percent = (completed_days / total_days) * 100
            stats_frame = ctk.CTkFrame(self.heatmap_frame, fg_color="transparent")
            stats_frame.pack(pady=10)

            ctk.CTkLabel(stats_frame, text=f"📊 Всего дней с записями: {total_days}",
                         font=("Segoe UI", 11), text_color="#888888").pack(side="left", padx=10)
            ctk.CTkLabel(stats_frame, text=f"🏆 Дней с выполненным планом: {completed_days} ({total_percent:.0f}%)",
                         font=("Segoe UI", 11), text_color="#10B981").pack(side="left", padx=10)

    def show_day_details(self, date_str, daily_norm, calories):
        dialog = ctk.CTkToplevel(self)
        dialog.title("📋 Детали дня")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.grab_set()
        dialog.configure(fg_color="#0a0a0a")

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (350 // 2)
        dialog.geometry(f"+{x}+{y}")

        main = ctk.CTkFrame(dialog, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%d %B %Y")
        weekday = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"][
            date_obj.weekday()]

        ctk.CTkLabel(main, text=f"📅 {formatted_date}", font=("Segoe UI", 20, "bold"),
                     text_color="#10B981").pack(pady=(0, 10))
        ctk.CTkLabel(main, text=weekday, font=("Segoe UI", 14), text_color="#888888").pack(pady=(0, 20))

        info_frame = ctk.CTkFrame(main, fg_color="#1a1a3e", corner_radius=15)
        info_frame.pack(fill="both", expand=True, pady=10)

        if calories > 0:
            percent = (calories / daily_norm) * 100 if daily_norm > 0 else 0

            if percent >= 100:
                status = "✅ План выполнен!"
                status_color = "#10B981"
                emoji = "🎉"
            elif percent >= 75:
                status = "🟢 Хороший результат"
                status_color = "#34D399"
                emoji = "👍"
            elif percent >= 50:
                status = "🟡 Можно лучше"
                status_color = "#F59E0B"
                emoji = "🤔"
            elif percent >= 25:
                status = "🟠 Ниже нормы"
                status_color = "#F97316"
                emoji = "😐"
            else:
                status = "🔴 Плохой результат"
                status_color = "#EF4444"
                emoji = "😔"

            row1 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row1.pack(fill="x", padx=15, pady=(15, 5))
            ctk.CTkLabel(row1, text="🔥 Калории:", font=("Segoe UI", 14), width=120).pack(side="left")
            ctk.CTkLabel(row1, text=f"{calories:.0f} / {daily_norm:.0f} ккал",
                         font=("Segoe UI", 14, "bold"), text_color="#3B82F6").pack(side="right")

            progress_bar = ctk.CTkProgressBar(info_frame, width=300, height=14, corner_radius=7,
                                              progress_color="#3B82F6")
            progress_bar.pack(pady=10)
            progress_bar.set(min(1.0, percent / 100))

            row3 = ctk.CTkFrame(info_frame, fg_color="transparent")
            row3.pack(fill="x", padx=15, pady=(5, 15))
            ctk.CTkLabel(row3, text=f"{emoji} Статус:", font=("Segoe UI", 14), width=120).pack(side="left")
            ctk.CTkLabel(row3, text=status, font=("Segoe UI", 14, "bold"),
                         text_color=status_color).pack(side="right")

            def go_to_day():
                self.parent.current_date = date_str
                self.parent.update_date_label()
                self.parent.load_today_meals()
                self.parent.update_stats()
                self.parent.update_progress_bars()
                dialog.destroy()
                self.destroy()

            ctk.CTkButton(main, text="📅 Перейти к этому дню", command=go_to_day,
                          width=220, height=40, corner_radius=20, fg_color="#10B981",
                          font=("Segoe UI", 13, "bold")).pack(pady=(15, 0))
        else:
            ctk.CTkLabel(info_frame, text="📭 Нет записей о питании",
                         font=("Segoe UI", 16), text_color="#888888").pack(pady=40)

            def add_meal_for_day():
                self.parent.current_date = date_str
                self.parent.update_date_label()
                self.parent.load_today_meals()
                self.parent.update_stats()
                self.parent.update_progress_bars()
                dialog.destroy()
                self.destroy()
                self.parent.meal_notebook._tabview._segmented_button._buttons_dict["➕ Добавить"].invoke()

            ctk.CTkButton(main, text="➕ Добавить приём пищи", command=add_meal_for_day,
                          width=220, height=40, corner_radius=20, fg_color="#10B981",
                          font=("Segoe UI", 13, "bold")).pack(pady=15)

        ctk.CTkButton(main, text="Закрыть", command=dialog.destroy,
                      width=150, height=35, corner_radius=15, fg_color="#2a2a2a",
                      font=("Segoe UI", 13)).pack(pady=(15, 0))


class CustomProductDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, on_success):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.on_success = on_success
        self.title("✨ Добавить свой продукт")
        self.geometry("500x550")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#0a0a0a")

        self.setup_ui()

    def setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(main, text="✨ Новый продукт", font=("Segoe UI", 24, "bold"),
                     text_color="#10B981").pack(pady=(0, 25))


        icon_frame = ctk.CTkFrame(main, fg_color="transparent")
        icon_frame.pack(fill="x", pady=10)

        ctk.CTkLabel(icon_frame, text="Иконка:", width=100, font=("Segoe UI", 13),
                     text_color="#ffffff").pack(side="left")

        self.icon_var = tk.StringVar(value="🍽️")
        icon_combo = ctk.CTkComboBox(icon_frame, values=["🍽️", "🍗", "🥩", "🐟", "🍚", "🥣", "🥚", "🥛", "🍎", "🍌", "🍅", "🥒", "🥔", "🍞"],
                                     variable=self.icon_var, width=120)
        icon_combo.pack(side="left", padx=10)


        ctk.CTkLabel(main, text="Название продукта:", font=("Segoe UI", 14, "bold"),
                     text_color="#ffffff").pack(anchor="w")
        self.name_entry = ctk.CTkEntry(main, width=400, height=40, corner_radius=15,
                                       fg_color="#1a1a1a", font=("Segoe UI", 13))
        self.name_entry.pack(fill="x", pady=(5, 20))


        ctk.CTkLabel(main, text="Пищевая ценность на 100 г:", font=("Segoe UI", 16, "bold"),
                     text_color="#10B981").pack(anchor="w", pady=(0, 15))


        cal_frame = ctk.CTkFrame(main, fg_color="transparent")
        cal_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(cal_frame, text="🔥 Калории:", width=100, font=("Segoe UI", 13),
                     text_color="#ffffff").pack(side="left", padx=10)
        self.cal_entry = ctk.CTkEntry(cal_frame, width=150, height=35, corner_radius=10,
                                      fg_color="#1a1a1a", font=("Segoe UI", 13))
        self.cal_entry.pack(side="left", padx=10)
        ctk.CTkLabel(cal_frame, text="ккал", font=("Segoe UI", 13), text_color="#888888").pack(side="left", padx=5)


        prot_frame = ctk.CTkFrame(main, fg_color="transparent")
        prot_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(prot_frame, text="🍗 Белки:", width=100, font=("Segoe UI", 13),
                     text_color="#ffffff").pack(side="left", padx=10)
        self.prot_entry = ctk.CTkEntry(prot_frame, width=150, height=35, corner_radius=10,
                                       fg_color="#1a1a1a", font=("Segoe UI", 13))
        self.prot_entry.pack(side="left", padx=10)
        ctk.CTkLabel(prot_frame, text="г", font=("Segoe UI", 13), text_color="#888888").pack(side="left", padx=5)


        fat_frame = ctk.CTkFrame(main, fg_color="transparent")
        fat_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(fat_frame, text="🧈 Жиры:", width=100, font=("Segoe UI", 13),
                     text_color="#ffffff").pack(side="left", padx=10)
        self.fat_entry = ctk.CTkEntry(fat_frame, width=150, height=35, corner_radius=10,
                                      fg_color="#1a1a1a", font=("Segoe UI", 13))
        self.fat_entry.pack(side="left", padx=10)
        ctk.CTkLabel(fat_frame, text="г", font=("Segoe UI", 13), text_color="#888888").pack(side="left", padx=5)


        carb_frame = ctk.CTkFrame(main, fg_color="transparent")
        carb_frame.pack(fill="x", pady=5)
        ctk.CTkLabel(carb_frame, text="🍚 Углеводы:", width=100, font=("Segoe UI", 13),
                     text_color="#ffffff").pack(side="left", padx=10)
        self.carbs_entry = ctk.CTkEntry(carb_frame, width=150, height=35, corner_radius=10,
                                        fg_color="#1a1a1a", font=("Segoe UI", 13))
        self.carbs_entry.pack(side="left", padx=10)
        ctk.CTkLabel(carb_frame, text="г", font=("Segoe UI", 13), text_color="#888888").pack(side="left", padx=5)

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(30, 0))

        def delete_product(self, product_name, product_id):
            self.db.cursor.execute("SELECT COUNT(*) FROM meals WHERE product_id=?", (product_id,))
            count = self.db.cursor.fetchone()[0]

            if count > 0:
                # Предлагаем два варианта
                if messagebox.askyesno("Внимание",
                                       f"Продукт '{product_name}' использован в {count} приёмах пищи.\n\n"
                                       "Удалить его нельзя, но можно СКРЫТЬ из списка?\n\n"
                                       "Да - скрыть, Нет - оставить как есть"):

                    self.db.cursor.execute("UPDATE products SET hidden=1 WHERE id=?", (product_id,))
                    self.db.conn.commit()
                    messagebox.showinfo("Успех", f"Продукт '{product_name}' скрыт из списка")
            else:

                self.db.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.db.conn.commit()
                messagebox.showinfo("Успех", f"Продукт '{product_name}' удалён")

            self.load_products_list()

        def save_product():
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название продукта")
                return

            try:
                calories = float(self.cal_entry.get())
                protein = float(self.prot_entry.get())
                fat = float(self.fat_entry.get())
                carbs = float(self.carbs_entry.get())
                if calories < 0 or protein < 0 or fat < 0 or carbs < 0:
                    raise ValueError
            except:
                messagebox.showerror("Ошибка", "Введите корректные положительные числа")
                return

            try:
                self.db.cursor.execute('''
                    INSERT INTO products (name, calories, protein, fat, carbs)
                    VALUES (?, ?, ?, ?, ?)
                ''', (name, calories, protein, fat, carbs))
                self.db.conn.commit()

                messagebox.showinfo("Успех", f"✅ Продукт '{name}' добавлен в базу!")
                self.on_success()
                self.destroy()
            except sqlite3.IntegrityError:
                messagebox.showerror("Ошибка", f"Продукт '{name}' уже существует")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")

        ctk.CTkButton(btn_frame, text="💾 СОХРАНИТЬ", command=save_product,
                      width=160, height=45, corner_radius=25, fg_color="#10B981",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)

        ctk.CTkButton(btn_frame, text="❌ ОТМЕНА", command=self.destroy,
                      width=130, height=45, corner_radius=25, fg_color="#2a2a2a",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)