from datetime import datetime


def format_date(date_str: str) -> str:
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")


def get_activity_text(activity_level: str) -> str:
    activities = {
        "sedentary": "🛋️ Сидячий",
        "light": "🚶 Легкая 1-2 дня тренировок",
        "moderate": "🏃 Средняя 2-3 дня тренировок",
        "active": "💪 Высокая 3-4 дня тренировок",
        "very_active": "⚡ Очень высокая 4+ дня тренировок"
    }
    return activities.get(activity_level, "Средняя")


def get_goal_text(goal: str) -> str:
    goals = {
        "maintain": "⚖️ Поддержание веса",
        "lose": "⬇️ Похудение",
        "gain": "⬆️ Набор массы"
    }
    return goals.get(goal, "Поддержание веса")