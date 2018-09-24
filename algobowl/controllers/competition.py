import zipfile
import datetime
from io import BytesIO
from tg import expose, abort, request, response
from algobowl.lib.base import BaseController
from algobowl.model import DBSession, Competition, Input, Group

__all__ = ['CompetitionsController', 'CompetitionController']


class CompetitionController(BaseController):
    def __init__(self, competition):
        self.competition = competition

    @expose()
    def all_inputs(self):
        user = request.identity and request.identity['user']
        now = datetime.datetime.now()
        comp = self.competition
        if not (user and user.admin) and now < comp.output_upload_begins:
            abort(403, "Input downloading is not available until the output"
                       " upload stage begins.")
        f = BytesIO()
        archive = zipfile.ZipFile(f, mode='w', compresslevel=6)
        inputs = (DBSession.query(Input)
                           .join(Input.group)
                           .filter(Group.competition_id == comp.id))
        for iput in inputs:
            archive.writestr(
                'inputs/{}'.format(iput.data.filename),
                iput.data.file.read())
        archive.close()
        f.seek(0)
        response.content_type = 'application/zip'
        return f.read()


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
