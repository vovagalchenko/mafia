from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from model.game import Game
from model.player import Player
from model.db_session import DB_Session_Factory
from game_api.exceptions import *
from game_api.parameter import Parameter, Date_Time_Parameter_Type

class get_game(HTTP_Response_Builder):
    min_date = Parameter('min_date', required = False, default = None, parameter_type = Date_Time_Parameter_Type)

    def do_controller_specific_work(self):
        if self.user.is_authorized_to_access_game(self.resource_id):
            db_session = DB_Session_Factory.get_db_session()
            game = db_session.query(Game).get(self.resource_id)
            player = db_session.query(Player).filter(Player.game_id == self.resource_id, Player.user_id == self.user.user_id).first()
            min_date = self.min_date
            if min_date is None:
                min_date = game.created
            return HTTP_Response("200 OK", {'game' : game.for_api(player, min_date)})
        else:
            raise Authorization_Exception("Either there's no game with this id, or you don't have access to it.")
