from datetime import datetime


def format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")


def get_activity_text(activity_level: str) -> str:
    activities = {
        "sedentary": "🛋️ Сидячий",
        "light": "🚶 Легкая",
        "moderate": "🏃 Средняя",
        "active": "💪 Высокая",
        "very_active": "⚡ Очень высокая"
    }
    return activities.get(activity_level, "Средняя")


def get_goal_text(goal: str) -> str:
    goals = {
        "maintain": "⚖️ Поддержание веса",
        "lose": "⬇️ Похудение",
        "gain": "⬆️ Набор массы"
    }
    return goals.get(goal, "Поддержание веса")