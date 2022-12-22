import threading
import pygame
import enum
from queue import Queue

from pyker.game.game import Game
from pyker.game.models import *
from pyker.gui.components import *
from pyker.gui.constants import *
from pyker.ai.dummy import Dummy

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
    Pot = 1
    WinnerText = 2


class GameStatus(enum.IntEnum):
    Free = 0
    Choice = 1
    Betting = 2
    ArtificialIntelligence = 3
    ShowWinner = 4
    EndGame = 5


class Interface:
    """Single instance of an entire Poker game"""

    def __init__(self, players_names):
        if not 2 <= len(players_names) <= 8:
            raise ValueError("Unvalid number of players.")

        self.n_players = len(players_names)
        players = []

        for i, name in enumerate(players_names):
            players.append(Player(name, i))

        self.game = Game(players)
        self.you = players[0]
        self.queue = Queue()

        self.status = GameStatus.Free  # waiting for the action
        self.available_actions = None

        # other stuff
        self.bet_text = None
        self.pot = 0
        self.cards_discovered = False
        self.winners = None

        self.previous_state = None
        self.state = None
        self.gui_built = False

        self.i = 0

    def reset(self):
        """Stuff to do at the end of a play"""
        BUTTON_GUIS.clear()
        PLAYER_GUIS.clear()
        COMMUNITY_CARD_GUIS.clear()
        OBJECT_GUIS.clear()
        self.pot = 0

    def update_state(self):
        for player_gui in PLAYER_GUIS.values():
            player_gui.update_state(self.state)

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
        for player in self.state.players.active:
            PLAYER_GUIS[player] = PlayerGUI(
                player, self.state, self.n_players
            )
        for player_gui in PLAYER_GUIS.values():
            player_gui.update_state(self.state)

    def build_pot_gui(self):
        self.pot = self.state.get_pot()

        OBJECT_GUIS[GuiObjects.Pot] = TextGUI(
            text=f"${self.pot}",
            size=FontSize.Large,
            topleft=(600, 240),
            color=(255, 255, 0),
        )

    def build_new_community_cards(self):
        """Create the community cards"""
        offset_x = 0
        x, y = 449, 313

        for card in self.state.community.cards:

            card_gui = CardGUI(card, topleft=(x + offset_x, y))
            COMMUNITY_CARD_GUIS[card] = card_gui
            offset_x += card_gui.image.get_width() + 8

    def draw_window(self):
        """Draw everything"""
        WIN.fill(COLORS["BORDEAUX"])

        # show player guis
        for player_gui in PLAYER_GUIS.values():
            player_gui.draw(WIN)

        # show community cards
        for card_gui in COMMUNITY_CARD_GUIS.values():
            card_gui.draw(WIN)

        # show buttons
        if self.status is GameStatus.Choice:
            for action in self.available_actions:
                if isinstance(action, tuple):
                    action = action[0]
                if BUTTON_GUIS[action].draw(WIN):
                    self.i += 1
                    if action is Action.BetOrRaise:
                        self.status = GameStatus.Betting
                    else:
                        self.previous_state = self.state
                        self.state = self.game.result(self.state, action) # EXECUTE ACTION 1
                        self.build_pot_gui()
                        self.update_state()
                        self.status = GameStatus.Free
                        if self.game.is_final(self.state):
                                self.status = GameStatus.ShowWinner

        # show objects (custom code for each object)
        for gui_object in GuiObjects:
            if gui_object in OBJECT_GUIS:
                if (
                    gui_object is GuiObjects.BetText
                    and not self.status is GameStatus.Betting
                ):
                    continue
                OBJECT_GUIS[gui_object].draw(WIN)

        pygame.display.update()

    def loop(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        run = True
        self.status = GameStatus.Free

        self.available_actions = None

        self.state = self.game.initial_state()

        while run:
            clock.tick(FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    run = False

            if self.status is GameStatus.Betting:
                # bet text area
                if self.bet_text is None:
                    self.bet_text = "$"
                    bet_text_gui = TextGUI(
                        text=self.bet_text, size=FontSize.Large, topleft=(500, 500)
                    )
                    OBJECT_GUIS[GuiObjects.BetText] = bet_text_gui
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.previous_state = self.state
                            range = (0, 0)
                            for action in self.game.actions(self.previous_state):
                                if isinstance(action, tuple):
                                    range = action[1]

                            self.state = self.game.result(
                                self.state,
                                Action.BetOrRaise,
                                amount=int(self.bet_text[1:]),
                                range=range
                            ) # EXECUTE ACTION 2
                            self.build_pot_gui()
                            self.update_state()
                            self.bet_text = None
                            self.status = GameStatus.Free
                            if self.game.is_final(self.state):
                                self.status = GameStatus.ShowWinner
                        elif event.key == pygame.K_ESCAPE:
                            self.bet_text = None
                            self.status = GameStatus.Choice
                        else:
                            self.bet_text += event.unicode
                            OBJECT_GUIS[GuiObjects.BetText].update_text(self.bet_text)
            elif self.status is GameStatus.ShowWinner:
                while len(COMMUNITY_CARD_GUIS) < 5:
                    self.build_new_community_cards()
                if not self.cards_discovered:
                    self.cards_discovered = True
                    for player_gui in PLAYER_GUIS.values():
                        player_gui.discover_cards()
                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            self.cards_discovered = False
                            self.status = GameStatus.Free
                            self.previous_state = self.state
                            if self.state.endgame:
                                self.status = GameStatus.EndGame
                            else:
                                self.state = self.game.initial_state(self.previous_state)
            elif self.status is GameStatus.EndGame:
                if not GuiObjects.WinnerText in OBJECT_GUIS:
                    winner = [player.name for (player, chips) in self.state.chips.items() if chips > 0][0]
                    winner_text = f"The winner is {winner}"
                    winner_text_gui = TextGUI(
                        winner_text,
                        size=FontSize.Large,
                        topleft=(320, 320),
                        color=COLORS["BLACK"],
                    )
                    OBJECT_GUIS[GuiObjects.WinnerText] = winner_text_gui

                for event in events:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            run = False
            elif self.status is GameStatus.ArtificialIntelligence:
                if self.queue.qsize() > 0:
                    action = self.queue.get()
                    self.previous_state = self.state
                    if isinstance(action, tuple):
                        self.state = self.game.result(self.state, action[0], amount=action[1], range=action[2])
                    else:
                        self.state = self.game.result(self.state, action)
                    self.build_pot_gui()
                    self.update_state()
                    self.status = GameStatus.Free
                    if self.game.is_final(self.state):
                        self.status = GameStatus.ShowWinner
            elif self.status is GameStatus.Free:
                # self.update_players_info()

                # must be a check on the state to know if it is INITIAL
                # build the interface when starting a new play                
                if self.game.is_initial(self.state) and not self.gui_built:  # start new play
                    self.reset()
                    self.build_buttons()
                    self.build_player_guis()
                    self.build_pot_gui()
                    self.gui_built = True
                
                # deactivate gui_built to build the interface at the next plays
                if self.previous_state is not None and self.game.is_initial(self.previous_state):
                    self.gui_built = False

                if (
                    self.previous_state is not None
                    and self.previous_state.current_round != self.state.current_round
                ):  # round ended
                    if self.state.current_round > Round.End:  # play ended
                        self.reset()
                    self.build_new_community_cards()

                if self.state.current_player == self.you:
                    self.available_actions = self.game.actions(self.state)  # action!
                    if self.available_actions is not None:
                        self.status = GameStatus.Choice
                else:
                    dummy = Dummy(self.game, self.state, self.queue)
                    thread = threading.Thread(target=dummy.run)
                    thread.start()
                    self.status = GameStatus.ArtificialIntelligence

            self.draw_window()

        pygame.quit()


if __name__ == "__main__":
    players = ["John", "Lucy", "Carl", "Hannah", "Luke", "Mike", "Steven", "Leah"]
    game = Interface(players)
    game.loop()
