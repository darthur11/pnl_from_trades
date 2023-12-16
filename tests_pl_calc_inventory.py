from datetime import datetime
import pytest
import pandas as pd
from .constants import BASE_COLUMNS
from .pl_calculator import PLCalculator

@pytest.fixture
def input_inventory_change():
    input = [
            ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,      0),
            ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,      0),
            ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,      0),
            ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0,  0),
            ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,     0),
            ('USD/KZT', 'USD', 'KZT', 1,  302, 500, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,    0),
            ('USD/PHP', 'USD', 'PHP', 1,  350, 60,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,    0),
            ('USD/KZT', 'USD', 'KZT', -1, 2,   550, datetime(2020, 2, 5, 0, 0), -2,   200,  202,  2,      1),
        ]
    new_columns = [
        'amount_signed', 
        'running_balance', 
        'lag_running_balance', 
        'amount_liquidated', 
        'flag_liquidation'
        ]
    return pd.DataFrame(input, columns=BASE_COLUMNS + new_columns)

def test_inventory_metrics(input_inventory_change: pd.DataFrame):
    """Should correctly calculate running inventory"""
    pl_calc = PLCalculator(input_inventory_change)
    new_columns = [
        'amount_signed', 
        'running_balance', 
        'lag_running_balance', 
        'amount_liquidated', 
        'flag_liquidation',
        'inventory_change',
        'running_inventory',
        'inventory_cost'
        ]
    expected_data = pd.DataFrame(
        [
            ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,     0, 450.0,   450.0,   450.0),
            ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,     0, 45000.0, 45450.0, 450.0),
            ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,     0, 3300.0,  3300.0,  66.0),
            ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0, 0, -90450,  -45000,  450.0),
            ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,    0, -9900,   -6600,   66.0),
            ('USD/KZT', 'USD', 'KZT', 1,  302, 500, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,   0, 146000,  101000,  500.0),
            ('USD/PHP', 'USD', 'PHP', 1,  350, 60,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,   0, 21600,   15000,   60),
            ('USD/KZT', 'USD', 'KZT', -1, 2,   550, datetime(2020, 2, 5, 0, 0), -2,   200,  202,  2,     1, -1000,   100000,   500),
        ], columns=BASE_COLUMNS + new_columns
    )
    pd.testing.assert_frame_equal(pl_calc.inventory_metrics(), expected_data)


# def test_inventory_change_calc(input_inventory_change: pd.DataFrame):
#     """Should correctly calculate inventory change"""
#     pl_calc = PLCalculator(input_inventory_change)
#     new_columns = [
#         'amount_signed', 
#         'running_balance', 
#         'lag_running_balance', 
#         'amount_liquidated', 
#         'flag_running_balance_sign_diff', 
#         'flag_liquidation',
#         'inventory_change'
#         ]
#     expected_data = pd.DataFrame(
#         [
#             ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,     1, 0, 450.0),
#             ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,     0, 0, 45000.0),
#             ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,     1, 0, 3300.0),
#             ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0, 1, 0, -45000.0),
#             ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,    1, 0, -6600),
#             ('USD/KZT', 'USD', 'KZT', 1,  302, 500, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,   1, 0, 101000),
#             ('USD/PHP', 'USD', 'PHP', 1,  350, 60,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,   1, 0, 15000),
#             ('USD/KZT', 'USD', 'KZT', -1, 2,   550, datetime(2020, 2, 5, 0, 0), -2,   200,  202,  2,     0, 1, -1100),
#         ], columns=BASE_COLUMNS + new_columns
#     )
#     pd.testing.assert_frame_equal(pl_calc.inventory_change(), expected_data)

# @pytest.fixture
# def input_running_inventory(input_inventory_change):
#     input = pd.Series([
#         450.0,
#         45000.0,
#         3300.0,
#         -45000.0,
#         -6600,
#         101000,
#         15000,
#         -1100
#     ]).rename('inventory_change')
#     return pd.concat([input_inventory_change, input], axis=1)

# def test_running_inventory_calc(input_running_inventory: pd.DataFrame):
#     """Should correctly calculate running inventory"""
#     pl_calc = PLCalculator(input_running_inventory)
#     new_columns = [
#         'amount_signed', 
#         'running_balance', 
#         'lag_running_balance', 
#         'amount_liquidated', 
#         'flag_running_balance_sign_diff', 
#         'flag_liquidation',
#         'inventory_change',
#         'running_inventory'
#         ]
#     expected_data = pd.DataFrame(
#         [
#             ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,     1, 0, 450.0,   450.0),
#             ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,     0, 0, 45000.0, 45450.0),
#             ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,     1, 0, 3300.0,  3300.0),
#             ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0, 1, 0, -45000,  -45000),
#             ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,    1, 0, -6600,   -6600),
#             ('USD/KZT', 'USD', 'KZT', 1,  302, 500, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,   1, 0, 101000,  101000),
#             ('USD/PHP', 'USD', 'PHP', 1,  350, 60,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,   1, 0, 15000,   15000),
#             ('USD/KZT', 'USD', 'KZT', -1, 2,   550, datetime(2020, 2, 5, 0, 0), -2,   200,  202,  2,     0, 1, -1100,   99900),
#         ], columns=BASE_COLUMNS + new_columns
#     )
#     pd.testing.assert_frame_equal(pl_calc.running_inventory(), expected_data)

# @pytest.fixture
# def input_inventory_cost(input_running_inventory):
#     input = pd.Series([
#         450.0,
#         45450.0,
#         3300.0,
#         -45000.0,
#         -6600,
#         101000,
#         15000,
#         99900
#     ]).rename('running_inventory')
#     return pd.concat([input_running_inventory, input], axis=1)

# def test_inventory_cost_calc(input_inventory_cost: pd.DataFrame):
#     """Should correctly calculate running inventory"""
#     pl_calc = PLCalculator(input_inventory_cost)
#     new_columns = [
#         'amount_signed', 
#         'running_balance', 
#         'lag_running_balance', 
#         'amount_liquidated', 
#         'flag_running_balance_sign_diff', 
#         'flag_liquidation',
#         'inventory_change',
#         'running_inventory',
#         'inventory_cost'
#         ]
#     expected_data = pd.DataFrame(
#         [
#             ('USD/KZT', 'USD', 'KZT', 1,  1,   450, datetime(2020, 2, 1, 0, 0), 1,    1,    None, 0,     1, 0, 450.0,   450.0,   450.0),
#             ('USD/KZT', 'USD', 'KZT', 1,  100, 450, datetime(2020, 2, 2, 0, 0), 100,  101,  1,    0,     0, 0, 45000.0, 45450.0, 450.0),
#             ('USD/PHP', 'USD', 'PHP', 1,  50,  66,  datetime(2020, 2, 2, 0, 0), 50,   50,   None, 0,     1, 0, 3300.0,  3300.0,  66.0),
#             ('USD/KZT', 'USD', 'KZT', -1, 201, 450, datetime(2020, 2, 3, 0, 0), -201, -100, 101,  101.0, 1, 0, -45000,  -45000,  450.0),
#             ('USD/PHP', 'USD', 'PHP', -1, 150, 66,  datetime(2020, 2, 3, 0, 0), -150, -100, 50,   50,    1, 0, -6600,   -6600,   66.0),
#             ('USD/KZT', 'USD', 'KZT', 1,  302, 500, datetime(2020, 2, 4, 0, 0), 302,  202,  -100, 100,   1, 0, 101000,  101000,  500.0),
#             ('USD/PHP', 'USD', 'PHP', 1,  350, 60,  datetime(2020, 2, 4, 0, 0), 350,  250,  -100, 100,   1, 0, 15000,   15000,   60),
#             ('USD/KZT', 'USD', 'KZT', -1, 2,   550, datetime(2020, 2, 5, 0, 0), -2,   200,  202,  2,     0, 1, -1100,   99900,   500),
#         ], columns=BASE_COLUMNS + new_columns
#     )
#     pd.testing.assert_frame_equal(pl_calc.inventory_cost(), expected_data)
