from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String, ForeignKey, Integer
from model.game import game_state_enum

class Game_Event(Base, Mafia_Model_Mixin):
    __tablename__ = 'game_event'

    game_event_id = Column('game_event_id', Integer, primary_key = True)
    from_player_id = Column('from_player_id', Integer, ForeignKey("player.player_id"), nullable = True, index = True, server_default = None)
    to_player_id = Column('to_player_id', Integer, ForeignKey("player.player_id"), nullable = True, index = True, server_default = None)
    game_id = Column('game_id', Integer, ForeignKey("game.game_id"), nullable = False, index = True)
    game_state = Column('game_state', game_state_enum, nullable = False)
    payload = Column('payload', mysql.LONGBLOB, nullable = False)

    def __init__(self, game_id, game_state, payload, from_player_id = None, to_player_id = None):
        self.game_id = game_id
        self.game_state = game_state
        self.payload = payload
        self.from_player_id = from_player_id
        self.to_player_id = to_player_id
