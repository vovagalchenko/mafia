from base import Base, Mafia_Model_Mixin
from sqlalchemy import Column, String, Enum, ForeignKey, Integer

class Player(Base, Mafia_Model_Mixin):
    __tablename__ = 'player'

    player_id = Column('player_id', Integer, primary_key = True)
    user_id = Column('user_id', String(50), ForeignKey("user.user_id"), nullable = False, index = True)
    game_id = Column('game_id', Integer, ForeignKey("game.game_id"), nullable = False, index = True)
    role = Column('role', Enum('INVITED', 'ACCEPTED', 'CITIZEN', 'MAFIA', 'GHOST'), nullable = False, server_default = 'INVITED')
    current_vote = Column('current_vote', Integer, ForeignKey("player.player_id"), nullable = True)

    def __init__(self, user_id, game_id, role = None):
        self.user_id = user_id
        self.game_id = game_id
        if role is not None:
            self.role = role
