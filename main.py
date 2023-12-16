from reader import read_data
from pl_calculator import PLCalculator
from constants import BASE_COLUMNS

if __name__ == '__main__':
    df = read_data('data.csv')
    pl_calc = PLCalculator(df)
    pl_calc.calculate()
    pl_calc.calculate_totals()
    # final = pl_calc.calculate()
    # final.to_csv('output.csv', index=False)