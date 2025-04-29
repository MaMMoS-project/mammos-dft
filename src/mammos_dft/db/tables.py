"""Functions for reading tables."""

from pathlib import Path
import pandas as pd
from rich import print
from textwrap import dedent

CSV_PATH = Path(__file__).parent / "db.csv"


def get_intrinsic_properties(
    formula=None,
    space_group_name=None,
    space_group_number=None,
    cell_length_a=None,
    cell_length_b=None,
    cell_length_c=None,
    cell_angle_alpha=None,
    cell_angle_beta=None,
    cell_angle_gamma=None,
    cell_volume=None,
    ICSD_label=None,
    OQMD_label=None,
):
    """Get intrinsic properties at 0K temperature from table.

    This function retrieves intrinsic properties at zero temperature
    given certain material information, that will be searched
    into a local database.

    :param formula: Chemical formula.
    :type formula: str
    :param space_group_name: Space group name.
    :type space_group_name: str
    :param space_group_number: Space group number.
    :type space_group_number: int
    :param cell_length_a: Cell length a.
    :type cell_length_a: float
    :param cell_length_b: Cell length b.
    :type cell_length_b: float
    :param cell_length_c: Cell length c.
    :type cell_length_c: float
    :param cell_angle_alpha: Cell angle alpha.
    :type cell_angle_alpha: float
    :param cell_angle_beta: Cell angle beta.
    :type cell_angle_beta: float
    :param cell_angle_gamma: Cell angle gamma.
    :type cell_angle_gamma: float
    :param cell_volume: Cell volume.
    :type cell_volume: float
    :param ICSD_label: Label in the NIST Inorganic Crystal Structure Database.
    :type ICSD_label: str
    :param OQMD_label: Label in the the Open Quantum Materials Database.
    :type OQMD_label: str
    :returns: 3-dimensional tuple with:

        * `Ms_0`: spontaneous magnetisation at temperature 0K expressed in Tesla.

        * `A_0`: exchange stiffness constant at temperature 0K expressed in J/m.

        * `K_0`: magnetocrystalline anisotropy at temperature 0K expressed in MJ/m^3.

    :rtype: scipy.interpolate.iterp1d
    """
    # TODO: implement CIF parsing
    df = find_materials(
        formula=formula,
        space_group_name=space_group_name,
        space_group_number=space_group_number,
        cell_length_a=cell_length_a,
        cell_length_b=cell_length_b,
        cell_length_c=cell_length_c,
        cell_angle_alpha=cell_angle_alpha,
        cell_angle_beta=cell_angle_beta,
        cell_angle_gamma=cell_angle_gamma,
        cell_volume=cell_volume,
        ICSD_label=ICSD_label,
        OQMD_label=OQMD_label,
    )
    num_results = len(df)
    if num_results == 0:
        raise LookupError("Requested material not found in database.")
    elif num_results > 1:  # list all possible choice
        error_string = (
            "Too many results. Please refine your search.\n"
            + "Avilable materials based on request:\n"
        )
        for row, material in df.iterrows():
            error_string += describe_material(material)
        raise LookupError(error_string)

    material = df.iloc[0]
    print("Found material in database.")
    print(describe_material(material))
    return material.Ms_0, material.A_0, material.K_0


def find_materials(**kwargs):
    """Find materials in database.

    This function retrieves one or known materials from the database
    `db.csv` by filtering for any requirements given in **kwargs.

    :returns: Dataframe containing materials with requested qualities.
        Possibly empty.
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(
        CSV_PATH,
        dtype={
            "formula": str,
            "space_group_name": str,
            "space_group_number": int,
            "cell_length_a": float,
            "cell_length_b": float,
            "cell_length_c": float,
            "cell_angle_alpha": float,
            "cell_angle_beta": float,
            "cell_angle_gamma": float,
            "cell_volume": float,
            "ICSD_label": str,
            "OQMD_label": str,
        },
        header=0,
        skiprows=[1],
    )
    for key, value in kwargs.items():
        if value is not None:
            df = df[df[key] == value]
    return df


def describe_material(material=None, material_label=None):
    """Describe material in a complete way.

    This function returns a string listing the properties of the given material
    or the given material label.

    :param material: Material dataframe containing structure information.
        Defaults to `None`.
    :type material: pandas.core.frame.DataFrame
    :param material_label: Label of material in local database.
        Defaults to `None`.
    :type material_label: str
    :return: Well-formatted material information.
    :rtype: str
    """
    if material_label is not None:
        df = find_materials()
        material = df[df["label"] == material_label].iloc[0]
    return dedent(
        f"""
            Chemical Formula: {material.formula}
            Space group name: {material.space_group_name}
            Space group number: {material.space_group_number}
            Cell length a: {material.cell_length_a}
            Cell length b: {material.cell_length_b}
            Cell length c: {material.cell_length_c}
            Cell angle alpha: {material.cell_angle_alpha}
            Cell angle beta: {material.cell_angle_beta}
            Cell angle gamma: {material.cell_angle_gamma}
            Cell volume: {material.cell_volume}
            ICSD_label: {material.ICSD_label}
            OQMD_label: {material.OQMD_label}
            """
    )
