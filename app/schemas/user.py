from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

# SUGESTIA: Przenieś UserRole do osobnego pliku,
# np. app/schemas/enums.py, aby uniknąć cyklicznych importów
# from app.schemas.enums import UserRole
# Na potrzeby przykładu zostawiam tak jak jest, zakładając, że wiesz co robisz:
from app.models.user import UserRole


# 1. Baza wspólna dla wszystkich (tylko bezpieczne pola)
class UserBaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr
    full_name: Optional[str] = Field(default=None, max_length=200)


# 2. Rejestracja publiczna (Użytkownik sam zakłada konto)
class UserRegisterDTO(UserBaseDTO):
    password: str = Field(min_length=8, max_length=128)
    # Brak pola 'role' i 'is_active' - system ustawia domyślne (user, True/False)


# 3. Tworzenie przez Admina (Admin może ustawić rolę od razu)
class UserCreateDTO(UserRegisterDTO):
    role: UserRole = UserRole.user
    is_active: bool = True


# 4. Aktualizacja (Patch)
class UserUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: Optional[EmailStr] = None # Często pozwala się zmienić email
    full_name: Optional[str] = Field(default=None, max_length=200)
    password: Optional[str] = Field(default=None, min_length=8, max_length=128)

    # Pola wrażliwe - powinny być filtrowane w serwisie/API
    # w zależności od uprawnień edytującego
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None


# 5. Odczyt (To co zwracamy klientowi)
class UserReadDTO(UserBaseDTO):
    id: UUID
    is_active: bool
    role: UserRole
    is_superuser: bool

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Hasło NIGDY nie jest tu zawarte
