import math
from pyker.entities import *
from pyker.hands_checker import get_winners


class Play:
    def __init__(self, players, dealer, blinds_level):
        self.deck = Deck()
        self.players = players
        self.folded_players = set()
        self.round = Round.PreFlop
        self.current_player = None
        self.dealer = dealer

        self._deal()

        self.community = Community()
        # set bets
        self.small_blind_bet = blinds_table[blinds_level]["small"]
        self.big_blind_bet = blinds_table[blinds_level]["big"]

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

    def end(self):
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
        self.round += 1

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

    def _init_round(self):
        if self.round == Round.End:
            self.end()
            return

        if self.round > Round.PreFlop:
            self.deck.deal_community_cards(self.community)
            for card in self.community.cards:
                print(card)

        self.current_player = self.players.next_to(self.dealer)
        self.round_last_player = self.players.first_active_from_backwards(self.dealer)
        while self.round_last_player in self.folded_players:
            print(self.folded_players)
            self.round_last_player = self.players.previous_than(self.round_last_player)
        self.round_last_better = None  # blind are treated as exceptions

        if self.round == Round.PreFlop:
            self.current_player = self.players.next_to(self.big_blind)
            self.round_last_player = self.big_blind

    def execute_action(self, action: Action):
        if action == Action.Fold:
            self.folded_players.add(self.current_player)
        elif action == Action.Call:
            self._pay(
                self.current_player,
                min(
                    self.current_player.chips,
                    self.highest_round_bet - self.current_player.round_bet,
                ),
            )
        elif action == Action.BetOrRaise:
            self.round_last_better = self.current_player
            self._bet(self.current_player)

        if self.current_player is self.round_last_player:
            print("ehi")
            self.current_player = None
            self._reset_round()
            self.round += 1
        else:
            self.current_player = self.players.next_to(self.current_player)

    def take_turn_actions(self):
        players_with_actions = [
            player
            for player in self.players.active
            if player not in self.folded_players and player.chips > 0
        ]
        if not players_with_actions or (
            len(players_with_actions) == 1
            and players_with_actions[0].round_bet == self.highest_round_bet
        ):
            self.current_player = None
            self.round += 1
            return None

        if self.current_player in self.folded_players or self.current_player.chips == 0:
            self.current_player = self.players.next_to(self.current_player)
            return None

        if self.current_player == self.round_last_better:
            self.current_player = None
            self.round += 1
            return None

        print(
            self.current_player.name,
            self.current_player.hand.cards[0],
            self.current_player.hand.cards[1],
            self.current_player.chips,
        )

        actions = self._actions(self.current_player)
        print(actions)
        return actions
