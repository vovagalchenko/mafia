from game_api.exceptions import *
from game_api.http_response_builder import HTTP_Response_Builder, HTTP_Response
from game_api.parameter import Parameter, Integer_Parameter_Type, String_Parameter_Type
from model.db_session import DB_Session_Factory
from model.game import Game, Game_Event
from model.player import Player
from sqlalchemy import or_
from subprocess import Popen, PIPE
from lib.time_utils import dt_to_timestamp
import random

class update_game(HTTP_Response_Builder):
    comment = Parameter("comment", required = False, parameter_type = String_Parameter_Type)
    vote = Parameter("vote", required = False, parameter_type = Integer_Parameter_Type)

    def do_controller_specific_work(self):
        if self.user.is_authorized_to_access_game(self.resource_id):
            if self.comment is None and self.vote is None:
                raise API_Exception("400 Bad Request", "You must provide a vote, a comment or both.")
            db_session = DB_Session_Factory.get_db_session()
            player = db_session.query(Player).filter(Player.game_id == self.resource_id, Player.user_id == self.user.user_id).first()
            game = db_session.query(Game).get(self.resource_id)
            if self.vote is not None and not (((game.game_state == 'DAY' or game.game_state == 'DUSK') and (player.role == 'CITIZEN' or player.role == 'MAFIA')) or ((game.game_state == 'NIGHT' or game.game_state == 'DAWN') and player.role == 'MAFIA')):
                raise API_Exception("400 Bad Request", "You are not authorized to vote at this time.")
            elif self.vote == player.player_id:
                raise API_Exception("400 Bad Request", "You can't vote to eliminate yourself.")
            elif self.vote is not None:
                if self.vote == player.current_vote:
                    raise API_Exception("400 Bad Request", "You've already voted to eliminate this player.")
                player_to_vote_to_eliminate = db_session.query(Player).filter(Player.player_id == self.vote, Player.game_id == self.resource_id).first()
                if player_to_vote_to_eliminate is None:
                    raise API_Exception("400 Bad Request", "Unable to find a player in this game you're voting to eliminate.")
                if player_to_vote_to_eliminate.role == 'GHOST':
                    raise API_Exception("400 Bad Request", "This player is already eliminated.")
                player.current_vote = self.vote
            
            game_event = Game_Event(game.game_id, game.game_state, self.vote, self.comment, player.player_id, None)
            db_session.add(game_event)
            if player.role == 'INVITED':
                player.role = 'ACCEPTED'
            db_session.add(player)
            db_session.commit()
            should_kick_off_timer = False

            if game.game_state == 'NOT_STARTED':
                players = db_session.query(Player).filter(Player.game_id == self.resource_id).all()
                everyone_accepted = True
                for one_player in players:
                    if one_player.role != 'ACCEPTED':
                        everyone_accepted = False
                        break
                if everyone_accepted:
                    for one_player in players:
                        one_player.role = 'CITIZEN'
                        db_session.add(one_player)
                    for mafia_index in random.sample(range(len(players)), len(players)/3):
                        players[mafia_index].role = 'MAFIA'
                    game.game_state = 'NIGHT'
            elif game.game_state == 'NIGHT':
                if self.vote is not None:
                    mafia_players = db_session.query(Player).filter(Player.game_id == self.resource_id, Player.role == 'MAFIA')
                    all_mafia_voted = True
                    for mafia_player in mafia_players:
                        if mafia_player.current_vote is None:
                            all_mafia_voted = False
                            break
                    if all_mafia_voted:
                        game.game_state = 'DAWN'
                        should_kick_off_timer = True
            elif game.game_state == 'DAY':
                if self.vote is not None:
                    active_players = db_session.query(Player).filter(Player.game_id == self.resource_id, or_(Player.role == 'MAFIA',Player.role == 'CITIZEN'))
                    all_active_players_voted = True
                    for active_player in active_players:
                        if active_player.current_vote is None:
                            all_active_players_voted = False
                            break
                    if all_active_players_voted is True:
                        game.game_state = 'DUSK'
                        should_kick_off_timer = True
            elif game.game_state == 'DAWN' or game.game_state == 'DUSK':
                if self.vote is not None:
                    should_kick_off_timer = True
 
            db_session.add(game)
            db_session.commit()

            if should_kick_off_timer is True:
                ## HOLY FUCK THIS IS A TERRIBLE HACK. FIGURE OUT A SMOOTHER WAY TO EXECUTE SOMETHING ASYNCHRONOUSLY
                command = "cd /home/vova/mafia/code; sleep 60; python -m scripts.finalize_vote -d %d -g %d" % (dt_to_timestamp(game_event.created), game.game_id)
                stdout_handle = open("/home/vova/mafia/data/apache_logs/stdout.tmp", "w")
                stderr_handle = open("/home/vova/mafia/data/apache_logs/stderr.tmp", "w")
                Popen(command, shell = True, stdout = stdout_handle, stderr = stderr_handle)
            return HTTP_Response("200 OK", game.for_api(player))
        else:
            raise Authorization_Exception("Either there's no game with this id, or you don't have authorization to update it.")
