from pyker.entities import *

def build_card(card: tuple[Suit, int]):
    return Card(card[0], card[1])

def build_hand(card1: tuple[Suit, int], card2: tuple[Suit, int]):
    return Hand([build_card(card1), build_card(card2)])

def build_community(cards: list[tuple[Suit, int]]):
    community = Community()
    cards = [build_card(card) for card in cards]
    community.cards += cards
    return community