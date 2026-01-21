"""Test db lookup."""

import mammos_entity as me
import pytest

from mammos_dft import db


def test_Co2Fe2H4():
    """Test material `Co2Fe2H4`.

    There is only one material with formula `Co2Fe2H4`, so this
    test should load its table without issues.
    """
    properties = db.get_micromagnetic_properties(
        chemical_formula="Co2Fe2H4", print_info=False
    )
    Ms_true = me.Ms(1190240.2412648, unit="A/m")
    Ku_true = me.Ku(2810000, unit="J/m3")
    assert Ms_true == properties.Ms_0
    assert Ku_true == properties.Ku_0


def test_Fe16N2():
    """Test material `Fe16N2`.

    There is only one material with such formula in the database,
    so we test it with the values we know to be true.
    """
    properties = db.get_micromagnetic_properties(
        chemical_formula="Fe16N2", print_info=False
    )
    Ms_true = me.Ms(1671126.902464901, unit="A/m")
    Ku_true = me.Ku(1100000, unit="J/m3")
    assert Ms_true == properties.Ms_0
    assert Ku_true == properties.Ku_0


def test_CrNiP():
    """Test material `CrNiP`.

    There is no material with such formula in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        db.get_micromagnetic_properties(chemical_formula="CrNiP")


def test_Co2Fe2H4_12():
    """Test material `Co2Fe2H4` with space group number `12`.

    There is no material with such formula and space group
    in the database, so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        db.get_micromagnetic_properties(
            chemical_formula="Co2Fe2H4", space_group_number=12
        )


def test_all():
    """Test search with no filters.

    This will select all entries in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        db.get_micromagnetic_properties(print_info=False)


def test_uppasd_inputs():
    """Check existence of UppASD inputs for all materials in database."""
    for material in db.find_materials().chemical_formula:
        inputs = db.get_uppasd_properties(material)

        assert inputs.exchange.exists()
        assert inputs.posfile.exists()
        assert inputs.momfile.exists()
        assert inputs.maptype in [1, 2]
        assert inputs.posfiletype in ["C", "D"]
        assert inputs.cell.shape == (3, 3)
