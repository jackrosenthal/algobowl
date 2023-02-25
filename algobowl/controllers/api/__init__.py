from algobowl.controllers.api import user as user_api
from algobowl.lib import base


class ApiController(base.BaseController):
    user = user_api.UserLookupApiController()
