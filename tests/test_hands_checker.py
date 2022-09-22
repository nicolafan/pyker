import pytest

from tests.util import *
from tests.util import build_card as bc, build_cards as bcs, build_hand as bh, build_community as bcm
from pyker.hands_checker import *


@pytest.mark.parametrize(
    "hand,community,expected",
    [
        (
            bh((C, RA), (C, R2)),
            bcm([(C, R3), (D, RA), (C, R4), (C, R5), (C, R6)]),
            bcs([(C, R6), (C, R5), (C, R4), (C, R3), (C, R2)]),
        ),
        (
            bh((H, RA), (D, R2)),
            bcm([(S, R9), (S, R10), (S, RJ), (S, RQ), (S, RK)]),
            bcs([(S, RK), (S, RQ), (S, RJ), (S, R10), (S, R9)]),
        ),
        (
            bh((H, R10), (H, RA)),
            bcm([(S, R9), (H, RJ), (H, RQ), (H, RK), (D, R2)]),
            bcs([(H, RA), (H, RK), (H, RQ), (H, RJ), (H, R10)]),
        ),
        (
            bh((H, RA), (H, R5)),
            bcm([(H, R2), (H, R3), (H, R4), (H, R7), (H, R9)]),
            bcs([(H, R5), (H, R4), (H, R3), (H, R2), (H, RA)])
        )
    ],
)
def test_check_straight_flush(hand, community, expected):
    assert check_straight_flush(hand, community) == expected


@pytest.mark.parametrize(
    "hand,community",
    [
        (
            bh((C, RA), (C, R2)),
            bcm([(C, R4), (D, RA), (C, R5), (C, R6), (C, R7)]),
        ),
        (
            bh((H, R2), (D, R3)),
            bcm([(D, R4), (H, R10), (H, RJ), (H, RQ), (H, RK)]),
        )
    ],
)
def test_check_straight_flush_not(hand, community):
    assert check_straight_flush(hand, community) == None


@pytest.mark.parametrize(
    "hand,community,expected",
    [
        (
            bh((H, RA), (S, RA)),
            bcm([(C, RA), (H, RK), (H, RQ), (D, R2), (D, RA)]),
            bcs([(C, RA), (D, RA), (H, RA), (S, RA), (H, RK)])
        ),
        (
            bh((C, RA), (S, RA)),
            bcm([(C, RK), (H, RK), (D, RQ), (S, RK), (D, RK)]),
            bcs([(C, RK), (D, RK), (H, RK), (S, RK), (C, RA)])
        )
    ]
)
def test_check_four_of_a_kind(hand, community, expected):
    assert check_four_of_a_kind(hand, community) == expected


@pytest.mark.parametrize(
    "hand,community",
    [
        (
            bh((H, RA), (S, RA)),
            bcm([(C, RA), (H, RK), (C, RK), (S, RQ), (S, RK)])
        )
    ]
)
def test_check_four_of_a_kind_not(hand, community):
    assert check_four_of_a_kind(hand, community) == None


@pytest.mark.parametrize(
    "hand,community,expected",
    [
        (
            bh((H, RA), (S, RA)),
            bcm([(S, R2), (C, RA), (C, R2), (C, RK), (S, RK)]),
            bcs([(C, RA), (H, RA), (S, RA), (C, RK), (S, RK)])
        ),
        (
            bh((H, RQ), (H, RJ)),
            bcm([(S, RQ), (S, RJ), (C, RJ), (H, RK), (C, RQ)]),
            bcs([(C, RQ), (H, RQ), (S, RQ), (C, RJ), (H, RJ)])
        ),
        (
            bh((H, RA), (S, RA)),
            bcm([(C, RA), (H, RK), (H, RQ), (D, RQ), (D, RA)]),
            bcs([(C, RA), (D, RA), (H, RA), (D, RQ), (H, RQ)])
        )
    ]
)
def test_check_full_house(hand, community, expected):
    assert check_full_house(hand, community) == expected


@pytest.mark.parametrize(
    "hand,community",
    [
        (
            bh((H, RA), (S, RA)),
            bcm([(C, RJ), (H, RJ), (C, RK), (S, RK), (S, R10)])
        )
    ]
)
def test_check_full_house_not(hand, community):
    assert check_full_house(hand, community) == None