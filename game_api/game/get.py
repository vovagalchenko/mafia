from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from game_api.parameter import Parameter, Integer_Parameter_Type
from model.game import Game
from model.db_session import DB_Session_Factory

class get_game(HTTP_Response_Builder):
    def do_controller_specific_work(self):
        if self.user.is_authorized_to_access_game(self.resource_id):
            db_session = DB_Session_Factory.get_db_session()
            game = db_session.query(Game).get(self.resource_id)
            return HTTP_Response("200 OK", {'game' : game.for_api()})
        else:
            raise Authorization_Exception("Either there's no game with this id, or you don't have access to it.")
