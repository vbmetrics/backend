from app.crud.base import CRUDBase
from app.models import Season, SeasonCreate, SeasonUpdate


class CRUDSeason(CRUDBase[Season, SeasonCreate, SeasonUpdate]):
    pass


season = CRUDSeason(Season)
