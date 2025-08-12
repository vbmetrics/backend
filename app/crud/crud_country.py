from app.crud.base import CRUDBase
from app.models import Country, CountryCreate, CountryUpdate


class CRUDCountry(CRUDBase[Country, CountryCreate, CountryUpdate]):
    pass


country = CRUDCountry(Country)
