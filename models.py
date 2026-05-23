from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class User:
    id: Optional[int]
    name: str
    age: int
    gender: str
    weight: float
    height: float
    activity_level: str
    goal: str
    daily_calories: float
    daily_protein: float
    daily_fat: float
    daily_carbs: float


@dataclass
class Product:
    id: Optional[int]
    name: str
    calories: float
    protein: float
    fat: float
    carbs: float


@dataclass
class Meal:
    id: Optional[int]
    user_id: int
    date: str
    meal_type: str
    product_id: int
    weight: float
    calories: float
    protein: float
    fat: float
    carbs: float


class Calculator:

    @staticmethod
    def calculate_bmr(weight: float, height: float, age: int, gender: str) -> float:
        if gender == "male":
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        return bmr * multipliers.get(activity_level, 1.2)

    @staticmethod
    def calculate_macros(tdee: float, goal: str, weight: float) -> Dict[str, int]:
        if goal == "lose":
            calories = tdee * 0.85
            protein = 2.0
            fat = 0.8
            carbs = (calories - (protein * weight * 4) - (fat * weight * 9)) / 4
        elif goal == "gain":
            calories = tdee * 1.15
            protein = 2.2
            fat = 1.0
            carbs = (calories - (protein * weight * 4) - (fat * weight * 9)) / 4
        else:
            calories = tdee
            protein = 1.8
            fat = 0.9
            carbs = (calories - (protein * weight * 4) - (fat * weight * 9)) / 4

        return {
            "calories": round(calories),
            "protein": round(protein * weight),
            "fat": round(fat * weight),
            "carbs": round(max(carbs, 0))
        }