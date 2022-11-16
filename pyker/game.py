import math

from pyker.hands_checker import get_winners
from pyker.models import *


class Play:
    """Class for play managament

    Most important class for playing the game.
    It deals with a single play: from dealing to assign winners' chips.
    """

    def __init__(self, players, dealer, blinds_level):
        self.players = players
        self.folded_players = set()  # players who folded during the play

        self.current_round = Round.PreFlop
        self.current_player = None

        # dealings
        self.deck = Deck()  # new complete deck of cards
        self.dealer = dealer
        self.__deal()
        self.community = Community()

        # set blinds and their bets
        self.small_blind_player = self.players.next_to(self.dealer)
        self.big_blind_player = self.players.next_to(self.small_blind_player)
        self.small_blind_bet = blinds_table[blinds_level]["small"]
        self.big_blind_bet = blinds_table[blinds_level]["big"]

        # blinds bet
        self.__pay(
            self.small_blind_player,
            min(self.small_blind_bet, self.small_blind_player.chips)
        )
        self.__pay(
            self.big_blind_player,
            min(self.big_blind_bet, self.big_blind_player.chips)
        )

        # manage round bets
        self.min_allowed_bet = self.big_blind_bet  # min amount to bet or raise
        self.highest_round_bet = self.big_blind_bet  # amount to bet to go to the next round

    def init_round(self):
        if self.current_round == Round.End:
            self.end()
            return

        if self.current_round > Round.PreFlop:
            self.deck.deal_community_cards(self.community)

        # determine starting player, last player (immutable once it's found), and initialize the last better of the round
        self.current_player = self.players.next_to(self.dealer)
        self.round_last_player = self.players.first_active_from_backwards(self.dealer)
        while self.round_last_player in self.folded_players:
            self.round_last_player = self.players.previous_than(self.round_last_player)
        self.round_last_better = None  # blinds are treated as exceptions

        # different order for preflops
        if self.current_round == Round.PreFlop:
            self.current_player = self.players.next_to(self.big_blind_player)
            self.round_last_player = self.big_blind_player

    def __reset_for_round(self):
        """Operations to perform after ending a round"""
        self.current_player = None
        self.current_round += 1
        self.min_allowed_bet = self.big_blind_bet
        self.highest_round_bet = 0
        self.players.reset_for_round()

    def end(self):
        # manage end play
        pot = sum([player.total_bet for player in self.players.active])

        # distribute the entire pot
        while pot > 0:
            ending_players = [
                player
                for player in self.players.active
                if player.total_bet > 0
                and not player in self.folded_players  # not sure about first check
            ]
            winners = get_winners(ending_players, self.community)

            bets = [
                player.total_bet
                for player in self.players.active
                if player.total_bet > 0
            ]
            min_bet = min(bets)

            pot_to_assign = min_bet * len(ending_players)
            pot_to_assing_by_player = math.ceil(pot_to_assign / len(winners))

            for winner in winners:
                winner.chips += pot_to_assing_by_player

            # decrease the pot by the portion assigned
            pot -= pot_to_assign

            # decrease players' bets (at the end the total_bet must be 0)
            for player in self.players.active:
                if player.total_bet >= min_bet:
                    player.total_bet -= min_bet

        # end play
        self.players.remove_losers()
        self.current_round += 1

    def __deal(self):
        self.deck.shuffle()

        self.dealer.hand = self.deck.deal_hand()
        next_player = self.players.next_to(self.dealer)
        while next_player != self.dealer:
            next_player.hand = self.deck.deal_hand()
            next_player = self.players.next_to(next_player)

    def __pay(self, player: Player, amount: int):
        player.chips -= amount
        player.round_bet += amount
        player.total_bet += amount

    def __available_actions(self, player: Player):  # will be modified
        actions = [Action.Fold]

        if player.round_bet == self.highest_round_bet:
            actions.append(Action.Check)
        else:
            actions.append(Action.Call)

        # improve this function
        if player.chips > self.highest_round_bet:
            actions.append(Action.BetOrRaise)

        return actions

    def __bet(self, player: Player):  # will be modified
        amount_to_call = self.highest_round_bet - player.round_bet
        new_bet = int(input("Insert your bet: "))

        while new_bet < self.min_allowed_bet or new_bet > player.chips - amount_to_call:
            # raise ValueError('Can\t bet this amount.')
            new_bet = int(input("Insert your bet: "))
            if new_bet == player.chips - amount_to_call:  # all-in
                break

        # first of all, player calls
        self.__pay(player, amount_to_call)

        self.min_allowed_bet = max(self.min_allowed_bet, new_bet)
        self.__pay(player, new_bet)
        self.highest_round_bet = player.round_bet

    def execute_action(self, action: Action):
        if action == Action.Fold:
            self.folded_players.add(self.current_player)
        elif action == Action.Call:
            self.__pay(
                self.current_player,
                min(
                    self.current_player.chips,
                    self.highest_round_bet - self.current_player.round_bet,
                ),
            )
        elif action == Action.BetOrRaise:
            self.round_last_better = self.current_player
            self.__bet(self.current_player)

        if self.current_player is self.round_last_player and self.round_last_better is None:
            self.__reset_for_round()
        else:
            self.current_player = self.players.next_to(self.current_player)

    def take_turn(self):
        """Player takes next turn

        Checks which actions are available to the current player.
        If no actions are available returns None and manages access to the next round.

        Returns:
            [Action]: A list of actions available for the current player
        """
        # players who can still play (have chips and didn't fold)
        players_with_actions = [
            player
            for player in self.players.active
            if player not in self.folded_players and player.chips > 0
        ]

        # if no players has available actions or there's only one and already called go to next round
        if not players_with_actions or (
            len(players_with_actions) == 1
            and players_with_actions[0].round_bet == self.highest_round_bet
        ):
            self.current_player = None
            self.current_round += 1
            return None

        # if current player folded or doesn't have chips, change player
        if self.current_player in self.folded_players or self.current_player.chips == 0:
            self.current_player = self.players.next_to(self.current_player)
            return None

        # if the player is the last better the round ends
        if self.current_player is self.round_last_better:
            self.__reset_for_round()
            return None

        actions = self.__available_actions(self.current_player)
        return actions
