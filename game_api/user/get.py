from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from model.user_model import User
from model.db_session import DB_Session_Factory
from game_api.exceptions import *
from game_api.parameter import Parameter, Date_Time_Parameter_Type

class get_user(HTTP_Response_Builder):

    def do_controller_specific_work(self):
        db_session = DB_Session_Factory.get_db_session()
        needed_user = db_session.query(User).get(self.resource_id)
        if needed_user is None:
            raise API_Exception("400 Bad Request", "Couldn't find a user with user_id <%s>" % (self.resource_id))
        else:
            return HTTP_Response("200 OK", {'user' : needed_user.for_api(self.user)})
