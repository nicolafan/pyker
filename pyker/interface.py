import pygame
import enum

from pyker.game import Play
from pyker.models import *
from pyker.gui.components import *
from pyker.gui.constants import *

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pyker - Poker Texas Hold'em")

# probably will be moved somewhere else
LAST_BUTTON_X = 1200
BUTTONS_Y = 650

BUTTON_GUIS = {}
PLAYER_GUIS = {}
COMMUNITY_CARD_GUIS = {}
OBJECT_GUIS = {}


class GuiObjects(enum.IntEnum):
    BetText = 0

class GameStatus(enum.IntEnum):
    Free = 0
    Choice = 1
    Betting = 2


class Game:
    """Single instance of an entire Poker game
    """
    def __init__(self, players_names):
        if not 2 <= len(players_names) <= 8:
            raise ValueError("Unvalid number of players.")

        self.n_players = len(players_names)
        players = []

        for i, name in enumerate(players_names):
            players.append(Player(name, 2000, is_you=i == 0))
        self.you = players[0]
        self.players = Players(players)

        self.play = None  # the current play
        self.dealer = players[0]  # keep track of the dealer
        self.blinds_level = 0  # keep track of the blinds level - HAS TO BE UPDATED

        self.status = GameStatus.Free # waiting for the action
        self.available_actions = None

        # other stuff
        self.bet_text = None

    def reset(self):
        """Stuff to do at the end of a play
        """
        BUTTON_GUIS.clear()
        PLAYER_GUIS.clear()
        COMMUNITY_CARD_GUIS.clear()
        self.dealer = self.players.next_to(self.dealer)

    def build_buttons(self):
        """Create the buttons dictionary

        Not sure about what I'm doing with the LAST_BUTTON things,
        by the way they probably can be just move inside here
        """
        x, y = LAST_BUTTON_X, BUTTONS_Y
        offset_x = 16

        for action in Action:
            button = ButtonGUI(action, topleft=(x, y))
            button.rect.left -= offset_x + button.image.get_width()
            offset_x += button.image.get_width() + 16
            BUTTON_GUIS[action] = button

    def build_player_guis(self):
        """Build the player guis dictionary

        Each player has a player GUI object associated in components
        that will show everything related to the player (name, cards, etc.)
        """
        for i, player in enumerate(self.players.starting):
            PLAYER_GUIS[player] = PlayerGUI(player, self.n_players, i, player==self.dealer)

    def update_players_info(self):
        """Info in the GUI must be updated, like the chips count
        """
        for player_gui in PLAYER_GUIS.values():
            player_gui.update_player_info()

    def build_new_community_cards(self):
        """Create the community cards
        """
        offset_x = 0
        x, y = 449, 313

        for card in self.play.community.cards:
            card_gui = CardGUI(card, topleft=(x + offset_x, y))
            COMMUNITY_CARD_GUIS[card] = card_gui
            offset_x += card_gui.image.get_width() + 8

    def draw_window(self):
        """Draw everything
        """
        WIN.fill(COLORS["BORDEAUX"])

        for player_gui in PLAYER_GUIS.values():
            player_gui.draw(WIN)
        for card_gui in COMMUNITY_CARD_GUIS.values():
            card_gui.draw(WIN)
        if self.status is GameStatus.Choice:
            for action in self.available_actions:
                if BUTTON_GUIS[action].draw(WIN):
                    if action is Action.BetOrRaise:
                        self.status = GameStatus.Betting
                    else:
                        self.play.execute_action(action)
                        self.status = GameStatus.Free
        
        for object_gui in OBJECT_GUIS.values():
            object_gui.draw(WIN)

        pygame.display.update()

    def loop(self):
        """Main game loop
        """
        clock = pygame.time.Clock()
        run = True
        self.status = GameStatus.Free

        self.available_actions = None

        while run:
            clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                    if event.type == pygame.QUIT:
                        run = False
                
            if self.status is GameStatus.Betting:
                if self.bet_text is None:
                    self.bet_text = "$"
                    bet_text_gui = TextGUI(
                        text=self.bet_text,
                        size=FontSize.Large,
                        topleft=(500, 500)
                    )
                    OBJECT_GUIS[GuiObjects.BetText] = bet_text_gui
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            try:
                                self.play.execute_action(Action.BetOrRaise, int(self.bet_text[1:]))
                            except ValueError:
                                self.bet_text = "$"
                                break
                            self.bet_text = None
                            self.status = GameStatus.Free
                        else:
                            self.bet_text += event.unicode
                            OBJECT_GUIS[GuiObjects.BetText].update_text(self.bet_text)
            else:
                self.update_players_info()

                if self.play is None:  # start new play
                    self.play = Play(self.players, self.dealer, self.blinds_level)
                    self.build_buttons()
                    self.build_player_guis()

                if self.play.current_player is None:  # round ended
                    if self.play.current_round > Round.End:  # play ended
                        self.play = None
                        self.reset()
                    else:
                        self.play.init_round()  # start new round
                        self.build_new_community_cards()
                else:
                    self.available_actions = self.play.take_turn()  # action!
                    if self.available_actions is not None:
                        self.status = GameStatus.Choice

            self.draw_window()
            if self.players.get_n_active() <= 1:
                run = False

        pygame.quit()


if __name__ == "__main__":
    players = ["John", "Lucy", "jasdfksa", "aa", "bb", "cc", "dd", "ee"]
    game = Game(players)
    game.loop()
