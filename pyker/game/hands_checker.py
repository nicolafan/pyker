from turtle import pos
from pyker.game.models import *
import enum


class HandRank(enum.IntEnum):
    StraightFlush = 9
    FourOfAKind = 8
    FullHouse = 7
    Flush = 6
    Straight = 5
    ThreeOfAKind = 4
    TwoPair = 3
    OnePair = 2
    HighCard = 1


class HandComparison(enum.IntEnum):
    Lose = -1
    Draw = 0
    Win = 1


def __get_n_higher_cards(cards: list[Card], n: int):
    cards.sort()

    for rank in Rank:
        start = -1
        end = -1
        for i in range(len(cards)):
            if cards[i].rank == rank:
                if start == -1:
                    start = i
                end = i
        if end > start:
            cards[start : end + 1] = list(reversed(cards[start : end + 1]))

    cards.reverse()
    return cards[:n]


def check_straight_flush(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    straight_flush = []

    for suit in Suit:
        same_suit_cards = [card for card in cards if card.suit == suit]
        same_suit_cards.sort()

        if len(same_suit_cards) >= 5:
            poss_straight_flush = []
            poss_straight_flush.append(same_suit_cards[0])

            for i in range(1, len(same_suit_cards)):
                card = same_suit_cards[i]
                if card.rank == poss_straight_flush[-1].rank + 1:
                    poss_straight_flush.append(card)
                else:
                    if len(poss_straight_flush) > len(straight_flush):
                        straight_flush = poss_straight_flush
                    poss_straight_flush = [card]

            if len(poss_straight_flush) >= 5:
                straight_flush = poss_straight_flush

        if len(straight_flush) >= 5:
            break

    # special case: A-2-3-4-5 because A is considered to be after K
    if len(straight_flush) == 4:
        highest_card = straight_flush[-1]
        if highest_card.rank == Rank.R5 and Card(highest_card.suit, Rank.RA) in cards:
            straight_flush = [Card(highest_card.suit, Rank.RA)] + straight_flush
            straight_flush.reverse()
            return straight_flush

    if len(straight_flush) < 5:
        return None

    straight_flush.reverse()
    return straight_flush[:5]


def check_four_of_a_kind(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()

    for rank in Rank:
        four_of_a_kind = [card for card in cards if card.rank == rank]
        if len(four_of_a_kind) == 4:
            # find the kicker
            four_of_a_kind.sort()
            remaining_cards = [card for card in cards if not card in four_of_a_kind]
            kicker = __get_n_higher_cards(remaining_cards, 1)
            four_of_a_kind += kicker
            return four_of_a_kind

    return None


def check_full_house(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()
    full_house = None

    for tris_rank in Rank:
        tris = [card for card in cards if card.rank == tris_rank]
        if len(tris) >= 3:
            for pair_rank in Rank:
                if pair_rank == tris_rank:
                    continue
                pair = [card for card in cards if card.rank == pair_rank]
                if len(pair) >= 2:
                    full_house = tris[:3] + pair[:2]

    return full_house


def check_flush(hand: Hand, community: Community):
    cards = hand.cards + community.cards

    for suit in Suit:
        flush = [card for card in cards if card.suit == suit]
        if len(flush) >= 5:
            flush.sort()
            flush.reverse()
            return flush[:5]

    return None


def check_straight(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()
    straight = []

    poss_straight = [cards[0]]

    for card in cards[1:]:
        if card.rank == poss_straight[-1].rank + 1:
            poss_straight.append(card)
        elif card.rank == poss_straight[-1].rank:
            continue
        else:
            if len(poss_straight) > len(straight):
                straight = poss_straight
            poss_straight = [card]

        if len(poss_straight) >= 5:
            straight = poss_straight

    # special case: A-2-3-4-5 because A is considered to be after K
    if len(straight) == 4:
        highest_card = straight[-1]
        for suit in Suit:
            if highest_card.rank == Rank.R5 and Card(suit, Rank.RA) in cards:
                straight = [Card(suit, Rank.RA)] + straight
                straight.reverse()
                return straight

    if len(straight) < 5:
        return None

    straight.reverse()
    return straight[:5]


def check_three_of_a_kind(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()
    tris = None

    for rank in Rank:
        poss_tris = [card for card in cards if card.rank == rank]
        if len(poss_tris) >= 3:
            poss_tris = poss_tris[:3]
            remaining_cards = [card for card in cards if card not in poss_tris]
            kickers = __get_n_higher_cards(remaining_cards, 2)
            tris = poss_tris + kickers

    return tris


def check_two_pair(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()
    two_pair = None

    for rank1 in Rank:
        pair1 = [card for card in cards if card.rank == rank1]
        if len(pair1) >= 2:
            for rank2 in Rank:
                if rank2 >= rank1:
                    break
                pair2 = [card for card in cards if card.rank == rank2]
                if len(pair2) >= 2:
                    two_pair = pair1[:2] + pair2[:2]

    if two_pair is None:
        return None

    remaining_cards = [card for card in cards if not card in two_pair]
    kicker = __get_n_higher_cards(remaining_cards, 1)
    two_pair += kicker

    return two_pair


def check_one_pair(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    cards.sort()
    one_pair = None

    for rank in Rank:
        poss_pair = [card for card in cards if card.rank == rank]
        if len(poss_pair) >= 2:
            one_pair = poss_pair[:2]

    if one_pair is None:
        return None

    remaining_cards = [card for card in cards if not card in one_pair]
    kickers = __get_n_higher_cards(remaining_cards, 3)
    one_pair = one_pair + kickers

    return one_pair


def check_high_card(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    return __get_n_higher_cards(cards, 5)


hands_checkers_dict = {
    HandRank.StraightFlush: check_straight_flush,
    HandRank.FourOfAKind: check_four_of_a_kind,
    HandRank.FullHouse: check_full_house,
    HandRank.Flush: check_flush,
    HandRank.Straight: check_straight,
    HandRank.ThreeOfAKind: check_three_of_a_kind,
    HandRank.TwoPair: check_two_pair,
    HandRank.OnePair: check_one_pair,
    HandRank.HighCard: check_high_card,
}


class HandInfo:
    def __init__(self, player: Player, hand: list[Card], hand_rank: HandRank):
        self.player = player
        self.hand = hand
        self.hand_rank = hand_rank

        self.high_cards = self._get_high_cards()
        self.kickers = self._get_kickers()

    def _get_high_cards(self):
        high_cards = self.hand[:1]

        if self.hand_rank == HandRank.FullHouse:
            high_cards.append(self.hand[3])
        elif self.hand_rank == HandRank.TwoPair:
            high_cards.append(self.hand[2])

        return high_cards

    def _get_kickers(self):
        kickers = []

        if self.hand_rank == HandRank.FourOfAKind or self.hand_rank == HandRank.TwoPair:
            kickers.append(self.hand[-1])
        elif self.hand_rank == HandRank.ThreeOfAKind:
            kickers += self.hand[-2:]
        elif self.hand_rank == HandRank.OnePair:
            kickers += self.hand[-3:]
        elif self.hand_rank == HandRank.HighCard:
            kickers += self.hand[-4:]

        return kickers

    def compare_to(self, other):
        if self.hand_rank > other.hand_rank:
            return HandComparison.Win
        if self.hand_rank < other.hand_rank:
            return HandComparison.Lose

        for card1, card2 in zip(self.high_cards, other.high_cards):
            comparison = card1.compare_to_by_rank(card2)
            if comparison < 0:
                return HandComparison.Win
            elif comparison > 0:
                return HandComparison.Lose

        if self.hand_rank == HandRank.Flush:
            for card1, card2 in zip(self.high_cards, other.high_cards):
                comparison = card1.compare_to_by_rank(card2)
                if comparison < 0:
                    return HandComparison.Win
                elif comparison > 0:
                    return HandComparison.Lose

        for card1, card2 in zip(self.kickers, other.kickers):
            comparison = card1.compare_to_by_rank(card2)
            if comparison < 0:
                return HandComparison.Win
            elif comparison > 0:
                return HandComparison.Lose

        return HandComparison.Draw


def get_winners(players: list[Player], hands: dict[Player, Hand], community: Community):
    if len(players) == 1:
        return players

    hands_info = []

    for player in players:
        hand_info = {}

        for hand_rank in HandRank:
            poss_hand = hands_checkers_dict[hand_rank](hands[player], community)
            if poss_hand is not None:
                hand_info = HandInfo(player, poss_hand, hand_rank)
                hands_info.append(hand_info)
                break

    winners = [hand_info.player for hand_info in hands_info]

    for i in range(len(hands_info)):
        for j in range(i + 1, len(hands_info)):
            hand_info1 = hands_info[i]
            hand_info2 = hands_info[j]

            comparison = hand_info1.compare_to(hand_info2)

            if comparison == HandComparison.Win:
                if hand_info2.player in winners:
                    winners.remove(hand_info2.player)
            elif comparison == HandComparison.Lose:
                if hand_info1.player in winners:
                    winners.remove(hand_info1.player)

    return winners
