import math

from pyker.game.hands_checker import get_winners
from pyker.game.models import *

import random
import copy


class State:
    """A state in a poker game, in a factored representation

    It has to be built with a configuration of all the information it must contain.
    It is an atomic entity: it cannot be changed, it is the Game that must use it to create a new state 
    and perform a transition via execution of players' actions.
    """

    def __init__(
        self,
        players: Players,
        deck: Deck,
        current_round: Round,
        current_player: Player,
        starting_chips: dict[Player, int],
        bets: dict[Player, int],
        total_bets: dict[Player, int],
        hands: dict[Player, Hand],
        community: Community,
        folded_players: set[Player],
        round_last_player: Player,
        round_last_better: Player,
        min_allowed_bet: int,
        dealer: Player,
        blinds_level: int,
        is_initial: bool=False,
        is_final: bool=False,
        winners: list[Player] | None=None
    ):
        self.players = players
        self.deck = deck
        self.current_round = current_round
        self.current_player = current_player
        self.starting_chips = starting_chips
        self.bets = bets  # bets at the current round
        self.total_bets = total_bets  # sum of bets during entire play
        self.hands = hands
        self.community = community
        self.folded_players = folded_players
        self.round_last_player = round_last_player
        self.round_last_better = round_last_better
        self.min_allowed_bet = min_allowed_bet
        self.dealer = dealer
        self.blinds_level = blinds_level
        self.is_initial = is_initial
        self.is_final = is_final
        self.winners = winners

        self.endgame = False

        self.n_players = len(players.active)
        self.current_player_bet = bets[current_player]
        self.highest_bet = max(self.bets.values())
        self.compute_chips()

        players_with_chips = [player for (player, chips) in self.chips.items() if chips > 0]
        if len(players_with_chips) < 2:
            self.endgame = True


    def __copy__(self):
        state = State(
            copy.copy(self.players),
            copy.copy(self.deck),
            self.current_round,
            self.current_player,
            self.starting_chips.copy(),
            self.bets.copy(),
            self.total_bets.copy(),
            self.hands,
            copy.copy(self.community),
            self.folded_players.copy(),
            self.round_last_player,
            self.round_last_better,
            self.min_allowed_bet,
            self.dealer,
            self.blinds_level,
            self.is_initial,
            self.is_final,
            self.winners
        )
        return state

    def compute_chips(self):
        self.chips = dict((player, self.starting_chips[player] - self.total_bets[player]) for player in self.players.active)

    def get_pot(self):
        return sum(self.total_bets.values())


class Game:
    """The Poker game

    Most important class for playing the game.
    It contains all the operations needed to manage changes of state during the game.
    It starts new rounds, new plays and manages the update of the players' information.
    """

    def __init__(self, players: list[Player]):
        """Create a Game

        Set things that must be remembered among different plays, such as the dealer 
        or the value of the blinds.

        Parameters
        ----------
        players : list[Player]
            Players from which to start a new game.
        """
        # things that won't change at each state
        self.players = Players(players)
        a = 5 # here I want only to compute how many plays to update the blinds level (or the seconds)

    def initial_state(self, final_state: State | None=None):
        """Create the initial state of a play

        Returns
        -------
        State
            Initial state of the play: the round is PreFlop and the blinds have
            already bet. It is now the turn of the first player after the big
            blind.
        """
        players = self.players
        deck = Deck()  # new complete deck of cards
        current_round = Round.PreFlop
        starting_chips = dict((player, 2000) for player in players.active)
        bets = dict((player, 0) for player in players.active)
        total_bets = dict((player, 0) for player in players.active)
        community = Community()
        folded_players = set()  # players who folded during the play

        # if it's not the first play we will have a final state
        if final_state is not None:
            players = copy.copy(final_state.players)
            players.remove_losers(final_state.chips)    
            dealer = players.next_to(final_state.dealer) # can give error (why?)
            starting_chips = dict((k, v) for (k, v) in final_state.chips.items() if k in players.active)
            total_bets = dict((player, 0) for player in players.active)
        else:
            dealer = players.active[random.randint(0, len(players.active) - 1)]

        # set and pay blinds
        small_blind_player = players.next_to(dealer)
        big_blind_player = players.next_to(small_blind_player)
        small_blind_bet = blinds_table[0]["small"]
        big_blind_bet = blinds_table[0]["big"]
        # set blinds' bets
        total_bets[small_blind_player] = bets[small_blind_player] = min(
            small_blind_bet, starting_chips[small_blind_player]
        )
        total_bets[big_blind_player] = bets[big_blind_player] = min(
            big_blind_bet, starting_chips[big_blind_player]
        )
        min_allowed_bet = big_blind_bet

        hands = self.__deal(deck, dealer, players)
        current_player = players.next_to(big_blind_player)

        # set ending round criteria (last player and last better)
        round_last_player = big_blind_player
        round_last_better = None  # blinds are treated as exceptions

        return State(
            players,
            deck,
            current_round,
            current_player,
            starting_chips,
            bets,
            total_bets,
            hands,
            community,
            folded_players,
            round_last_player,
            round_last_better,
            min_allowed_bet,
            dealer,
            0, # blinds level
            True
        )

    def is_initial(self, state: State):
        """Determine if the given State is the initial state of a play

        Parameters
        ----------
        state : State
            State that has to be checked

        Returns
        -------
        bool
            True if the State is the initial state of a play, False otherwise
        """
        return state.is_initial

    def is_final(self, state: State):
        return state.is_final

    def actions(self, state: State):
        """Given a State, return the available actions to the current player

        Parameters
        ----------
        state : State
            A State of the play
        
        Returns
        -------
        list
            A list of available actions, if the action is BetOrRaise, the element is not
            Action but a tuple whose first element is Action.BetOrRaise and second element
            is a renge of values that the current player can choose to bet.
        """
        current_player = state.current_player
        actions = []

        if state.current_player_bet == state.highest_bet:
            actions.append(Action.Check)
        else:
            actions.append(Action.Fold)
            actions.append(Action.Call)

        # this is the way to compute players' chips
        player_chips = state.chips[current_player]
        current_bet = state.bets[current_player]
        amount_to_call = state.highest_bet - current_bet

        if player_chips > amount_to_call:
            lowest_possible_bet = min(state.min_allowed_bet, player_chips - amount_to_call)
            highest_possible_bet = player_chips - amount_to_call
            actions.append((Action.BetOrRaise, (lowest_possible_bet, highest_possible_bet)))

        return actions

    def execute_action(self, state: State):
        player = state.current_player
        print(player.name, state.chips[player], state.bets[player])
        for card in state.hands[player].cards:
            print(card)
        for card in state.community.cards:
            print(card)
        print(self.actions(state))
        action = int(input("Insert integer of action: "))
        amount = 0
        if isinstance(self.actions(state)[action], tuple):
            print(self.actions(state)[action][1])
            amount = int(input("Insert the amount: "))
            action = self.actions(state)[action][0]
        else:
            action = self.actions(state)[action]

        return self.result(state, action, amount=amount)

    def end(self, state: State):  # needed
        """Find winners, update game and produce a final state

        Parameters
        ----------
        state : State
            The last state of the game. The last player of the play played and
            River has been dealt.

        Returns
        -------
        _type_
            _description_
        """
        pot = state.get_pot()
        winners = None
        total_bets = state.total_bets.copy()
        chips = state.chips.copy()

        players = state.players.active

        # distribute the entire pot
        while pot > 0:

            # players that could win the pot
            ending_players = [
                player
                for player in players
                if state.total_bets[player] > 0
                and not player in state.folded_players  # not sure about first check
            ]
            winners = get_winners(ending_players, state.hands, state.community)

            # bets of the players, at the end of the game, not only ending players
            bets = [
                state.total_bets[player]
                for player in players
                if state.total_bets[player] > 0
            ]
            min_bet = min(bets)

            # assign as a pot the min bet of all the players
            pot_to_assign = min_bet * len(bets)
            pot_to_assign_by_player = math.ceil(pot_to_assign / len(winners))

            for winner in winners:
                chips[winner] += pot_to_assign_by_player


            # decrease the pot by the portion assigned
            pot -= pot_to_assign

            # decrease players' bets (at the end the total_bet must be 0)
            for player in players:
                if total_bets[player] >= min_bet:
                    total_bets[player] -= min_bet

        final_state = State(
            copy.copy(state.players),
            copy.copy(state.deck),
            Round.End,
            state.current_player,
            chips,
            dict((player, 0) for player in state.players.active),
            dict((player, 0) for player in state.players.active),
            state.hands,
            copy.copy(state.community),
            state.folded_players.copy(),
            state.round_last_player,
            state.round_last_better,
            state.min_allowed_bet,
            state.dealer,
            state.blinds_level,
            False,
            True,
            winners
        )

        return final_state

    def __deal(self, deck: Deck, dealer: Player, players: Players):  # needed
        hands = {}

        deck.shuffle()

        starting_player = players.next_to(dealer)
        hands[starting_player] = deck.deal_hand()
        next_player = players.next_to(starting_player)
        while next_player != starting_player:
            hands[next_player] = deck.deal_hand()
            next_player = players.next_to(next_player)

        return hands

    def result(self, state: State, action: Action, *, amount: int = 0, range: tuple[int, int] = (0, 0)):
        """Game transition between States

        Given a State, the Action of the current player and an optional amount
        used only when the Action is Action.BetOrRaise

        Parameters
        ----------
        state : State
            The initial State of the transition.
        action : Action
            The Action to perform.
        amount : int, optional
            The amount to bet.
        range : tuple[int, int], optional
            The range of possible bet (second element of the BetOrRaise tuple in actions).

        Returns
        -------
        State
            A new State, after the transition, according to the rules of Poker.
        """
        current_player = state.current_player

        players = copy.copy(state.players)
        deck = copy.copy(state.deck)
        
        next_round = state.current_round
        starting_chips = state.starting_chips
        bets = state.bets.copy()
        total_bets = state.total_bets.copy()
        hands = state.hands
        community = copy.copy(state.community)  # maybe copy
        folded_players = state.folded_players.copy()
        round_last_player = state.round_last_player
        round_last_better = state.round_last_better
        min_allowed_bet = state.min_allowed_bet

        # perform the call everytime the action is call or bet
        if action is Action.Call or action is Action.BetOrRaise:
            # or the max the player can, for the call
            amount_to_call = min(
                state.highest_bet - bets[current_player],
                state.chips[current_player]
            )
            total_bets[current_player] += amount_to_call
            bets[current_player] += amount_to_call

        # if the action is bet, then you have to be the amount
        if action is Action.BetOrRaise:
            if not range[0] <= amount <= range[1]: 
                raise ValueError("This amount cannot be bet.")

            total_bets[current_player] += amount
            bets[current_player] += amount
            round_last_better = current_player
            min_allowed_bet = amount

        elif action is Action.Fold:
            folded_players.add(current_player)

        next_player = players.next_to(
            state.current_player
        )
        while next_player in folded_players or state.chips[next_player] == 0: # maybe
            next_player = players.next_to(next_player)
            if next_player == current_player:
                break

        # determine the passage to the next round
        one_player_remained = state.n_players - len(folded_players) == 1
        if (
            (
                state.round_last_better is None
                and state.round_last_player == current_player
                and not action is Action.BetOrRaise # and the player has not made a bet
            )
            or (next_player == state.round_last_better and not action is Action.BetOrRaise)
            or one_player_remained
            or (next_player == current_player) # maybe
        ):
            next_round += 1

            if next_round == Round.End:
                state_copy = copy.copy(state)
                state_copy.total_bets = total_bets
                state_copy.folded_players = folded_players
                state_copy.compute_chips()
                final_state = self.end(state_copy)
                return final_state

            players_with_chips = [player for player in players.active if state.chips[player] > 0 and not player in folded_players]

            if one_player_remained or len(players_with_chips) <= 1:
                while next_round < Round.End:
                    next_round += 1
                while len(community.cards) < 5:
                    deck.deal_community_cards(community)
                state_copy = copy.copy(state)
                state_copy.total_bets = total_bets
                state_copy.folded_players = folded_players
                state_copy.community = community
                state_copy.compute_chips()
                final_state = self.end(state_copy)
                return final_state 

            bets = dict((player, 0) for player in players.active)
            deck.deal_community_cards(community)
            next_player = players.next_to(state.dealer)
            while next_player in folded_players or state.chips[next_player] == 0:
                next_player = players.next_to(next_player)
                if next_player == state.dealer:
                    break
            round_last_player = players.first_active_from_backwards(state.dealer)
            while round_last_player in folded_players or state.chips[round_last_player] == 0:
                round_last_player = players.previous_than(round_last_player)
            round_last_better = None

        new_state = State(
            players,
            deck,
            next_round,
            next_player,
            starting_chips,
            bets,
            total_bets,
            hands,
            community,
            folded_players,
            round_last_player,
            round_last_better,
            min_allowed_bet,
            state.dealer,
            0
        )

        return new_state
