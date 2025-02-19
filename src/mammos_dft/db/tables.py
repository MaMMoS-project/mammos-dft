"""Functions for reading tables."""

from pathlib import Path
import polars as pl

CSV_PATH = Path(__file__).parent / "db.csv"

def get_material_parameters(formula):
    """Get information from given chemical formula.

    This function retrieves intrinsic properties at zero temperature
    given a certain chemical formula, by looking the values
    in a database.

    :param formula: Chemical formula
    :type formula: str
    """
    df = pl.read_csv(CSV_PATH)
    df_filtered = df.filter(pl.col("formula")==formula)
    num_results = len(df_filtered)
    if num_results == 0:
        raise LookupError("Requested formula not found in database.")
    elif len(df_filtered) > 1:
        raise LookupError("Too many results found with this formula.")
    return df_filtered.select(["Ms_0", "A_0", "K_0"]).row(0)
