import enum
import os
from pathlib import Path

import pygame
from pyker.models import Action, Card

# SPRITES
CARDS_SPRITES = {}
BUTTONS_SPRITES = {}

# FONTS


class FontSize(enum.IntEnum):
    Small = 0,
    Medium = 1,
    Large = 2


FONTS = {}


def load_assets():
    assets_dir = "assets"
    assets_cards_dir = Path(os.path.join(assets_dir, "cards"))
    assets_buttons_dir = Path(os.path.join(assets_dir, "buttons"))
    assets_fonts_dir = Path(os.path.join(assets_dir, "fonts"))

    # load cards sprites
    for filename in os.listdir(assets_cards_dir):
        card_name = filename[:-4]
        card_sprite = pygame.image.load(
            os.path.join(assets_cards_dir, filename))
        card_sprite = pygame.transform.scale(
            card_sprite, (card_sprite.get_width() * 2,
                          card_sprite.get_height() * 2)
        )
        CARDS_SPRITES[card_name] = card_sprite

    # load buttons sprites
    for filename in os.listdir(assets_buttons_dir):
        button_name = filename[:-4]
        button_sprite = pygame.image.load(
            os.path.join(assets_buttons_dir, filename))
        button_sprite = pygame.transform.scale(
            button_sprite,
            (button_sprite.get_width() * 4, button_sprite.get_height() * 4),
        )
        BUTTONS_SPRITES[button_name] = button_sprite

    # load fonts sprites
    pygame.font.init()
    FONTS[FontSize.Small] = pygame.font.Font(
        os.path.join(assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 8)
    FONTS[FontSize.Medium] = pygame.font.Font(
        os.path.join(assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 16)
    FONTS[FontSize.Large] = pygame.font.Font(os.path.join(
        assets_fonts_dir, "PixeloidMono-1G8ae.ttf"), 32)


load_assets()


class CardGUI:
    def __init__(self, window, card: Card, *, covered=False, topleft=(0, 0), angle=0):
        self.window = window
        self.covered = covered
        self.image = pygame.transform.rotate(CARDS_SPRITES[card.code()], angle)
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
    def __init__(self, window, text, *, size=FontSize.Small, topleft=(0, 0), angle=0, color=(255, 255, 255)):
        self.window = window
        self.text = pygame.transform.rotate(
            FONTS[size].render(text, True, color),
            angle
        )
        self.rect = self.text.get_rect()
        self.rect.topleft = topleft

    def draw(self):
        self.window.blit(self.text, self.rect)
