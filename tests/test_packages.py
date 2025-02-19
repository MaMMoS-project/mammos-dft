"""Packages tests."""

def test_polars():
    """Check polars dependency."""
    import polars as pl
    assert pl.__version__ == "1.22.0"
