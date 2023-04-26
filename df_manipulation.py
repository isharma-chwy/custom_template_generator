"""Module for functions used in manipulating dataframes"""

import re
from typing import Generator, Tuple

import pandas as pd


def convert_and_match_ndc(input_df: pd.DataFrame, ndc_column_name_to_check: str, ndc_validator_column_name: str):    
    """Converts ndc column to string and matches ndc to 10 or 11 digit format. Returns a DataFrame with new columns called matched_10_or_11_digit(bool) and converted_11_digits(string)"""

    # Create a working copy of the DataFrame
    working_copy = input_df.copy()

    # convert ndc column to string
    working_copy[ndc_column_name_to_check] = working_copy[ndc_column_name_to_check].astype(str)

    # # Define regex pattern
    # pattern = r'(?:\d{4}-\d{4}-\d{2}|\d{5}-\d{3}-\d{2}|\d{5}-\d{4}-\d{1}|\d{5}-\d{4}-\d{2})'

    # # Apply regex pattern to the DataFrame column
    # working_copy['matched_10_or_11_digit'] = working_copy.loc[:,ndc_column_name_to_check].apply(lambda x: bool(re.match(pattern, x)))
    
    def convert_to_11_digits_if_10_digit_ndc(value):
        if re.match(r'\d{5}-\d{3}-\d{2}', value):
            return value[:6] + '0' + value[6:]
        elif re.match(r'\d{5}-\d{4}-\d{1}', value):
            return value[:-1] + '0' + value[-1]
        elif re.match(r'\d{4}-\d{4}-\d{2}', value):
            return '0' + value
        elif re.match(r'\d{5}-\d{4}-\d{2}', value):
            return value
        else:
            return 'Incorrect NDC format'

    # Apply conversion to 11-digit format
    working_copy[ndc_validator_column_name] = working_copy.loc[:,ndc_column_name_to_check].apply(convert_to_11_digits_if_10_digit_ndc)

    return working_copy

def split_dataframe_by_column_unique_values(input_df: pd.DataFrame,
                                            column: str,
                                            sortby: str,) -> Generator[
                                                            Tuple[str, pd.DataFrame],
                                                            None,
                                                            None]:
    """Generator that yields a tuple of (colum_value, fitered_dataframe) by 
    unique values in a specified column, sorted by the specified sortby column."""

    if column not in input_df.columns:
        raise ValueError(f"Column {column} not in dataframe")
    elif input_df.empty:
        raise ValueError("Dataframe is empty")

    unique_values = input_df[column].unique()
    for value in unique_values:
        yield (value, input_df[input_df[column] == value].sort_values(sortby).copy())
