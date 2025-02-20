"""Test db lookup."""

import pytest

import mammos_dft

def test_Ce2Fe14B():
    Ms_0, A_0, K_0 = mammos_dft.db.get_material_parameters("Ce2Fe14B")
    assert (Ms_0, A_0, K_0) == (0.99632415793215,4.8615622027493e-12,1189274.36002828)

def test_NdFe14B():
    with pytest.raises(LookupError):
        Ms_0, A_0, K_0 = mammos_dft.db.get_material_parameters("NdFe14B")

def test_NdFe14B_A1():
    Ms_0, A_0, K_0 = mammos_dft.db.get_material_parameters("NdFe14B", structure="A1")
    assert (Ms_0, A_0, K_0) == (0.99632415793215,4.8615622027493e-12,1189274.36002828)
