import enum
import random
import string


class Rank(enum.IntEnum):
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5
    R6 = 6
    R7 = 7
    R8 = 8
    R9 = 9
    R10 = 10
    RJ = 11
    RQ = 12
    RK = 13
    RA = 14


class Suit(enum.IntEnum):
    Clubs = 0
    Diamonds = 1
    Hearts = 2
    Spades = 3


class Action(enum.Enum):
    BetOrRaise = enum.auto()
    Call = enum.auto()
    Check = enum.auto()
    Fold = enum.auto()

    def __str__(self):
        action_str_dict = {
            Action.BetOrRaise: "bet",
            Action.Call: "call",
            Action.Check: "check",
            Action.Fold: "fold",
        }

        return action_str_dict[self]


class Round(enum.IntEnum):
    PreFlop = 1
    Flop = 2
    Turn = 3
    River = 4
    End = 5


suit_names = {
    Suit.Clubs: "clubs",
    Suit.Diamonds: "diamonds",
    Suit.Hearts: "hearts",
    Suit.Spades: "spades",
}

blinds_table = {
    0: {"small": 25, "big": 50, "time": 15 * 60},
    1: {"small": 50, "big": 100, "time": 30 * 60},
    2: {"small": 75, "big": 150, "time": 45 * 60},
    3: {"small": 100, "big": 200, "time": 60 * 60},
    4: {"small": 200, "big": 400, "time": 75 * 60},
    5: {"small": 400, "big": 800, "time": 90 * 60},
    6: {"small": 800, "big": 1600, "time": 105 * 60},
}


class Card:
    def __init__(self, suit: Suit, rank: Rank) -> None:
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __lt__(self, other):
        """Compare two cards for deck ordering

        Args:
            other (Card): The card to compare

        Returns:
            bool: True if self comes before other, False otherwise
        """
        if self.rank < other.rank:
            return True
        if self.rank == other.rank:
            if self.suit < other.suit:
                return True
        return False

    def __str__(self):
        return str(self.rank) + " of " + suit_names[self.suit]

    def __hash__(self):
        return hash(repr(self))

    def code(self):
        """Return a string code for the current card"""
        return self.rank.name[1:] + self.suit.name[0]

    def compare_to_by_rank(self, other):
        """Card comparison by in-game value

        Card comparison according to Poker rules: suit doesn't count.
        """
        comparison = 1

        if self.rank > other.rank:
            comparison = -1
        elif self.rank == other.rank:
            comparison = 0

        return comparison


class Hand:
    """A hand given to a player consisting of two cards"""

    def __init__(self, cards: list[Card]):
        self.cards = cards


class Community:
    """Community cards of a single play"""

    def __init__(self):
        self.cards = []

    def __copy__(self):
        community = Community()
        community.cards = self.cards.copy()
        return community


class Deck:
    """Deck of cards"""

    def __init__(self):
        self.cards = [Card(suit, rank) for rank in Rank for suit in Suit]

    def __copy__(self):
        deck = Deck()
        deck.cards = self.cards.copy()
        return deck

    def shuffle(self):
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop(0)

    def deal_hand(self):
        """Return a hand consisting of two cards"""
        return Hand([self.pop(), self.pop()])

    def deal_community_cards(self, community: Community):
        """Add community cards to the community object

        The method understands how many cards to deal based on the number
        of cards already dealt.

        Args:
            community (Community): Container of community cards
        """
        if community.cards:
            # deal turn or river
            community.cards.append(self.pop())
        else:
            # deal flop
            community.cards += [self.pop(), self.pop(), self.pop()]


class Player:
    """Player of the game"""
    def __init__(self, name: string, place: int):
        self.name = name
        self.place = place


class Players:
    """Class for managing the collection of players of the game"""
    def __init__(self, players: list[Player]):
        self.starting = players  # starting players (immutable)
        self.active = players.copy()  # active players (players who haven't lost)

    def __copy__(self):
        players = Players(self.starting)
        players.active = self.active.copy()
        return players

    def is_active(self, player: Player):
        return player in self.active

    def get_n_starting(self):
        """Get number of starting players
        """
        return len(self.starting)

    def get_n_active(self):
        """Get number of active players
        """
        return len(self.active)

    def remove_losers(self, chips: dict[Player, int]):
        """Remove losers from the active players
        """
        self.active = [player for player in self.active if chips[player] > 0]

    def next_to(self, player: Player):
        """Return player after the player obtained as parameter

        Args:
            player (Player): A player of the game

        Raises:
            ValueError: If the player parameter is not present in the players of the game

        Returns:
            Player: The player next to the player obtained as parameter
        """
        idx = self.starting.index(player)
        n_checked = 1

        while n_checked < self.get_n_starting():
            idx += 1
            idx %= self.get_n_starting()
            possible_next_player = self.starting[idx]
            if self.is_active(possible_next_player):
                return possible_next_player
            n_checked += 1

        raise ValueError("The player was not among the players of this game.")

    def previous_than(self, player: Player):
        """Return player before the player obtained as parameter

        Args:
            player (Player): A player of the game

        Raises:
            ValueError: If the player parameter is not present in the players of the game

        Returns:
            Player: The player before the player obtained as parameter
        """
        idx = self.starting.index(player)
        n_checked = 0

        while n_checked < self.get_n_starting():
            idx -= 1
            if idx == -1:
                idx = self.get_n_starting() - 1
            idx %= self.get_n_starting()
            possible_previous_player = self.starting[idx]
            if self.is_active(possible_previous_player):
                return possible_previous_player
            n_checked += 1

        raise ValueError("The player was not among the players of this game.")

    def take_random(self):
        """Return a random player

        Returns:
            Player: A random player
        """
        idx = random.randint(0, self.get_n_active() - 1)
        return self.active[idx]

    def first_active_from(self, player: Player):
        """Return first active player after player (included)

        Args:
            player (Player): Starting player
        """
        if self.is_active(player):
            return player
        return self.next_to(player)

    def first_active_from_backwards(self, player: Player):
        """Return first active player before player (included)

        Args:
            player (Player): Starting player
        """
        if self.is_active(player):
            return player
        return self.previous_than(player)
