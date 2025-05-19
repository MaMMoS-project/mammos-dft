"""Functions for reading tables."""

import pathlib
import pandas as pd
from rich import print
import shutil
from textwrap import dedent
import typing

import mammos_entity as me
import mammos_units as u

DATA_DIR = pathlib.Path(__file__).parent / "data"


def check_short_label(short_label):
    """Check that short label follows the standards and returns material parameters.

    :param short_label: Short label containing chemical formula and space group
        number separated by a hyphen.
    :type short_label: str
    :raises ValueError: Wrong format.
    :return: Chemical formula and space group number.
    :rtype: (str,int)
    """
    short_label_list = short_label.split("-")
    if len(short_label_list) != 2:
        raise ValueError(
            dedent(
                """
                Wrong format for `short_label`.
                Please use the format <chemical_formula>-<space_group_number>.
                """
            )
        )
    chemical_formula = short_label_list[0]
    space_group_number = int(short_label_list[1])
    return chemical_formula, space_group_number


def get_micromagnetic_properties(
    short_label=None,
    chemical_formula=None,
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
    print_info=True,
):
    """Get micromagnetic intrinsic properties at 0K temperature from table.

    Given certain material information, this function searches
    and retrieves the following values from a local database:

    * `Ms_0`: spontaneous magnetisation at temperature 0K expressed in A/m.

    * `K_0`: magnetocrystalline anisotropy at temperature 0K expressed in J/m^3.

    :param short_label: Chemical formula and space group number separated by
        a hyphen "-".
    :type short_label: str
    :param chemical_formula: Chemical formula.
    :type chemical_formula: str
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
    :returns: 2-dimensional tuple (Ms_0, K1_0)
    :rtype: (mammos_entity.Ms, mammos_entity.Ku)
    :raise ValueError: Wrong format for `short_label`.
    """
    # TODO: implement CIF parsing
    if short_label is not None:
        chemical_formula, space_group_number = check_short_label(short_label)
    material = find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
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
    MicromagneticProperties = typing.NamedTuple(
        "MicromagneticProperties", [("Ms_0", me.Entity), ("K1_0", me.Entity)]
    )
    return MicromagneticProperties(
        me.Ms(material.SpontaneousMagnetization),
        me.Ku(material.UniaxialAnisotropyConstant),
    )


def get_micromagnetic_properties_floats(
    short_label=None,
    chemical_formula=None,
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
    print_info=True,
):
    """Get micromagnetic intrinsic properties at 0K temperature from table.

    This function retrieves intrinsic properties at zero temperature
    given certain material information, that will be searched
    into a local database.

    :param short_label: Chemical formula and space group number separated by
        a hyphen "-".
    :type short_label: str
    :param chemical_formula: Chemical formula.
    :type chemical_formula: str
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
    :returns: 2-dimensional tuple (Ms_0, K1_0) in the ontology-standard units.
    :rtype: (float, float)
    :rtype: scipy.interpolate.iterp1d
    :raise ValueError: Wrong format for `short_label`.
    """
    if short_label is not None:
        chemical_formula, space_group_number = check_short_label(short_label)
    material = find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
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
    Ms_0 = me.Ms(material.SpontaneousMagnetization)
    Ku_0 = me.Ku(material.UniaxialAnisotropyConstant)
    return Ms_0.value, Ku_0.value


def find_materials(**kwargs):
    """Find materials in database.

    This function retrieves one or known materials from the database
    `db.csv` by filtering for any requirements given in **kwargs.

    :returns: Dataframe containing materials with requested qualities.
        Possibly empty.
    :rtype: pandas.DataFrame
    """
    df = pd.read_csv(
        DATA_DIR / "db.csv",
        converters={
            "chemical_formula": str,
            "space_group_name": str,
            "space_group_number": int,
            "cell_length_a": u.Quantity,
            "cell_length_b": u.Quantity,
            "cell_length_c": u.Quantity,
            "cell_angle_alpha": u.Quantity,
            "cell_angle_beta": u.Quantity,
            "cell_angle_gamma": u.Quantity,
            "cell_volume": u.Quantity,
            "ICSD_label": str,
            "OQMD_label": str,
            "label": str,
            "SpontaneousMagnetization": u.Quantity,
            "UniaxialAnisotropyConstant": u.Quantity,
        },
    )
    for key, value in kwargs.items():
        if value is not None:
            if isinstance(value, u.Quantity):
                df = df[df[key] == value.to(df[key].unit)]
            else:
                df = df[df[key] == value]
    return df


def find_unique_material(print_info=True, **kwargs):
    """Find unique material in database.

    This function retrieves one material from the database
    `db.csv` by filtering for any requirements given in **kwargs.
    If no or more than one materials are found, an error is raised.

    :returns: Dataframe containing materials with requested qualities.
        Possibly empty.
    :rtype: pandas.DataFrame
    :raises LookupError: Requested material not found in database.
    :raises LookupError: Too many results.
    """
    df = find_materials(**kwargs)
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
    else:
        material = df.iloc[0]
        if print_info:
            print("Found material in database.")
            print(describe_material(material))
        return material


def get_cif(
    short_label=None,
    chemical_formula=None,
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
    print_info=True,
    outdir="out",
):
    """Load cif and move it to the directory `outdir`."""
    pathlib.Path(outdir).mkdir(exist_ok=True, parents=True)
    if short_label is not None:
        chemical_formula, space_group_number = check_short_label(short_label)
    material = find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
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
    shutil.copy(
        DATA_DIR / material.label / "structure.cif",
        outdir,
    )


def get_dft_output(
    short_label=None,
    chemical_formula=None,
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
    print_info=True,
    outdir="out",
):
    """Load dft output files and move them to directory `outdir`."""
    pathlib.Path(outdir).mkdir(exist_ok=True, parents=True)
    if short_label is not None:
        chemical_formula, space_group_number = check_short_label(short_label)
    material = find_unique_material(
        print_info=print_info,
        chemical_formula=chemical_formula,
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
    for file in "jfile", "momfile", "posfile":
        shutil.copy(
            DATA_DIR / material.label / file,
            outdir,
        )


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
    :raise ValueError: Material and material label cannot be both empty.
    """
    if material is None and material_label is None:
        raise ValueError("Material and material label cannot be both empty.")
    elif material_label is not None:
        df = find_materials()
        material = df[df["label"] == material_label].iloc[0]
    return dedent(
        f"""
            Chemical Formula: {material.chemical_formula}
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
