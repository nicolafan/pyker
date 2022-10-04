import enum
import os
from pathlib import Path

import pygame
from pyker.models import Action, Card, Player
from pyker.gui.constants import *


# SPRITES
CARDS_SPRITES = {}
BUTTONS_SPRITES = {}
OTHERS_SPRITES = {}


class FontSize(enum.IntEnum):
    Small = (0,)
    Medium = (1,)
    Large = 2


class Marker(enum.IntEnum):
    Dealer = (0,)
    SmallBlind = (1,)
    BigBlind = 2

    def __str__(self):
        marker_str_dict = {
            Marker.Dealer: "dealer",
            Marker.SmallBlind: "small_blind",
            Marker.BigBlind: "big_blind",
        }

        return marker_str_dict[self]


FONTS = {}


def load_assets():
    assets_dir = "assets"
    assets_cards_dir = Path(os.path.join(assets_dir, "cards"))
    assets_buttons_dir = Path(os.path.join(assets_dir, "buttons"))
    assets_others_dir = Path(os.path.join(assets_dir, "others"))
    assets_fonts_dir = Path(os.path.join(assets_dir, "fonts"))

    # load cards sprites
    for filename in os.listdir(assets_cards_dir):
        card_name = filename[:-4]
        card_sprite = pygame.image.load(os.path.join(assets_cards_dir, filename))
        card_sprite = pygame.transform.scale(
            card_sprite, (card_sprite.get_width() * 2, card_sprite.get_height() * 2)
        )
        CARDS_SPRITES[card_name] = card_sprite

    # load buttons sprites
    for filename in os.listdir(assets_buttons_dir):
        button_name = filename[:-4]
        button_sprite = pygame.image.load(os.path.join(assets_buttons_dir, filename))
        button_sprite = pygame.transform.scale(
            button_sprite,
            (button_sprite.get_width() * 4, button_sprite.get_height() * 4),
        )
        BUTTONS_SPRITES[button_name] = button_sprite

    # load others sprites
    for filename in os.listdir(assets_others_dir):
        other_name = filename[:-4]
        other_sprite = pygame.image.load(os.path.join(assets_others_dir, filename))
        other_sprite = pygame.transform.scale(
            other_sprite, (other_sprite.get_width() * 2, other_sprite.get_height() * 2)
        )
        OTHERS_SPRITES[other_name] = other_sprite

    # load fonts
    pygame.font.init()
    FONTS[FontSize.Small] = pygame.font.Font(
        os.path.join(assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 8
    )
    FONTS[FontSize.Medium] = pygame.font.Font(
        os.path.join(assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 16
    )
    FONTS[FontSize.Large] = pygame.font.Font(
        os.path.join(assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 32
    )


load_assets()


class PlayerGUI:
    player_cells = {
        2: [(0, 3)],
        3: [(1, 0), (1, 6)],
        4: [(1, 0), (0, 3), (1, 6)],
        5: [(1, 0), (0, 1), (0, 5), (1, 6)],
        6: [(1, 0), (0, 1), (0, 3), (0, 5), (1, 6)],
        7: [(2, 1), (1, 0), (0, 1), (0, 5), (1, 6), (2, 5)],
        8: [(2, 1), (1, 0), (0, 1), (0, 3), (0, 5), (1, 6), (2, 5)],
    }

    cell_centers = {}

    for cell in player_cells[8]:
        centerx = WIDTH // COLS * cell[1] + CELL_WIDTH // 2
        centery = HEIGHT // ROWS * cell[0] + CELL_HEIGHT // 2
        cell_centers[cell] = (centerx, centery)

    """Manage the entire presence of a player on the screen (cards, info, objects)
    """

    def __init__(self, window, player: Player, n_players: int, player_idx: int):
        self.window = window
        self.player = player
        
        self.card_guis = {}
        self.player_info_gui = None
        self.is_you = False
        
        self.cell = None
        if player_idx > 0:  # if is not you
            self.cell = self.player_cells[n_players][player_idx - 1]
            self.__build_cards()
        else:
            self.is_you = True
            self.__build_your_cards()

        self.update_player_info()

    def __build_cards(self):
        if self.player.hand is None:
            return

        x, y = self.cell_centers[self.cell]

        card1, card2 = self.player.hand.cards
        card1_gui = CardGUI(self.window, card1)
        card2_gui = CardGUI(self.window, card2)
        card1_gui.rect.right = x - 1
        card2_gui.rect.left = x + 1
        card1_gui.rect.centery = y
        card2_gui.rect.centery = y

        self.card_guis[card1] = card1_gui
        self.card_guis[card2] = card2_gui

    def __build_your_cards(self):
        if self.player.hand is None:
            return

        x, y = WIDTH / 2, 640
        card1, card2 = self.player.hand.cards
        card1_gui = CardGUI(self.window, card1, scale=2)
        card2_gui = CardGUI(self.window, card2, scale=2)
        card1_gui.rect.midright = (x, y)
        card2_gui.rect.midleft = (x, y)

        self.card_guis
        self.card_guis[card1] = card1_gui
        self.card_guis[card2] = card2_gui

    def update_player_info(self):
        if self.player.hand is None:
            return
        
        if self.is_you:
            return

        x, y = self.cell_centers[self.cell]
        self.player_info_gui = PlayerInfoGUI(
            self.window,
            self.player,
            color=COLORS["BLACK"],
            width=CELL_WIDTH - 20,
            height=40,
            centerx=x,
            bottom=y + CELL_HEIGHT // 2,
        )

    def draw(self):
        for card_gui in self.card_guis.values():
            card_gui.draw()
        
        if self.is_you:
            return
        
        self.player_info_gui.draw()


class CardGUI:
    def __init__(
        self, window, card: Card, *, covered=False, topleft=(0, 0), angle=0, scale=1
    ):
        self.window = window
        self.covered = covered
        self.image = pygame.transform.rotate(CARDS_SPRITES[card.code()], angle)
        self.image = pygame.transform.scale(
            self.image,
            (self.image.get_width() * scale, self.image.get_height() * scale),
        )
        self.rect = self.image.get_rect()  # use the rect to move the card
        self.rect.topleft = topleft

    def draw(self):
        self.window.blit(self.image, (self.rect.x, self.rect.y))


class ButtonGUI:
    def __init__(self, window, action, *, topleft=(0, 0), angle=0):
        self.window = window
        self.image = pygame.transform.rotate(BUTTONS_SPRITES[str(action)], angle)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
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

        self.window.blit(self.image, (self.rect.x, self.rect.y))
        return action


class TextGUI:
    def __init__(
        self,
        window,
        text,
        *,
        size=FontSize.Small,
        topleft=(0, 0),
        angle=0,
        color=(255, 255, 255)
    ):
        self.window = window
        self.text = pygame.transform.rotate(
            FONTS[size].render(text, True, color), angle
        )
        self.rect = self.text.get_rect()
        self.rect.topleft = topleft

    def draw(self):
        self.window.blit(self.text, self.rect)


class PlayerInfoGUI:
    def __init__(self, window, player, *, color, width, height, centerx, bottom):
        self.window = window
        self.surface = pygame.Surface((width, height))  # the size of your rect
        self.surface.set_alpha(128)  # alpha level
        self.surface.fill(color)
        self.rect = self.surface.get_rect(centerx=centerx, bottom=bottom)

        self.text_name = TextGUI(window, player.name, size=FontSize.Medium)
        self.text_name.rect.centerx = centerx
        self.text_name.rect.top = self.rect.top

        self.text_chips = TextGUI(window, "$" + str(player.chips), size=FontSize.Medium)
        self.text_chips.rect.centerx = centerx
        self.text_chips.rect.bottom = self.rect.bottom

    def draw(self):
        self.window.blit(self.surface, (self.rect.x, self.rect.y))

        self.text_name.draw()
        self.text_chips.draw()


class MarkerGUI:
    offsets_dict = {
        (2, 1): ("topright", (5, -5)),
        (1, 0): ("topright", (10, 0)),
        (0, 1): ("bottomright", (5, 5)),
        (0, 3): ("bottomright", (0, 10)),
        (0, 5): ("bottomleft", (-5, 5)),
        (1, 6): ("topleft", (-10, 0)),
        (2, 5): ("topleft", (-5, -5)),
    }

    def __init__(
        self, window, marker: Marker, is_you=False, cell=None, *, center=None, angle=0
    ):
        self.window = window
        self.image = pygame.transform.rotate(OTHERS_SPRITES[str(marker)], angle)

    def draw():
        return
