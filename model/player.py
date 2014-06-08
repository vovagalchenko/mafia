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

    def for_api(self, asking_player):
        all_columns = super(Player, self).for_api()
        is_dead = self.role == 'GHOST'
        is_in_game = self.role != 'INVITED'
        if is_dead or (asking_player.player_id != all_columns['player_id'] and not(asking_player.role == 'MAFIA' and self.role == 'MAFIA')):
            all_columns.pop('role', None)
        all_columns['is_dead'] = is_dead
        all_columns['is_in_game'] = is_in_game
        return all_columns
