import pandas as pd

def read_data(filename: str, delimiter = ';', thousands= ' ', decimal = ',') -> pd.DataFrame:
    """This function reads data from a csv file and returns a pandas DataFrame

    Args:
        filename (str): Path to the csv file
        delimiter (str, optional): Delimiter of CSV. Defaults to ';'.
        thousands (str, optional): Delimiter of thousands for numbers. Defaults to ' '.
        decimal (str, optional): Delimiter of decimal places. Defaults to ','.

    Returns:
        pd.DataFrame: Pandas DataFrame
    """
    return pd.read_csv(filename, delimiter=delimiter, thousands= thousands, decimal=decimal)
