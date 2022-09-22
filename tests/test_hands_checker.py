import pytest

from tests.util import build_card as bc, build_hand as bh, build_community as bcm
from pyker.hands_checker import *

C = Suit.Clubs
D = Suit.Diamonds
H = Suit.Hearts
S = Suit.Spades


@pytest.mark.parametrize(
    "hand,community,expected",
    [
        (
            bh((C, 1), (C, 2)),
            bcm([(C, 3), (D, 1), (C, 4), (C, 5), (C, 6)]),
            [bc((C, 6)), bc((C, 5)), bc((C, 4)), bc((C, 3)), bc((C,2))],
        ),
        (
            bh((H, 1), (D, 2)),
            bcm([(S, 9), (S, 10), (S, 11), (S, 12), (S, 13)]),
            [bc((S, 13)), bc((S, 12)), bc((S, 11)), bc((S, 10)), bc((S, 9))],
        ),
        (
            bh((H, 10), (H, 1)),
            bcm([(S, 9), (H, 11), (H, 12), (H, 13), (D, 2)]),
            [bc((H, 1)), bc((H, 13)), bc((H, 12)), bc((H, 11)), bc((H, 10))],
        ),
    ],
)
def test_check_straight_flush(hand, community, expected):
    assert check_straight_flush(hand, community) == expected


@pytest.mark.parametrize(
    "hand,community",
    [
        (
            bh((C, 1), (C, 2)),
            bcm([(C, 4), (D, 1), (C, 5), (C, 6), (C, 7)]),
        ),
        (
            bh((H, 2), (D, 3)),
            bcm([(D, 4), (H, 10), (H, 11), (H, 12), (H, 13)]),
        )
    ],
)
def test_check_straight_flush_not_straight_flash(hand, community):
    assert check_straight_flush(hand, community) == None
