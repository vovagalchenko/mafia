from base import Base, Mafia_Model_Mixin
from sqlalchemy.dialects import mysql
from sqlalchemy import Column, String, Integer, Enum, ForeignKey
from sqlalchemy.orm import relationship, backref
from model.db_session import DB_Session_Factory
from model.player import Player

game_state_enum = Enum('NOT_STARTED', 'NIGHT', 'DAWN', 'DAY', 'DUSK', 'MAFIA_WIN', 'CITIZENS_WIN')

class Game(Base, Mafia_Model_Mixin):
    __tablename__ = 'game'
    
    game_id = Column('game_id', Integer, primary_key = True)
    game_state = Column('game_state', game_state_enum, server_default = 'NOT_STARTED', index = True)
    leader_user_id = Column('leader_user_id', String(50), ForeignKey("user.user_id"), nullable = False)
    players = relationship("Player", backref = "game", lazy="dynamic")

    def __init__(self, leader_user_id):
        self.leader_user_id = leader_user_id

    def for_api(self):
        all_columns = super(Game, self).for_api()
        db_session = DB_Session_Factory.get_db_session()
        all_columns['players'] = []
        for player in self.players.all():
            all_columns['players'].append(player.for_api())
        return all_columns
