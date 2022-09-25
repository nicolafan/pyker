import enum
import os

import pygame
from pyker.game import Play
from pyker.models import *



WIDTH, HEIGHT = 1280, 720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyker - Poker Texas Hold'em")

COLORS = {"BORDEAUX": (90, 0, 44)}

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

CARDS_SPRITES = {}
BUTTONS_SPRITES = {}

CARDS = {}
BUTTONS = {}


def load_sprites():
    assets_dir = "assets"
    assets_cards_dir = os.path.join(assets_dir, "cards")
    assets_buttons_dir = os.path.join(assets_dir, "buttons")

    for filename in os.listdir(assets_cards_dir):
        card_name = filename[:-4]
        card_sprite = pygame.image.load(os.path.join(assets_cards_dir, filename))
        card_sprite = pygame.transform.scale(
            card_sprite, (card_sprite.get_width() * 2, card_sprite.get_height() * 2)
        )
        CARDS_SPRITES[card_name] = card_sprite

    for filename in os.listdir(assets_buttons_dir):
        button_name = filename[:-4]
        button_sprite = pygame.image.load(os.path.join(assets_buttons_dir, filename))
        button_sprite = pygame.transform.scale(
            button_sprite,
            (button_sprite.get_width() * 4, button_sprite.get_height() * 4),
        )
        BUTTONS_SPRITES[button_name] = button_sprite


class CardGUI:
    def __init__(self, x, y, orientation, covered, card: Card):
        self.image = pygame.transform.rotate(CARDS_SPRITES[card.code()], orientation)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

        self.covered = False

    def draw(self):
        WIN.blit(self.image, (self.rect.x, self.rect.y))


class ButtonGUI:
    def __init__(self, x, y, action: Action):
        d = {
            Action.BetOrRaise: "bet",
            Action.Call: "call",
            Action.Check: "check",
            Action.Fold: "fold",
        }
        self.image = BUTTONS_SPRITES[d[action]]
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        WIN.blit(self.image, (self.rect.x, self.rect.y))
        return action


class Game:
    def __init__(self, n_players, players_names):
        if not 2 <= n_players <= 8:
            raise ValueError("Unvalid number of players.")

        load_sprites()

        self.n_players = n_players
        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)

        # self.dealer = self.players.take_random()
        self.play = None
        self.dealer = players[0]
        self.blinds_level = 0

        self.is_interactive = False
        self.available_actions = None

    def reset(self):
        CARDS.clear()
        BUTTONS.clear()
        self.dealer = self.players.next_to(self.dealer)

    def draw_players_cards(self):
        if self.play is None:
            return
        for i, player in enumerate(self.players.starting):
            if player.hand is not None:
                player_cell = PLAYERS_CELLS[self.n_players][i]

                x = WIDTH / COLS * player_cell[1] + CARD_X_OFFSET
                y = HEIGHT / ROWS * player_cell[0] + CARD_Y_OFFSET

                local_offset_x = 0
                local_offset_y = 0
                for card in player.hand.cards:
                    orientation = CELLS_ORIENTATIONS[player_cell]
                    card_game = Card(
                        x + local_offset_x, y + local_offset_y, orientation, card
                    )
                    card_game.draw()

                    if orientation == 270 or orientation == 90:
                        local_offset_y += card_game.image.get_height() + 4
                    else:
                        local_offset_x += card_game.image.get_width() + 4

    def draw_community_cards(self):
        if self.play is None:
            return
        offset_x = 0
        x, y = 449, 313

        for card in self.play.community.cards:
            card_game = Card(x + offset_x, y, 0, card)
            card_game.draw()
            offset_x += card_game.image.get_width() + 8

    def draw_buttons(self):
        if not self.is_interactive:
            return
        self.available_actions.sort()
        x, y = LAST_BUTTON_X, BUTTONS_Y
        offset_x = 16

        for action in reversed(self.available_actions):
            button = ButtonGUI(x, y, action)
            button.rect.left -= offset_x + button.image.get_width()
            if button.draw():
                self.play.execute_action(action)
                self.is_interactive = False

            offset_x += button.image.get_width() + 16

    def build_buttons(self):
        x, y = LAST_BUTTON_X, BUTTONS_Y
        offset_x = 16

        for action in Action:
            button = ButtonGUI(x, y, action)
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
                        x + local_offset_x, y + local_offset_y, orientation, False, card
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
            card_gui = CardGUI(x + offset_x, y, 0, False, card)
            CARDS[card] = card_gui
            offset_x += card_gui.image.get_width() + 8

    def draw_window(self):
        WIN.fill(COLORS["BORDEAUX"])

        for card in CARDS.values():
            card.draw()
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
                if self.play is None:
                    self.play = Play(self.players, self.dealer, self.blinds_level)
                    self.build_buttons()
                    self.build_players_cards()
                if self.play.current_player is None:
                    if self.play.round > Round.End:
                        self.play = None
                        self.reset()
                    else:
                        self.play._init_round()
                        self.build_new_community_cards()
                else:
                    self.available_actions = self.play.take_turn_actions()
                    if self.available_actions is not None:
                        self.is_interactive = True

            self.draw_window()
            if self.players.get_n_active() <= 1:
                run = False

        pygame.quit()


if __name__ == "__main__":
    n = 4
    players = ["John", "Lucy", "Carl", "Mark"]#, "Hannah", "Mike", "Lana", "Phil"]
    game = Game(n, players)
    game.loop()