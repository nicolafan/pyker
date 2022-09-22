from pyker.entities import *


def check_straight_flush(hand: Hand, community: Community):
    cards = hand.cards + community.cards
    straight_flush = []

    for suit in Suit:
        same_suit_cards = [card for card in cards if card.suit == suit]
        same_suit_cards.sort()
        if len(same_suit_cards) >= 5:
            straight_flush.append(same_suit_cards[0])

            for i in range(1, len(same_suit_cards)):
                card = same_suit_cards[i]
                if card.rank == straight_flush[-1].rank + 1:
                    straight_flush.append(card)
                else:
                    straight_flush = [card]

                if (
                    i == len(same_suit_cards) - 1
                    and len(straight_flush) >= 4
                    and straight_flush[-1].rank == 13
                    and any(card.rank == 1 for card in same_suit_cards)
                ):
                    straight_flush.append(Card(suit, 1))

    if len(straight_flush) < 5:
        return None

    straight_flush.reverse()
    return straight_flush[:5]
