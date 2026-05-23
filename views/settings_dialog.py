import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import json
import os


class SettingsDialog(ctk.CTkToplevel):

    SETTINGS_FILE = "app_settings.json"

    def __init__(self, parent, on_theme_change=None):
        super().__init__(parent)
        self.parent = parent
        self.on_theme_change = on_theme_change

        self.title("⚙️ Настройки")
        self.geometry("580x550")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#0a0a0a")

        self.load_settings()
        self.setup_ui()
        self.preview_settings()

    def load_settings(self):

        default_settings = {
            "theme": "dark",
            "accent_color": "green",
            "auto_save": True,
            "notifications": False,
            "default_meal": "Завтрак",
            "default_weight": 100
        }

        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    default_settings.update(saved)
            except:
                pass

        self.settings = default_settings
        self.current_theme = self.settings["theme"]
        self.current_accent = self.settings["accent_color"]
        self.temp_theme = self.current_theme
        self.temp_accent = self.current_accent
        self.temp_auto_save = self.settings["auto_save"]
        self.temp_notifications = self.settings["notifications"]
        self.temp_default_meal = self.settings["default_meal"]
        self.temp_default_weight = self.settings["default_weight"]

    def preview_settings(self):

        ctk.set_appearance_mode(self.temp_theme)
        color_map = {"green": "green", "blue": "blue", "dark-blue": "dark-blue"}
        ctk.set_default_color_theme(color_map.get(self.temp_accent, "green"))

    def apply_temp_settings(self):
        self.preview_settings()
        self.apply_indicator.configure(text="✓ Изменения применены (временно)",
                                       text_color="#F59E0B")
        self.apply_indicator.after(2000, lambda: self.apply_indicator.configure(text=""))

    def save_settings(self):

        self.current_theme = self.temp_theme
        self.current_accent = self.temp_accent
        self.settings["theme"] = self.current_theme
        self.settings["accent_color"] = self.current_accent
        self.settings["auto_save"] = self.temp_auto_save
        self.settings["notifications"] = self.temp_notifications
        self.settings["default_meal"] = self.temp_default_meal
        self.settings["default_weight"] = self.temp_default_weight

        with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)


        self.apply_theme()

        if self.on_theme_change:
            self.on_theme_change(self.settings)

        messagebox.showinfo("Успех", "✅ Настройки сохранены!\n\n"
                                     "Они будут применены при следующем запуске приложения.")
        self.destroy()

    def apply_theme(self):

        ctk.set_appearance_mode(self.current_theme)
        color_map = {"green": "green", "blue": "blue", "dark-blue": "dark-blue"}
        ctk.set_default_color_theme(color_map.get(self.current_accent, "green"))

    def cancel_settings(self):

        if messagebox.askyesno("Подтверждение",
                               "Отменить все изменения?\nНастройки вернутся к сохранённым ранее."):
            self.destroy()

    def reset_to_default(self):

        if messagebox.askyesno("Сброс настроек",
                               "Сбросить все настройки к значениям по умолчанию?"):
            self.temp_theme = "dark"
            self.temp_accent = "green"
            self.temp_auto_save = True
            self.temp_notifications = False
            self.temp_default_meal = "Завтрак"
            self.temp_default_weight = 100


            self.theme_var.set("dark")
            self.color_var.set("green")
            self.auto_save_var.set(True)
            self.notifications_var.set(False)
            self.default_meal_var.set("Завтрак")
            self.default_weight_var.set("100")


            self.preview_settings()
            self.apply_indicator.configure(text="✓ Сброшено к настройкам по умолчанию",
                                           text_color="#10B981")
            self.apply_indicator.after(2000, lambda: self.apply_indicator.configure(text=""))

    def setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=25, pady=25)

        ctk.CTkLabel(main, text="⚙️ Настройки приложения",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#10B981").pack(pady=(0, 10))


        self.apply_indicator = ctk.CTkLabel(main, text="", font=("Segoe UI", 11))
        self.apply_indicator.pack(pady=(0, 5))


        control_btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        control_btn_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(control_btn_frame, text="👁️ Предпросмотр",
                      command=self.apply_temp_settings,
                      width=120, height=32, corner_radius=15,
                      fg_color="#3B82F6", font=("Segoe UI", 12)).pack(side="left", padx=5)

        ctk.CTkButton(control_btn_frame, text="🔄 Сброс",
                      command=self.reset_to_default,
                      width=100, height=32, corner_radius=15,
                      fg_color="#F59E0B", font=("Segoe UI", 12)).pack(side="left", padx=5)


        scroll_frame = ctk.CTkScrollableFrame(main, fg_color="transparent", height=380)
        scroll_frame.pack(fill="both", expand=True, pady=10)


        ctk.CTkLabel(scroll_frame, text="🎨 Внешний вид", font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(10, 10))


        theme_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        theme_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(theme_frame, text="Тема:", width=100,
                     font=("Segoe UI", 13)).pack(side="left")
        self.theme_var = tk.StringVar(value=self.temp_theme)
        theme_combo = ctk.CTkComboBox(theme_frame, values=["dark", "light", "system"],
                                      variable=self.theme_var, width=160,
                                      command=self.on_theme_changed)
        theme_combo.pack(side="left")


        color_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        color_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(color_frame, text="Акцентный цвет:", width=100,
                     font=("Segoe UI", 13)).pack(side="left")
        self.color_var = tk.StringVar(value=self.temp_accent)
        color_combo = ctk.CTkComboBox(color_frame, values=["green", "blue", "dark-blue"],
                                      variable=self.color_var, width=160,
                                      command=self.on_color_changed)
        color_combo.pack(side="left")


        ctk.CTkFrame(scroll_frame, height=1, fg_color="#2a2a2a").pack(fill="x", pady=15)

        ctk.CTkLabel(scroll_frame, text="⚡ Поведение", font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(10, 10))


        self.auto_save_var = tk.BooleanVar(value=self.temp_auto_save)
        ctk.CTkCheckBox(scroll_frame, text="Автоматически сохранять изменения",
                        variable=self.auto_save_var,
                        font=("Segoe UI", 13),
                        command=self.on_auto_save_changed).pack(anchor="w", pady=5)


        self.notifications_var = tk.BooleanVar(value=self.temp_notifications)
        ctk.CTkCheckBox(scroll_frame, text="Показывать уведомления",
                        variable=self.notifications_var,
                        font=("Segoe UI", 13),
                        command=self.on_notifications_changed).pack(anchor="w", pady=5)


        ctk.CTkFrame(scroll_frame, height=1, fg_color="#2a2a2a").pack(fill="x", pady=15)


        ctk.CTkLabel(scroll_frame, text="🔧 Значения по умолчанию", font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(10, 10))


        meal_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        meal_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(meal_frame, text="Приём пищи:", width=120,
                     font=("Segoe UI", 13)).pack(side="left")
        self.default_meal_var = tk.StringVar(value=self.temp_default_meal)
        meal_combo = ctk.CTkComboBox(meal_frame, values=["Завтрак", "Обед", "Ужин", "Перекус"],
                                     variable=self.default_meal_var, width=160,
                                     command=self.on_default_meal_changed)
        meal_combo.pack(side="left")


        weight_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        weight_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(weight_frame, text="Вес порции (г):", width=120,
                     font=("Segoe UI", 13)).pack(side="left")
        self.default_weight_var = tk.StringVar(value=str(self.temp_default_weight))
        weight_entry = ctk.CTkEntry(weight_frame, textvariable=self.default_weight_var, width=160)
        weight_entry.pack(side="left")
        weight_entry.bind("<KeyRelease>", lambda e: self.on_default_weight_changed())


        ctk.CTkFrame(scroll_frame, height=1, fg_color="#2a2a2a").pack(fill="x", pady=15)


        ctk.CTkLabel(scroll_frame, text="ℹ️ О программе", font=("Segoe UI", 16, "bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(10, 5))

        about_text = "CalorieFlow v1.0\nКалькулятор калорий и трекер питания\n\n"
        about_text += "Разработано в рамках курсовой работы\n"
        about_text += "© 2025, Купченко Архип"

        ctk.CTkLabel(scroll_frame, text=about_text, font=("Segoe UI", 11),
                     text_color="#888888", justify="left").pack(anchor="w", pady=5)


        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        ctk.CTkButton(btn_frame, text="💾 СОХРАНИТЬ", command=self.save_settings,
                      width=150, height=45, corner_radius=20, fg_color="#10B981",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)

        ctk.CTkButton(btn_frame, text="❌ ОТМЕНА", command=self.cancel_settings,
                      width=130, height=45, corner_radius=20, fg_color="#2a2a2a",
                      font=("Segoe UI", 14, "bold")).pack(side="right", padx=8)

    def on_theme_changed(self, choice):
        self.temp_theme = choice
        self.apply_indicator.configure(text="⚠️ Изменения не применены. Нажмите 'Предпросмотр'",
                                       text_color="#F59E0B")

    def on_color_changed(self, choice):
        self.temp_accent = choice
        self.apply_indicator.configure(text="⚠️ Изменения не применены. Нажмите 'Предпросмотр'",
                                       text_color="#F59E0B")

    def on_auto_save_changed(self):
        self.temp_auto_save = self.auto_save_var.get()

    def on_notifications_changed(self):
        self.temp_notifications = self.notifications_var.get()

    def on_default_meal_changed(self, choice):
        self.temp_default_meal = choice

    def on_default_weight_changed(self):
        try:
            self.temp_default_weight = int(self.default_weight_var.get())
        except:
            pass