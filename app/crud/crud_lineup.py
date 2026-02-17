from app.crud.base import CRUDBase
from app.models.lineup import Lineup


class CRUDLineup(CRUDBase[Lineup, Lineup, Lineup]):
    pass

lineup = CRUDLineup(Lineup)
