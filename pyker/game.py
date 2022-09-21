from entities import *
from multiprocessing.sharedctypes import Value
from typing import List


class Game:
    def __init__(self, n_players, players_names):
        if not 2 <= n_players <= 8:
            raise ValueError('Unvalid number of players.')

        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)

        self.dealer = self.players.take_random()
        self.blinds_level = 0

    def loop(self):
        while self.players.get_n_active() > 1:
            play = Play(self)
            play.loop()
            self.dealer = self.players.next_to(self.dealer)


class Play:
    def __init__(self, game: Game):
        self.game = game
        self.pot = 0

        self.deck = Deck()
        self.players = self.game.players
        self.folded = set()
        self.dealer = self.game.dealer

        self._deal()

        self.community = Community(self.deck)
        # set bets
        self.small_blind_bet = blinds_table[self.game.blinds_level]['small']
        self.big_blind_bet = blinds_table[self.game.blinds_level]['big']

        # set blinds
        self.small_blind = self.players.next_to(self.dealer)
        self.big_blind = self.players.next_to(self.small_blind)

        # blinds bet
        self._pay(self.small_blind, self.small_blind_bet)
        self._pay(self.big_blind, self.big_blind_bet)
        self.min_allowed_bet = self.big_blind_bet
        self.highest_round_bet = self.big_blind_bet

    def loop(self):
        self._run_round(Round.PreFlop)
        self.community.deal(Round.Flop)
        print(self.community.cards)
        self._run_round(Round.Flop)
        self.community.deal(Round.Turn)
        print(self.community.cards)
        self._run_round(Round.Turn)
        self.community.deal(Round.River)
        print(self.community.cards)
        self._run_round(Round.River)

    def _deal(self):
        self.deck.shuffle()

        self.dealer.hand = Hand(self.deck)
        next_player = self.players.next_to(self.dealer)
        while next_player != self.dealer:
            next_player.hand = Hand(self.deck)
            next_player = self.players.next_to(next_player)

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

    def _run_round(self, round: Round):
        player = self.players.next_to(self.dealer)
        last_player = self.players.first_active_from_backwards(self.dealer)
        last_better = None

        if round == Round.PreFlop:
            player = self.players.next_to(self.big_blind)
            last_player = self.big_blind

        while True:
            if player in self.folded:
                player = self.players.next_to(player)
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
                self.folded.add(player)

            elif action == Action.Call:
                self._pay(player, self.highest_round_bet - player.bet)

            elif action == Action.Bet:
                last_better = player
                self._bet(player)

            if last_better == None and player == last_player:
                break

            player = self.players.next_to(player)

        print("END BETTING ROUND")


game = Game(4, ['Brooks', 'John', 'Leo', 'Lisa'])
print(game.dealer.name, game.players.next_to(
    game.dealer).name, game.players.active)
game.loop()
