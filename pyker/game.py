import enum
from multiprocessing.sharedctypes import Value
import random
from typing import List


class Suit(enum.Enum):
    Clubs = enum.auto()
    Diamonds = enum.auto()
    Hearts = enum.auto()
    Spades = enum.auto()


class Action(enum.Enum):
    Bet = enum.auto()
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


class Hand:
    def __init__(self):
        self.cards = []

    def deal(self, deck: Deck):
        for i in range(2):
            self.cards.append(deck.pop())


class Community:
    def __init__(self):
        self.cards = []

    def deal_flop(self, deck: Deck):
        for i in range(3):
            self.cards.append(deck.pop())

    def deal_turn(self, deck: Deck):
        self.cards.append(deck.pop())

    def deal_river(self, deck: Deck):
        self.cards.append(deck.pop())


class Player:
    def __init__(self, name, chips):
        self.name = name
        self.chips = chips
        self.hand = None
        self.bet = 0


class Players:
    def __init__(self, players: List):
        self.starting = players
        self.active = players
    
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
        checked = 0
        
        while checked < self.get_n_starting():
            idx += 1
            idx %= self.get_n_starting()
            possible_next_player = self.starting[idx]
            if self.is_active(possible_next_player):
                if possible_next_player == player:
                    raise ValueError('Only one player left in the game. The game has already ended.')
                return player
            checked += 1
        
        raise ValueError('The player was not among the players of this game.')
    
    def previous_than(self, player: Player):
        idx = self.starting.index(player)
        checked = 0
        
        while checked < self.get_n_starting():
            idx -= 1
            if idx == -1:
                idx = self.get_n_starting - 1
            idx %= self.get_n_starting()
            possible_next_player = self.starting[idx]
            if self.is_active(possible_next_player):
                if possible_next_player == player:
                    raise ValueError('Only one player left in the game. The game has already ended.')
                return player
            checked += 1
        
        raise ValueError('The player was not among the players of this game.')
    
    def take_random(self):
        idx = random.randint(0, self.get_n_active())
        return self.active[idx]


class Game:
    def __init__(self, n_players, players_names):
        if n_players < 2 or n_players > 8:
            raise ValueError('Unvalid number of players.')

        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)
        self.dealer = self.players.take_random()
        self.blinds_level = 0

    def loop(self):
        while len(self.players) > 1:
            play = Play(self)
            play.run_round(Round.PreFlop)
            play.run_round(Round.Flop)
            play.run_round(Round.Turn)
            play.run_round(Round.River)
            self.dealer_idx += 1
            self.dealer_idx %= len(self.players)


class Play:
    def __init__(self, game: Game):
        self.game = game
        self.pot = 0

        self.deck = Deck()
        self.active_players = self.game.players
        self.dealer_idx = self.game.dealer_idx

        self._deal()

        # set bets
        self.small_blind_bet = blinds_table[self.game.blinds_level]['small']
        self.big_blind_bet = blinds_table[self.game.blinds_level]['big']

        # set blind indexes
        self.small_blind_idx = (self.game.dealer_idx +
                                1) % len(self.active_players)
        self.big_blind_idx = (self.small_blind_idx +
                              1) % len(self.active_players)

        # blinds bet
        self._pay(
            self.active_players[self.small_blind_idx], self.small_blind_bet)
        self._pay(self.active_players[self.big_blind_idx], self.big_blind_bet)
        self.min_allowed_bet = self.big_blind_bet
        self.highest_round_bet = self.big_blind_bet

    def _deal(self):
        self.deck.shuffle()
        dealings = self.deck.deal(len(self.active_players))

        # shall start from dealer
        for i, hand_cards in enumerate(dealings):
            player_idx = (self.dealer_idx + i) % len(self.active_players)
            self.active_players[player_idx].hand = Hand(hand_cards)

    def _pay(self, player: Player, amount: int):
        real_amount = min(amount, player.chips)
        player.chips -= real_amount
        self.pot += real_amount
        player.bet = real_amount

    def _actions(self, player: Player):
        actions = [Action.Fold]

        if player.bet == self.highest_round_bet:
            actions.append(Action.Check)
        else:
            actions.append(Action.Call)

        # improve this function
        if player.chips > 0:
            actions.append(Action.Bet)

        return actions

    def _bet(self, player: Player):
        bet = int(input('Insert your bet: '))

        while bet < self.highest_round_bet + self.min_allowed_bet or bet > player.chips:
            # raise ValueError('Can\t bet this amount.')
            bet = int(input('Insert your bet: '))

        self.min_allowed_bet = bet - self.highest_round_bet
        self.highest_round_bet = bet

        bet -= player.bet
        self._pay(player, bet)

    def run_round(self, round: Round):
        folded = set()
        i = self.dealer_idx
        end_idx = (self.dealer_idx + len(self.active_players) -
                   1) % len(self.active_players)
        last_player = self.active_players[end_idx]
        last_better = None

        while True:
            player = self.active_players[i]

            if player in folded:
                i += 1
                continue

            if player == last_better:
                break

            print(player.name, player.hand.cards[0],
                  player.hand.cards[1], player.chips)

            actions = self._actions(player)
            print(actions)
            idx_action = int(input("Select an action:"))
            action = actions[idx_action]

            if action == Action.Fold:
                folded.add(player)

            elif action == Action.Call:
                self._pay(player, self.highest_round_bet - player.bet)

            elif action == Action.Bet:
                last_better = player
                self._bet(player)

            if last_better == None and player == last_player:
                break

            i += 1
            i %= len(self.active_players)

        self.active_players = [
            player for player in self.active_players if player not in folded]
        print("END BETTING ROUND")


game = Game(4, ['Brooks', 'John', 'Leo', 'Lisa'])
game.loop()
