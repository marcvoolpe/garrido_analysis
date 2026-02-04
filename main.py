import pandas as pd
import numpy as np
from constants import COLS, TN, PATH
from plots import payoff_histogram, comprehension_stacked_barchart, num_of_decisions_by_class


def create_df(path: str) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=",",
    )
    return df


def filter_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows which are not participants (warm-ups / trials...)
    """
    mask = df['participant._current_page_name'] == 'Results'
    df = df[mask]

    mask = df['session.config.name'] != 'Full Experiment'
    df = df[mask]
    return df


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Define useful columns
    """
    
    def mistakes_per_comprehension_row(row):
        values = row.split(',')
        clean_values = [int(x.split(':')[1].strip().strip('}')) for x in values]
        corrected_values = [x-1 for x in clean_values]
        return sum(corrected_values)

    df['defined.comprehension_mistakes'] = df[COLS['comprehension_attempts']].apply(mistakes_per_comprehension_row)
    COLS['comprehension_mistakes'] = 'defined.comprehension_mistakes'

    #4. create column for manager / employee distinction
    df['defined.is_manager'] = df[COLS['role']].str.contains('Manager', case=False)
    COLS['is_manager'] = 'defined.is_manager'

    #5. create column to check for deal existence between two humans
    df['defined.human_deal'] = df['experiment.1.player.price_accepted'].notna()
    COLS['human_deal'] = 'defined.human_deal'

    #6. create column for first mover choice
    df['defined.first_mover_choice'] = None
    df.loc[df[COLS['first_mover']] == 'Retailer Manager',
        'defined.first_mover_choice'] = df[COLS['retailer_choice']]
    df.loc[df[COLS['first_mover']] == 'Supplier Manager',
        'defined.first_mover_choice'] = df[COLS['supplier_choice']]
    COLS['first_mover_choice'] = 'defined.first_mover_choice'

    #7. create column for second mover choice
    df['defined.second_mover_choice'] = None
    df.loc[df[COLS['first_mover']] != 'Retailer Manager',
        'defined.second_mover_choice'] = df[COLS['retailer_choice']]
    df.loc[df[COLS['first_mover']] != 'Supplier Manager',
        'defined.second_mover_choice'] = df[COLS['supplier_choice']]
    COLS['second_mover_choice'] = 'defined.second_mover_choice'

    #8. create column for choice of the specific manager in that row
    df['defined.choice'] = None
    df.loc[df[COLS['role']] == 'Retailer Manager',
        'defined.choice'] = df[COLS['retailer_choice']]
    df.loc[df[COLS['role']] == 'Supplier Manager',
        'defined.choice'] = df[COLS['supplier_choice']]
    COLS['choice'] = 'defined.choice'

    #9. create column for round product class
    df['defined.product_class'] = None
    df.loc[
        (df['session.config.class_a'] == 1) &
        (df['session.config.class_b'] == 0) &
        (df['session.config.class_c'] == 0),
        'defined.product_class'
    ] = "A"
    df.loc[
        (df['session.config.class_a'] == 0) &
        (df['session.config.class_b'] == 1) &
        (df['session.config.class_c'] == 0),
        'defined.product_class'
    ] = "B"
    df.loc[
        (df['session.config.class_a'] == 0) &
        (df['session.config.class_b'] == 0) &
        (df['session.config.class_c'] == 1),
        'defined.product_class'
    ] = "C"
    COLS['product_class'] = 'defined.product_class'

    #10a. create treatment_name column with cycling numbers (1-12, each repeated 4 times)
    df.reset_index(drop=True, inplace=True)
    df['treatment_name'] = ((df.index // 4) % 12) + 1
    df['treatment_name'] = df['treatment_name'].astype(str) + '_' + df[COLS['product_class']] + '_'
    df['treatment_name'] = df['treatment_name'] + df[COLS['first_mover']].str[:-8] + '_First_'
    df['treatment_name'] = df['treatment_name'] + df['session.config.baseline'].apply(lambda x: 'Human' if x == 1 else 'AI')

    #10b. create correct_treatment_name column
    df['Correct_treatment_name'] = df.index.map(lambda i: TN[(i // 4) % 12])
    
    return df


def validate(df: pd.DataFrame):
    """
    Validate the DataFrame for data integrity
    """

    #1. ensure there is no ambiguity on the first-mover config
    ambiguous_mask = df['session.config.force_retailer_first'] == df['session.config.force_supplier_first']
    if ambiguous_mask.any():
        ambiguous_rows = df[ambiguous_mask][['session.config.force_retailer_first', 'session.config.force_supplier_first']].to_string()
        raise Exception(
            f"Random Assignment detected: {ambiguous_mask.sum()} rows have force_retailer_first == force_supplier_first\n"
            f"Ambiguous rows:\n{ambiguous_rows}"
        )

    #2. ensure treatment_name and correct_treatment_name DO NOT differ
    mismatches = df['treatment_name'] != df['Correct_treatment_name']
    num_mismatches = mismatches.sum()

    if num_mismatches > 0:
        mismatched_rows = df[mismatches][
            ['treatment_name', 'Correct_treatment_name']
        ].to_string(index=False)

        raise Exception(
            f"{num_mismatches} rows differ between treatment_name and Correct_treatment_name\n"
            f"Mismatched rows:\n{mismatched_rows}"
        )


def main():
    """
    Main pipeline
    """
    
    #1: Load data
    print("Loading data...")
    df = create_df(PATH)
    print(f"Loaded {len(df)} rows")
    
    #2: Filter data
    print("Filtering data...")
    df = filter_df(df)
    print(f"After filtering: {len(df)} rows")
    
    #3: Add derived columns
    print("Adding derived columns...")
    df = add_derived_columns(df)
    
    #4: Validate the processed data - will raise exceptions if problems found
    print("Validating processed data...")
    validate(df)
    print("Data validation passed!")
    
    #5: Completed Pipeline
    print("\nPipeline completed successfully!")
    print(f"Final DataFrame shape: {df.shape}")

    #6: Plots graphs
    payoff_histogram(df)
    comprehension_stacked_barchart(df)
    num_of_decisions_by_class(df)
   
    return df


if __name__ == "__main__":
    df = main()
