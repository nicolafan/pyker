import math
from pyker.entities import *
from pyker.hands_checker import get_winners


class Game:
    def __init__(self, n_players, players_names):
        if not 2 <= n_players <= 8:
            raise ValueError("Unvalid number of players.")

        players = [Player(name, 2000) for name in players_names]
        self.players = Players(players)

        # self.dealer = self.players.take_random()
        self.dealer = players[0]
        self.blinds_level = 0

    def loop(self):
        while self.players.get_n_active() > 1:
            play = Play(self)
            play.loop()
            if self.players.get_n_active() > 1:
                self.dealer = self.players.next_to(self.dealer)

        print(f"The winner is {self.players.active[0].name}")


class Play:
    def __init__(self, game: Game):
        self.game = game

        self.deck = Deck()
        self.players = self.game.players
        self.folded_players = set()
        self.dealer = self.game.dealer

        self._deal()

        self.community = Community()
        # set bets
        self.small_blind_bet = blinds_table[self.game.blinds_level]["small"]
        self.big_blind_bet = blinds_table[self.game.blinds_level]["big"]

        # set blinds
        self.small_blind = self.players.next_to(self.dealer)
        self.big_blind = self.players.next_to(self.small_blind)

        # blinds bet
        self._pay(self.small_blind, self.small_blind_bet)
        self._pay(self.big_blind, self.big_blind_bet)
        self.min_allowed_bet = self.big_blind_bet
        self.highest_round_bet = self.big_blind_bet

    def _reset_round(self):
        self.min_allowed_bet = self.big_blind_bet
        self.highest_round_bet = 0
        self.players.reset_round_bets()

    def loop(self):
        self._run_round(Round.PreFlop)
        self.deck.deal_community_cards(self.community)
        print(self.community.cards[0], self.community.cards[1], self.community.cards[2])
        self._reset_round()
        self._run_round(Round.Flop)
        self.deck.deal_community_cards(self.community)
        print(self.community.cards[3])
        self._reset_round()
        self._run_round(Round.Turn)
        self.deck.deal_community_cards(self.community)
        print(self.community.cards[4])
        self._reset_round()
        self._run_round(Round.River)

        # manage end play
        pot = sum([player.total_bet for player in self.players.active])
        while pot > 0:
            winners = get_winners(
                [
                    player
                    for player in self.players.active
                    if player.total_bet > 0 and not player in self.folded_players
                ],
                self.community,
            )
            min_bet = min(
                [
                    player.total_bet
                    for player in self.players.active
                    if player.total_bet > 0
                ]
            )
            pot_to_assign = min_bet * len(
                [
                    player
                    for player in self.players.active
                    if player.total_bet >= min_bet
                ]
            )
            amount = math.ceil(pot_to_assign / len(winners))

            for winner in winners:
                winner.chips += amount

            pot -= pot_to_assign

            for player in self.players.active:
                if player.total_bet >= min_bet:
                    player.total_bet -= min_bet

        self.players.remove_losers()

    def _deal(self):
        self.deck.shuffle()

        self.dealer.hand = self.deck.deal_hand()
        next_player = self.players.next_to(self.dealer)
        while next_player != self.dealer:
            next_player.hand = self.deck.deal_hand()
            next_player = self.players.next_to(next_player)

    def _pay(self, player: Player, amount: int):
        player.chips -= amount
        player.round_bet += amount
        player.total_bet += amount

    def _actions(self, player: Player):
        actions = [Action.Fold]

        if player.round_bet == self.highest_round_bet:
            actions.append(Action.Check)
        else:
            actions.append(Action.Call)

        # improve this function
        if player.chips > self.highest_round_bet:
            actions.append(Action.BetOrRaise)

        return actions

    def _bet(self, player: Player):
        amount_to_call = self.highest_round_bet - player.round_bet
        new_bet = int(input("Insert your bet: "))

        while new_bet < self.min_allowed_bet or new_bet > player.chips - amount_to_call:
            # raise ValueError('Can\t bet this amount.')
            new_bet = int(input("Insert your bet: "))
            if new_bet == player.chips - amount_to_call:  # all-in
                break

        # first of all player calls
        self._pay(player, amount_to_call)

        self.min_allowed_bet = max(self.min_allowed_bet, new_bet)
        self._pay(player, new_bet)
        self.highest_round_bet = player.round_bet

    def _run_round(self, round: Round):
        player = self.players.next_to(self.dealer)
        last_player = self.players.first_active_from_backwards(self.dealer)
        last_better = None  # blinds are treated as exceptions

        if round == Round.PreFlop:
            player = self.players.next_to(self.big_blind)
            last_player = self.big_blind

        while True:

            players_with_actions = [
                player
                for player in self.players.active
                if player not in self.folded_players and player.chips > 0
            ]
            if not players_with_actions or (
                len(players_with_actions) == 1
                and players_with_actions[0].round_bet == self.highest_round_bet
            ):
                break

            if player in self.folded_players or player.chips == 0:
                player = self.players.next_to(player)
                continue

            if player == last_better:
                break

            print(player.name, player.hand.cards[0], player.hand.cards[1], player.chips)

            actions = self._actions(player)
            print(actions)
            idx_action = int(input("Select an action:"))

            action = actions[idx_action]

            if action == Action.Fold:
                self.folded_players.add(player)

            elif action == Action.Call:
                self._pay(
                    player, min(player.chips, self.highest_round_bet - player.round_bet)
                )

            elif action == Action.BetOrRaise:
                last_better = player
                self._bet(player)

            if last_better == None and player == last_player:
                break

            player = self.players.next_to(player)

        print("END BETTING ROUND")


game = Game(4, ["Brooks", "John", "Leo", "Lisa"])
print(game.dealer.name, game.players.next_to(game.dealer).name, game.players.active)
game.loop()
