from curses.panel import bottom_panel
import os
from pathlib import Path

import pygame

from pyker.game import Play
from pyker.models import *
from pyker.gui.components import *
from pyker.gui.constants import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyker - Poker Texas Hold'em")

LAST_BUTTON_X = 1200
BUTTONS_Y = 650

BUTTONS = {}
PLAYER_GUIS = {}
COMMUNITY_CARDS = {}

class Game:
    def __init__(self, players_names):
        if not 2 <= len(players_names) <= 8:
            raise ValueError("Unvalid number of players.")

        self.n_players = len(players_names)
        players = []
        
        for i, name in enumerate(players_names):
            players.append(Player(name, 2000, is_you=i==0))
        self.you = players[0]
        self.players = Players(players)
 
        self.play = None  # the current play
        self.dealer = players[0]  # keep track of the dealer
        self.blinds_level = 0  # keep track of the blinds level

        self.is_interactive = False  # waiting for the action
        self.available_actions = None

    def reset(self):
        BUTTONS.clear()
        PLAYER_GUIS.clear()
        COMMUNITY_CARDS.clear()
        self.dealer = self.players.next_to(self.dealer)
        
    def build_buttons(self):
        x, y = LAST_BUTTON_X, BUTTONS_Y
        offset_x = 16

        for action in Action:
            button = ButtonGUI(WIN, action, topleft=(x, y))
            button.rect.left -= offset_x + button.image.get_width()
            offset_x += button.image.get_width() + 16
            BUTTONS[action] = button
            
    def build_player_guis(self):
        for i, player in enumerate(self.players.starting):
            PLAYER_GUIS[player] = PlayerGUI(
                WIN,
                player,
                self.n_players,
                i
            )
            
    def update_players_info(self):
        for player_gui in PLAYER_GUIS.values():
            player_gui.update_player_info()

    def build_new_community_cards(self):
        offset_x = 0
        x, y = 449, 313

        for card in self.play.community.cards:
            card_gui = CardGUI(WIN, card, topleft=(x + offset_x, y))
            COMMUNITY_CARDS[card] = card_gui
            offset_x += card_gui.image.get_width() + 8

    def draw_window(self):
        WIN.fill(COLORS["BORDEAUX"])

        for player_gui in PLAYER_GUIS.values():
            player_gui.draw()
        for card_gui in COMMUNITY_CARDS.values():
            card_gui.draw()
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
                    self.build_player_guis()
                if self.play.current_player is None:  # round ended
                    if self.play.current_round > Round.End:  # play ended
                        self.play = None
                        self.reset()
                    else:
                        self.update_players_info()  # start new round
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
    players = ["John", "Lucy", "jasdfksa", "aa", "bb", "cc", "dd", "ee"]
    game = Game(players)
    game.loop()
