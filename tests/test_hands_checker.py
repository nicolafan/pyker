import pytest

from tests.util import *
from pyker.hands_checker import *

C = Suit.Clubs
D = Suit.Diamonds
H = Suit.Hearts
S = Suit.Spades


@pytest.mark.parametrize(
    "hand,community,expected",
    [
        (
            build_hand((C, 1), (C, 2)),
            build_community([(C, 3), (D, 1), (C, 4), (C, 5), (C, 6)]),
            build_card((C, 6)),
        ),
        (
            build_hand((H, 1), (D, 2)),
            build_community([(S, 9), (S, 10), (S, 11), (S, 12), (S, 13)]),
            build_card((S, 13)),
        ),
        (
            build_hand((H, 10), (H, 1)),
            build_community([(S, 9), (H, 11), (H, 12), (H, 13), (D, 2)]),
            build_card((H, 1)),
        ),
    ],
)
def test_check_straight_flush(hand, community, expected):
    assert check_straight_flush(hand, community) == expected


@pytest.mark.parametrize(
    "hand,community",
    [
        (
            build_hand((C, 1), (C, 2)),
            build_community([(C, 4), (D, 1), (C, 5), (C, 6), (C, 7)]),
        ),
        (
            build_hand((H, 2), (D, 3)),
            build_community([(D, 4), (H, 10), (H, 11), (H, 12), (H, 13)]),
        )
    ],
)
def test_check_straight_flush_not_straight_flash(hand, community):
    assert check_straight_flush(hand, community) == None
