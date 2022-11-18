from pyker.game.models import *

C = Suit.Clubs
D = Suit.Diamonds
H = Suit.Hearts
S = Suit.Spades

R2 = Rank.R2
R3 = Rank.R3
R4 = Rank.R4
R5 = Rank.R5
R6 = Rank.R6
R7 = Rank.R7
R8 = Rank.R8
R9 = Rank.R9
R10 = Rank.R10
RJ = Rank.RJ
RQ = Rank.RQ
RK = Rank.RK
RA = Rank.RA


def build_card(card: tuple[Suit, Rank]):
    return Card(card[0], card[1])


def build_cards(cards: list[tuple[Suit, Rank]]):
    return [build_card(card) for card in cards]


def build_hand(card1: tuple[Suit, Rank], card2: tuple[Suit, Rank]):
    return Hand([build_card(card1), build_card(card2)])


def build_community(cards: list[tuple[Suit, Rank]]):
    community = Community()
    cards = [build_card(card) for card in cards]
    community.cards += cards
    return community
