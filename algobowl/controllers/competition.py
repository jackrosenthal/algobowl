from tg import expose
from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Competition

__all__ = ['CompetitionsController', 'CompetitionController']


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition


class CompetitionsController(BaseController):
    @expose()
    def _lookup(self, comp_id, *args):
        competition = (DBSession.query(Competition)
                                .filter(Competition.id == comp_id)
                                .one_or_none())

        return CompetitionController(competition), args
