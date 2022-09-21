from entities import *

def check_straight_flush(Hand, Community):
    cards = Hand.cards + Community.cards
    high_card = None

    for suit in Suit:
        same_suit_cards = [card for card in cards if card.suit == suit]
        same_suit_cards.sort()
        if len(same_suit_cards) >= 5:
            previous_rank = same_suit_cards[0].rank
            cnt = 1

            for i in range(1, len(same_suit_cards)):
                card = same_suit_cards[i]
                if card.rank == previous_rank + 1:
                    previous_rank += 1 
                    cnt += 1
                else:
                    previous_rank = card.rank
                    cnt = 1
                
                if cnt >= 5:
                    high_card = card

                if i == len(same_suit_cards) - 1 and cnt >= 4 and previous_rank == 13 and any(card.rank == 1 for card in same_suit_cards):
                    high_card = Card(suit, 1) 
        
    return high_card