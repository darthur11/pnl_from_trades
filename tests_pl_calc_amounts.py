from datetime import datetime

import pandas as pd
import pytest

from .constants import BASE_COLUMNS
from .pl_calculator import PLCalculator


@pytest.fixture
def input_data_amount_signed():
    input = [
        ("USD/KZT", "USD", "KZT", 1, 1, 450, datetime(2020, 2, 1, 0, 0)),
        ("USD/KZT", "USD", "KZT", 1, 100, 450, datetime(2020, 2, 2, 0, 0)),
        ("USD/PHP", "USD", "PHP", 1, 50, 66, datetime(2020, 2, 2, 0, 0)),
        ("USD/KZT", "USD", "KZT", -1, 201, 450, datetime(2020, 2, 3, 0, 0)),
        ("USD/PHP", "USD", "PHP", -1, 150, 66, datetime(2020, 2, 3, 0, 0)),
        ("USD/KZT", "USD", "KZT", 1, 302, 450, datetime(2020, 2, 4, 0, 0)),
        ("USD/PHP", "USD", "PHP", 1, 350, 66, datetime(2020, 2, 4, 0, 0)),
    ]
    return pd.DataFrame(input, columns=BASE_COLUMNS)


@pytest.fixture
def input_data_running_balance(input_data_amount_signed):
    input = pd.Series([1, 100, 50, -201, -150, 302, 350]).rename("amount_signed")
    return pd.concat([input_data_amount_signed, input], axis=1)


@pytest.fixture
def input_data_lag_running_balance(input_data_running_balance):
    input = pd.Series([1, 101, 50, -100, -100, 202, 250]).rename("running_balance")
    return pd.concat([input_data_running_balance, input], axis=1)


@pytest.fixture
def input_amount_liquidated_calc(input_data_lag_running_balance):
    input = pd.Series([None, 1, None, 101, 50, -100, -100]).rename(
        "lag_running_balance"
    )
    return pd.concat([input_data_lag_running_balance, input], axis=1)


def test_amount_signed_calc(input_data_amount_signed: pd.DataFrame):
    """Should correctly calculate signed amount"""
    pl_calc = PLCalculator(input_data_amount_signed)
    expected_data = pd.DataFrame(
        [
            ("USD/KZT", "USD", "KZT", 1, 1, 450, datetime(2020, 2, 1, 0, 0), 1),
            ("USD/KZT", "USD", "KZT", 1, 100, 450, datetime(2020, 2, 2, 0, 0), 100),
            ("USD/PHP", "USD", "PHP", 1, 50, 66, datetime(2020, 2, 2, 0, 0), 50),
            ("USD/KZT", "USD", "KZT", -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201),
            ("USD/PHP", "USD", "PHP", -1, 150, 66, datetime(2020, 2, 3, 0, 0), -150),
            ("USD/KZT", "USD", "KZT", 1, 302, 450, datetime(2020, 2, 4, 0, 0), 302),
            ("USD/PHP", "USD", "PHP", 1, 350, 66, datetime(2020, 2, 4, 0, 0), 350),
        ],
        columns=BASE_COLUMNS + ["amount_signed"],
    )
    pd.testing.assert_frame_equal(pl_calc.signed_amount(), expected_data)


def test_running_balance_calc(input_data_running_balance: pd.DataFrame):
    """Should correctly calculate running balance"""
    pl_calc = PLCalculator(input_data_running_balance)
    expected_data = pd.DataFrame(
        [
            ("USD/KZT", "USD", "KZT", 1, 1, 450, datetime(2020, 2, 1, 0, 0), 1, 1),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                100,
                450,
                datetime(2020, 2, 2, 0, 0),
                100,
                101,
            ),
            ("USD/PHP", "USD", "PHP", 1, 50, 66, datetime(2020, 2, 2, 0, 0), 50, 50),
            (
                "USD/KZT",
                "USD",
                "KZT",
                -1,
                201,
                450,
                datetime(2020, 2, 3, 0, 0),
                -201,
                -100,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                -1,
                150,
                66,
                datetime(2020, 2, 3, 0, 0),
                -150,
                -100,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                302,
                450,
                datetime(2020, 2, 4, 0, 0),
                302,
                202,
            ),
            ("USD/PHP", "USD", "PHP", 1, 350, 66, datetime(2020, 2, 4, 0, 0), 350, 250),
        ],
        columns=BASE_COLUMNS + ["amount_signed", "running_balance"],
    )
    pd.testing.assert_frame_equal(pl_calc.running_balance(), expected_data)


def test_lag_running_balance_calc(input_data_lag_running_balance: pd.DataFrame):
    """Should correctly calculate lag running balance"""
    pl_calc = PLCalculator(input_data_lag_running_balance)
    expected_data = pd.DataFrame(
        [
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                1,
                450,
                datetime(2020, 2, 1, 0, 0),
                1,
                1,
                None,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                100,
                450,
                datetime(2020, 2, 2, 0, 0),
                100,
                101,
                1,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                1,
                50,
                66,
                datetime(2020, 2, 2, 0, 0),
                50,
                50,
                None,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                -1,
                201,
                450,
                datetime(2020, 2, 3, 0, 0),
                -201,
                -100,
                101,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                -1,
                150,
                66,
                datetime(2020, 2, 3, 0, 0),
                -150,
                -100,
                50,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                302,
                450,
                datetime(2020, 2, 4, 0, 0),
                302,
                202,
                -100,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                1,
                350,
                66,
                datetime(2020, 2, 4, 0, 0),
                350,
                250,
                -100,
            ),
        ],
        columns=BASE_COLUMNS
        + ["amount_signed", "running_balance", "lag_running_balance"],
    )
    pd.testing.assert_frame_equal(pl_calc.lag_running_balance(), expected_data)


def test_amount_liquidated_calc(input_amount_liquidated_calc: pd.DataFrame):
    """Should correctly calculate amount liqiduated"""
    pl_calc = PLCalculator(input_amount_liquidated_calc)
    expected_data = pd.DataFrame(
        [
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                1,
                450,
                datetime(2020, 2, 1, 0, 0),
                1,
                1,
                None,
                0,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                100,
                450,
                datetime(2020, 2, 2, 0, 0),
                100,
                101,
                1,
                0,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                1,
                50,
                66,
                datetime(2020, 2, 2, 0, 0),
                50,
                50,
                None,
                0,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                -1,
                201,
                450,
                datetime(2020, 2, 3, 0, 0),
                -201,
                -100,
                101,
                101.0,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                -1,
                150,
                66,
                datetime(2020, 2, 3, 0, 0),
                -150,
                -100,
                50,
                50,
            ),
            (
                "USD/KZT",
                "USD",
                "KZT",
                1,
                302,
                450,
                datetime(2020, 2, 4, 0, 0),
                302,
                202,
                -100,
                100,
            ),
            (
                "USD/PHP",
                "USD",
                "PHP",
                1,
                350,
                66,
                datetime(2020, 2, 4, 0, 0),
                350,
                250,
                -100,
                100,
            ),
        ],
        columns=BASE_COLUMNS
        + [
            "amount_signed",
            "running_balance",
            "lag_running_balance",
            "amount_liquidated",
        ],
    )
    pd.testing.assert_frame_equal(pl_calc.amount_liquidated(), expected_data)
