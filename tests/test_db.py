"""Test db lookup."""

import numpy as np
import pytest

from mammos_dft.db import get_intrinsic_properties


def test_CrNiP():
    """Test material `CrNiP`.

    There is only one material with formula `CrNiP`, so this
    test should load its table without issues.
    """
    Ms_0, A_0, K_0 = get_intrinsic_properties(formula="CrNiP")
    assert (Ms_0, K_0) == (0.83, 0.21)
    assert np.isnan(A_0)


def test_NdFe14B():
    """Test material `NdFe14B`.

    There is no material with such formula in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_intrinsic_properties(formula="NdFe14B")


def test_CrNiP_P1():
    """Test material `CrNiP` with space group name `P1`.

    There is no material with such formula and space group
    in the database, so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_intrinsic_properties(formula="Co2Fe2H4", space_group_name="P1")


def test_all():
    """Test search with no filters.

    This will select all entries in the database,
    so we expect a `LookupError`.
    """
    with pytest.raises(LookupError):
        get_intrinsic_properties()
