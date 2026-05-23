import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox


class UserManagerDialog(ctk.CTkToplevel):


    def __init__(self, parent, db, on_user_selected=None):
        super().__init__(parent)
        self.parent = parent
        self.db = db
        self.on_user_selected = on_user_selected

        self.title("👥 Управление пользователями")
        self.geometry("600x550")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#0a0a0a")

        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)


        ctk.CTkLabel(main, text="👥 Управление пользователями",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#10B981").pack(pady=(0, 15))


        control_frame = ctk.CTkFrame(main, fg_color="transparent")
        control_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(control_frame, text="➕ Создать нового",
                      command=self.create_user,
                      width=140, height=35, corner_radius=15,
                      fg_color="#10B981", font=("Segoe UI", 12, "bold")).pack(side="left", padx=5)

        ctk.CTkButton(control_frame, text="🔄 Обновить список",
                      command=self.load_users,
                      width=130, height=35, corner_radius=15,
                      fg_color="#2a2a2a", font=("Segoe UI", 12)).pack(side="left", padx=5)


        users_label = ctk.CTkLabel(main, text="📋 Список пользователей",
                                   font=("Segoe UI", 14, "bold"),
                                   text_color="#ffffff")
        users_label.pack(anchor="w", pady=(10, 5))

        self.users_frame = ctk.CTkScrollableFrame(main, fg_color="transparent", height=300)
        self.users_frame.pack(fill="both", expand=True, pady=5)


        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(15, 0))

        ctk.CTkButton(btn_frame, text="✓ Выбрать пользователя",
                      command=self.select_user,
                      width=180, height=40, corner_radius=20,
                      fg_color="#10B981", font=("Segoe UI", 13, "bold")).pack(side="right", padx=8)

        ctk.CTkButton(btn_frame, text="✖️ Закрыть",
                      command=self.destroy,
                      width=120, height=40, corner_radius=20,
                      fg_color="#2a2a2a", font=("Segoe UI", 13)).pack(side="right", padx=8)

    def load_users(self):

        for widget in self.users_frame.winfo_children():
            widget.destroy()

        users = self.db.get_all_users()

        if not users:
            empty_label = ctk.CTkLabel(self.users_frame, text="📭 Нет пользователей.\nНажмите 'Создать нового'",
                                       font=("Segoe UI", 14), text_color="#888888")
            empty_label.pack(pady=30)
            return

        for user_id, name in users:

            self.db.cursor.execute("SELECT age, weight, height FROM users WHERE id=?", (user_id,))
            user_data = self.db.cursor.fetchone()
            age = user_data[0] if user_data else "?"
            weight = user_data[1] if user_data else "?"
            height = user_data[2] if user_data else "?"


            card = ctk.CTkFrame(self.users_frame, corner_radius=12, fg_color="#2a2a3e")
            card.pack(fill="x", pady=5, padx=5)


            card.bind("<Button-1>", lambda e, uid=user_id, uname=name: self.on_card_click(uid, uname))


            left_frame = ctk.CTkFrame(card, fg_color="transparent")
            left_frame.pack(side="left", padx=12, pady=10)
            left_frame.bind("<Button-1>", lambda e, uid=user_id, uname=name: self.on_card_click(uid, uname))

            ctk.CTkLabel(left_frame, text="👤", font=("Segoe UI", 28)).pack(side="left", padx=(0, 10))

            info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
            info_frame.pack(side="left")
            info_frame.bind("<Button-1>", lambda e, uid=user_id, uname=name: self.on_card_click(uid, uname))

            ctk.CTkLabel(info_frame, text=name, font=("Segoe UI", 15, "bold"),
                         text_color="#ffffff").pack(anchor="w")
            ctk.CTkLabel(info_frame, text=f"📅 {age} лет | ⚖️ {weight} кг | 📏 {height} см",
                         font=("Segoe UI", 11), text_color="#888888").pack(anchor="w")


            right_frame = ctk.CTkFrame(card, fg_color="transparent")
            right_frame.pack(side="right", padx=12, pady=10)

            ctk.CTkButton(right_frame, text="✏️", width=40, height=32, corner_radius=8,
                          fg_color="#F59E0B", font=("Segoe UI", 14),
                          command=lambda uid=user_id, uname=name: self.edit_user(uid, uname)
                          ).pack(side="left", padx=2)

            ctk.CTkButton(right_frame, text="🗑️", width=40, height=32, corner_radius=8,
                          fg_color="#EF4444", font=("Segoe UI", 14),
                          command=lambda uid=user_id, uname=name: self.delete_user(uid, uname)
                          ).pack(side="left", padx=2)

    def on_card_click(self, user_id, user_name):

        for widget in self.users_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.configure(fg_color="#2a2a3e")
        for widget in self.users_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkFrame):
                        for subchild in child.winfo_children():
                            if isinstance(subchild, ctk.CTkFrame):
                                for label in subchild.winfo_children():
                                    if isinstance(label, ctk.CTkLabel) and label.cget("text") == user_name:
                                        widget.configure(fg_color="#3a5a3a")
                                        self.selected_user_id = user_id
                                        self.selected_user_name = user_name
                                        return

    def create_user(self):
        from views.dialogs import ProfileDialog
        ProfileDialog(self, self.db, on_save=self.on_user_saved)

    def edit_user(self, user_id, user_name):
        from views.dialogs import ProfileDialog
        ProfileDialog(self, self.db, user_id, on_save=self.on_user_saved)

    def delete_user(self, user_id, user_name):
        if messagebox.askyesno("Подтверждение",
                               f"Удалить пользователя '{user_name}'?\n\n"
                               f"Все данные о питании будут потеряны!"):
            self.db.cursor.execute("DELETE FROM meals WHERE user_id=?", (user_id,))
            self.db.cursor.execute("DELETE FROM weight_log WHERE user_id=?", (user_id,))
            self.db.cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            self.db.conn.commit()

            messagebox.showinfo("Успех", f"✅ Пользователь '{user_name}' удалён!")
            self.load_users()

    def on_user_saved(self, user_id, user_name):
        self.load_users()
        if user_id and user_name and self.on_user_selected:
            self.on_user_selected(user_id, user_name)

    def select_user(self):
        if hasattr(self, 'selected_user_id') and self.selected_user_id:
            if self.on_user_selected:
                self.on_user_selected(self.selected_user_id, self.selected_user_name)
            self.destroy()
        else:
            messagebox.showwarning("Внимание", "Сначала выберите пользователя из списка (кликните по карточке)")