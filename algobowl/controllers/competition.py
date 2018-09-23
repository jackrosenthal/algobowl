import datetime
from tg import expose, abort
from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Competition

__all__ = ['CompetitionsController', 'CompetitionController']


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition


class CompetitionsController(BaseController):
    @expose()
    def _lookup(self, comp_id, *args):
        try:
            comp_id = int(comp_id)
        except ValueError:
            abort(404, "Invalid input for competition id")
        competition = DBSession.query(Competition).get(comp_id)
        if not competition:
            abort(404, "No such competition")

        return CompetitionController(competition), args

    @expose('algobowl.templates.competition.list')
    def index(self):
        now = datetime.datetime.now()
        active = (DBSession.query(Competition)
                           .filter(Competition.input_upload_begins <= now)
                           .filter(Competition.evaluation_ends > now)
                           .order_by(Competition.evaluation_ends))
        historical = (DBSession.query(Competition)
                               .filter(Competition.evaluation_ends < now)
                               .order_by(Competition.evaluation_ends))
        return {'active': active, 'historical': historical}
