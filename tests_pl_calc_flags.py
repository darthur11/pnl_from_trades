from datetime import datetime
import pytest
import pandas as pd
from .constants import BASE_COLUMNS
from .pl_calculator import PLCalculator

@pytest.fixture
def input_data_flags():
    input = [
        ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0),
        ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0),
        ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0),
        ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0),
        ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50),
        ('USD/KZT', 'USD', 'KZT', 1,  302, 450, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100),
        ('USD/PHP', 'USD', 'PHP', 1,  350, 66,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100),        
    ]
    return pd.DataFrame(input, columns=BASE_COLUMNS + ['amount_signed', 'running_balance', 'lag_running_balance', 'amount_liquiduated'])

def test_flags_calc(input_data_flags: pd.DataFrame):
    """Should correctly calculate amount liqiduated"""
    pl_calc = PLCalculator(input_data_flags)
    expected_data = pd.DataFrame(
        [
            ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,      0),
            ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,      0),
            ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,      0),
            ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0,  0),
            ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,     0),
            ('USD/KZT', 'USD', 'KZT', 1,  302, 450, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,    0),
            ('USD/PHP', 'USD', 'PHP', 1,  350, 66,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,    0),
        ], columns=BASE_COLUMNS + ['amount_signed', 'running_balance', 'lag_running_balance', 'amount_liquiduated', 'flag_liquidation']
    )

    pd.testing.assert_frame_equal(pl_calc.flags_calc(), expected_data)
    