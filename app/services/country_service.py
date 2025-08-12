from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlmodel import Session

from app import crud, models
from app.crud.crud_country import CRUDCountry


class CountryService:
    def __init__(self, country_crud: CRUDCountry):
        """
        Service to manage countries.

        :param country_crud: CRUD object to interact with database.
        """
        self.country_crud = country_crud

    def get_by_code(self, db: Session, country_code: str) -> models.Country:
        db_country = self.country_crud.get(db=db, id=country_code)
        if not db_country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Country not found"
            )
        return db_country

    def get_all(self, db: Session, skip: int, limit: int) -> Sequence[models.Country]:
        return self.country_crud.get_multi(db=db, skip=skip, limit=limit)

    def create(self, db: Session, country_in: models.CountryCreate) -> models.Country:
        existing_country = self.country_crud.get(db=db, id=country_in.alpha_2_code)
        if existing_country:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Country with this code already exists.",
            )

        return self.country_crud.create(db=db, obj_in=country_in)

    def update(
        self, db: Session, country_code: str, country_in: models.CountryUpdate
    ) -> models.Country:
        db_country = self.get_by_code(db=db, country_code=country_code)
        return self.country_crud.update(db=db, db_obj=db_country, obj_in=country_in)

    def delete(self, db: Session, country_code: str) -> models.Country:
        db_country = self.get_by_code(db=db, country_code=country_code)
        return self.country_crud.remove(db=db, id=db_country.alpha_2_code)


country_service = CountryService(crud.country)
