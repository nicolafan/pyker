import os
from pathlib import Path

import pygame

from pyker.game import Play
from pyker.models import *
from pyker.gui.components import *

WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyker - Poker Texas Hold'em")

COLORS = {
    "BORDEAUX": (90, 0, 44),
    "WHITE": (255, 255, 255),
    "GRAY_BG": (128, 128, 128, 1)
}

FPS = 60

CARD_Y_OFFSET = 10
CARD_X_OFFSET = 40

LAST_BUTTON_X = 1200
BUTTONS_Y = 650

ROWS = 7
COLS = 5

PLAYERS_CELLS = {
    2: [(5, 2), (1, 2)],
    3: [(5, 2), (3, 0), (3, 4)],
    4: [(5, 2), (3, 0), (1, 2), (3, 4)],
    5: [(5, 2), (5, 1), (1, 1), (2, 3), (5, 3)],
    6: [(5, 2), (5, 1), (1, 1), (1, 2), (1, 3), (5, 3)],
    7: [(5, 2), (5, 1), (3, 0), (1, 1), (1, 3), (3, 4), (5, 3)],
    8: [(5, 2), (5, 1), (3, 0), (1, 1), (1, 2), (1, 3), (3, 4), (5, 3)],
}

CELLS_ORIENTATIONS = {
    (5, 2): 0,
    (5, 1): 0,
    (3, 0): 270,
    (1, 1): 180,
    (1, 2): 180,
    (1, 3): 180,
    (3, 4): 90,
    (5, 3): 0,
}

CELL_WIDTH = WIDTH / 5
CELL_HEIGHT = HEIGHT / 7

CARDS = {}
BUTTONS = {}
NAMES = []
CHIPS = []
class Game:
    def __init__(self, players_names):
        if not 2 <= len(players_names) <= 8:
            raise ValueError("Unvalid number of players.")

        self.n_players = len(players_names)
        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)

        self.play = None  # the current play
        self.dealer = players[0]  # keep track of the dealer
        self.blinds_level = 0  # keep track of the blinds level

        self.is_interactive = False  # waiting for the action
        self.available_actions = None

    def reset(self):
        CARDS.clear()
        BUTTONS.clear()
        self.dealer = self.players.next_to(self.dealer)

    def build_buttons(self):
        x, y = LAST_BUTTON_X, BUTTONS_Y
        offset_x = 16

        for action in Action:
            button = ButtonGUI(WIN, action, topleft=(x, y))
            button.rect.left -= offset_x + button.image.get_width()
            offset_x += button.image.get_width() + 16
            BUTTONS[action] = button

    def build_players_cards(self):
        for i, player in enumerate(self.players.starting):
            if player.hand is not None:
                player_cell = PLAYERS_CELLS[self.n_players][i]

                x = WIDTH / COLS * player_cell[1] + CARD_X_OFFSET
                y = HEIGHT / ROWS * player_cell[0] + CARD_Y_OFFSET

                local_offset_x = 0
                local_offset_y = 0
                for card in player.hand.cards:
                    orientation = CELLS_ORIENTATIONS[player_cell]
                    card_gui = CardGUI(
                        WIN, card, topleft=(x + local_offset_x, y + local_offset_y), angle=orientation
                    )
                    CARDS[card] = card_gui

                    if orientation == 270 or orientation == 90:
                        local_offset_y += card_gui.image.get_height() + 4
                    else:
                        local_offset_x += card_gui.image.get_width() + 4

    def build_new_community_cards(self):
        offset_x = 0
        x, y = 449, 313

        for card in self.play.community.cards:
            card_gui = CardGUI(WIN, card, topleft=(x + offset_x, y))
            CARDS[card] = card_gui
            offset_x += card_gui.image.get_width() + 8

    def build_players_names(self):
        for i, player in enumerate(self.players.starting):
            player_cell = PLAYERS_CELLS[self.n_players][i]
            x = WIDTH / COLS * player_cell[1]
            y = HEIGHT / ROWS * player_cell[0]

            y += CELL_HEIGHT

            t = TextGUI(WIN, player.name, topleft=(x, y), angle=90, size=FontSize.Medium)
            NAMES.append(t)

    def build_players_chips(self):
        CHIPS.clear()
        for i, player in enumerate(self.players.starting):
            player_cell = PLAYERS_CELLS[self.n_players][i]
            x = WIDTH / COLS * player_cell[1]
            y = HEIGHT / ROWS * player_cell[0]

            y += CELL_HEIGHT - 60

            t = TextGUI(WIN, str(player.chips), topleft=(x, y), angle=90, size=FontSize.Medium)
            CHIPS.append(t)


    def draw_window(self):
        WIN.fill(COLORS["BORDEAUX"])

        for card in CARDS.values():
            card.draw()
        for name in NAMES:
            name.draw()
        for chips in CHIPS:
            chips.draw()
        if self.is_interactive:
            for action in self.available_actions:
                if BUTTONS[action].draw():
                    self.play.execute_action(action)
                    self.is_interactive = False

        pygame.display.update()

    def loop(self):
        clock = pygame.time.Clock()
        run = True
        self.is_interactive = False

        self.available_actions = None

        while run:
            clock.tick(FPS)
            if self.is_interactive:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        run = False
            else:
                if self.play is None:  # start new play
                    self.play = Play(self.players, self.dealer, self.blinds_level)
                    self.build_buttons()
                    self.build_players_names()
                    self.build_players_cards()
                if self.play.current_player is None:  # round ended
                    if self.play.current_round > Round.End:  # play ended
                        self.play = None
                        self.reset()
                    else:
                        self.build_players_chips()  # start new round
                        self.play.init_round()
                        self.build_new_community_cards()
                else:
                    self.available_actions = self.play.take_turn()  # action!
                    if self.available_actions is not None:
                        self.is_interactive = True

            self.draw_window()
            if self.players.get_n_active() <= 1:
                run = False

        pygame.quit()


if __name__ == "__main__":
    players = ["John", "Lucy", "Carl", "Mark"]#, "Hannah", "Mike", "Lana", "Phil"]
    game = Game(players)
    game.loop()
