from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from game_api.parameter import Parameter, Array_Parameter_Type
from lib.cfg import CFG
from model.db_session import DB_Session_Factory
from model.user_model import User
from model.game import Game
from model.player import Player

class create_game(HTTP_Response_Builder):
    invited_user_ids = Parameter('invited_user_ids', required = True, parameter_type = Array_Parameter_Type)
    
    def do_controller_specific_work(self):
        db_session = DB_Session_Factory.get_db_session()
        game = Game(self.user.user_id)
        db_session.add(game)
        for invited_user_id in self.invited_user_ids:
            user = db_session.query(User).get(invited_user_id)
            if user is None:
                user = User(invited_user_id, None, None, None)
                db_session.add(user)
                db_session.flush()
            player = Player(invited_user_id, game.game_id, 'INVITED')
            db_session.add(player)
        db_session.add(Player(self.user.user_id, game.game_id, 'ACCEPTED'))
        db_session.commit()
        return HTTP_Response('200 OK', {'game' : game.for_api()})
