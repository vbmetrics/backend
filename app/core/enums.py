# app/core/enums.py
from enum import Enum


class UserRole(str, Enum):
    admin = "admin"
    user = "user"
    coach = "coach"
    analyst = "analyst"
