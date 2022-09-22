from pyker.entities import *


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
            four_of_a_kind.append(None)
            for card in cards:
                if card not in four_of_a_kind:
                    kicker = four_of_a_kind[-1]
                    if kicker is None or kicker.rank != card.rank:
                        kicker = card
                        four_of_a_kind[-1] = kicker
            return four_of_a_kind
                    
    return None
