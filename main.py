from database import Database
from views.main_window import MainWindow


def main():
    db = Database()
    app = MainWindow(db)
    app.mainloop()


if __name__ == "__main__":
    main()