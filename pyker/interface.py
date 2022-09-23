import pygame
import os

from pyker.game import Play
from pyker.entities import *
import enum

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyker - Poker Texas Hold'em")

colors = {"BORDEAUX": (90, 0, 44)}

FPS = 60

TEST_CARD = pygame.image.load(os.path.join("assets", "cards", "tile000.png"))
TEST_CARD = pygame.transform.scale(TEST_CARD, (70, 94))

CARD_Y_OFFSET = 10
CARD_X_OFFSET = 40

ROWS = 7
COLS = 5

CELL_X = 2
CELL_Y = 5


class Game:
    def __init__(self, n_players, players_names):
        if not 2 <= n_players <= 8:
            raise ValueError("Unvalid number of players.")

        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)

        # self.dealer = self.players.take_random()
        self.play = None
        self.dealer = players[0]
        self.blinds_level = 0

    def draw_window(self):
        WIN.fill(colors["BORDEAUX"])
        x = WIDTH / COLS * CELL_X + CARD_X_OFFSET
        y = HEIGHT / ROWS * CELL_Y + CARD_Y_OFFSET
        WIN.blit(TEST_CARD, (x, y))

        pygame.display.update()

    def loop(self):
        clock = pygame.time.Clock()
        run = True
        is_interactive = False

        while run:
            clock.tick(FPS)
            if is_interactive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
            else:
                if self.play is None:
                    self.play = Play(self.players, self.dealer, self.blinds_level)
                if self.play.current_player is None:
                    if self.play.round > Round.End:
                        self.play = None
                    else:
                        self.play._init_round()
                else:
                    actions = self.play.take_turn_actions()
                    if actions is not None:
                        is_interactive = True

            self.draw_window()
            if self.players.get_n_active() <= 1:
                run = False

        pygame.quit()


if __name__ == "__main__":
    n = 8
    players = ["John", "Lucy"]  # , "Carl", "Mark", "Hannah", "Mike", "Lana", "Phil"]
    game = Game(n, players)
    game.loop()
