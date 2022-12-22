import random
import time

from queue import Queue
from pyker.game.game import Game, State

class Dummy:
    def __init__(self, game: Game, initial_state: State, queue: Queue):
        self.game = game
        self.initial_state = initial_state
        self.queue = queue
    
    def run(self):
        time.sleep(3)
        actions = self.game.actions(self.initial_state)
        action = random.choice(actions)
        if isinstance(action, tuple):
            action, range = action[0], action[1]
            amount = random.randint(*range)
            self.queue.put((action, amount, range))
        else:
            self.queue.put(action)

    

    