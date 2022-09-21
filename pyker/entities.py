import enum
import random
import string
from typing import List

class Suit(enum.Enum):
    Clubs = enum.auto()
    Diamonds = enum.auto()
    Hearts = enum.auto()
    Spades = enum.auto()


class Action(enum.Enum):
    BetOrRaise = enum.auto()
    Call = enum.auto()
    Check = enum.auto()
    Fold = enum.auto()


class Round(enum.Enum):
    PreFlop = enum.auto()
    Flop = enum.auto()
    Turn = enum.auto()
    River = enum.auto()


suit_names = {
    Suit.Clubs: 'clubs',
    Suit.Diamonds: 'diamonds',
    Suit.Hearts: 'hearts',
    Suit.Spades: 'spades'
}

rank_symbols = {
    1: 'A',
    2: '2',
    3: '3',
    4: '4',
    5: '5',
    6: '6',
    7: '7',
    8: '8',
    9: '9',
    10: '10',
    11: 'J',
    12: 'Q',
    13: 'K'
}

blinds_table = {
    0: {'small': 25, 'big': 50, 'time': 15 * 60},
    1: {'small': 50, 'big': 100, 'time': 30 * 60},
    2: {'small': 75, 'big': 150, 'time': 45 * 60},
    3: {'small': 100, 'big': 200, 'time': 60 * 60},
    4: {'small': 200, 'big': 400, 'time': 75 * 60},
    5: {'small': 400, 'big': 800, 'time': 90 * 60},
    6: {'small': 800, 'big': 1600, 'time': 105 * 60}
}


class Card:
    def __init__(self, suit: Suit, rank: int) -> None:
        self.suit = suit
        self.rank = rank

    def __lt__(self, other):
        return self.rank < other.rank

    def __str__(self):
        return rank_symbols[self.rank] + " of " + suit_names[self.suit]


class Deck:
    def __init__(self):
        self.cards = []
        for i in range(1, 14):
            self.cards.append(Card(Suit.Clubs, i))
            self.cards.append(Card(Suit.Diamonds, i))
            self.cards.append(Card(Suit.Hearts, i))
            self.cards.append(Card(Suit.Spades, i))

    def shuffle(self):
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop(0)


class Hand:
    def __init__(self, deck: Deck):
        self.cards = []

        for i in range(2):
            self.cards.append(deck.pop())


class Community:
    def __init__(self, deck: Deck):
        self.cards = []
        self.deck = deck

    def deal(self, round: Round):
        n_cards = 1

        if round == round.Flop:
            n_cards = 3
        for i in range(n_cards):
            self.cards.append(self.deck.pop())


class Player:
    def __init__(self, name: string, chips: int):
        self.name = name
        self.chips = chips
        self.hand = None
        self.bet = 0


class Players:
    def __init__(self, players: List[Player]):
        self.starting = players
        self.active = players.copy()

    def is_active(self, player: Player):
        return player in self.active

    def get_n_starting(self):
        return len(self.starting)

    def get_n_active(self):
        return len(self.active)

    def remove_loser(self, player: Player):
        self.active.remove(player)

    def next_to(self, player: Player):
        idx = self.starting.index(player)
        n_checked = 1

        while n_checked < self.get_n_starting():
            idx += 1
            idx %= self.get_n_starting()
            possible_next_player = self.starting[idx]
            if self.is_active(possible_next_player):
                if possible_next_player == player:
                    raise ValueError(
                        'Only one player left in the game. The game has already ended.')
                return possible_next_player
            n_checked += 1

        raise ValueError('The player was not among the players of this game.')

    def previous_than(self, player: Player):
        idx = self.starting.index(player)
        n_checked = 0

        while n_checked < self.get_n_starting():
            idx -= 1
            if idx == -1:
                idx = self.get_n_starting() - 1
            idx %= self.get_n_starting()
            possible_previous_player = self.starting[idx]
            if self.is_active(possible_previous_player):
                if possible_previous_player == player:
                    raise ValueError(
                        'Only one player left in the game. The game has already ended.')
                return possible_previous_player
            n_checked += 1

        raise ValueError('The player was not among the players of this game.')

    def take_random(self):
        idx = random.randint(0, self.get_n_active() - 1)
        return self.active[idx]

    def first_active_from(self, player: Player):
        if self.is_active(player):
            return player
        return self.next_to(player)

    def first_active_from_backwards(self, player: Player):
        if self.is_active(player):
            return player
        return self.previous_than(player)