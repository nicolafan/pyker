import enum
from multiprocessing.sharedctypes import Value
import random


class Suit(enum.Enum):
    Clubs = enum.auto()
    Diamonds = enum.auto()
    Hearts = enum.auto()
    Spades = enum.auto()


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
    def __init__(self, suit, rank) -> None:
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

    def deal(self, n_players):
        return [(self.pop(), self.pop()) for i in range(n_players)]


class Hand:
    def __init__(self, cards):
        if len(cards) != 2:
            raise ValueError('Unvalid number of cards for the hand.')

        self.cards = cards


class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = None

    def deal_hand(self, hand: Hand):
        self.hand = hand


class Game:
    def __init__(self, n_players, players_names):
        if n_players < 2 or n_players > 8:
            raise ValueError('Unvalid number of players.')
        self.n_players = n_players
        self.players_names = players_names

        self.players = [Player(name, 500) for name in players_names]
        self.dealer = random.randint(0, n_players - 1)

    def loop(self):
        while len(self.players) > 1:
            round = Round(self)
            round.loop()


class Round:
    def __init__(self, game: Game):
        self.game = game

        self.deck = Deck()
        self.deck.shuffle()
        self.active_players = self.game.players
        dealings = self.deck.deal(len(self.active_players))

        # shall start from dealer
        for i, hand_cards in enumerate(dealings):
            self.active_players[i].deal_hand(Hand(hand_cards))

    def loop(self):
        for player in self.active_players:
            print(player.hand.cards[0], player.hand.cards[1])


game = Game(3, ['Brooks', 'John', 'Leo'])
game.loop()
