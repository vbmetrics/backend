from collections.abc import Sequence

from sqlmodel import Session

from app.crud.crud_country import CRUDCountry
from app.models.country import Country
from app.schemas import CountryCreateDTO, CountryUpdateDTO
from app.services.errors import BadRequestError, NotFoundError


class CountryService:
    def __init__(self, country_crud: CRUDCountry):
        """
        Service to manage countries.

        :param country_crud: CRUD object to interact with database.
        """
        self.country_crud = country_crud

    def get_by_code(self, db: Session, country_code: str) -> Country:
        db_country = self.country_crud.get(db=db, code=country_code)
        if not db_country:
            raise NotFoundError(
                "Country not found",
                code="COUNTRY_NOT_FOUND",
                details={"alpha_2_code": country_code},
            )
        return db_country

    def get_all(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str | None = None
    ) -> Sequence[Country]:
        return self.country_crud.get_multi(db=db, skip=skip, limit=limit, search=search)

    def create(self, db: Session, country_in: CountryCreateDTO) -> Country:
        if len(country_in.alpha_2_code) != 2:
            raise BadRequestError(
                "alpha_2_code must be 2 letters", code="INVALID_ALPHA2"
            )
        existing = self.country_crud.get(db=db, code=country_in.alpha_2_code)
        if existing:
            raise BadRequestError(
                "Country already exists",
                code="COUNTRY_EXISTS",
                details={"alpha_2_code": country_in.alpha_2_code},
            )

        return self.country_crud.create(db=db, obj_in=country_in)

    def update(
        self, db: Session, country_code: str, country_in: CountryUpdateDTO
    ) -> Country:
        db_country = self.get_by_code(db=db, country_code=country_code)
        return self.country_crud.update(db=db, db_obj=db_country, obj_in=country_in)

    def delete(self, db: Session, country_code: str) -> Country:
        db_country = self.get_by_code(db=db, country_code=country_code)
        return self.country_crud.remove(db=db, db_obj=db_country)
