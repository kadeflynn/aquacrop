import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aquacrop.entities.residue import Residue


def simulate_residue_decomposition(
    NewCond_mass: float,
    NewCond_decomp_days: float,
    NewCond_saturated_water_capacity: float,
    NewCond_fraction_cover: float,
    NewCond_residue_water_storage: float,
    temperature_mean_c: float,
    residue: "Residue",
) -> tuple[float, float, float, float, float]:
    """
    Simulate daily residue decomposition.

    The decomposition approach is based on Steiner et al. (1999):
    Crop Residue Decomposition in No-Tillage Small-Grain Fields.

    Parameters:
    -----------
    NewCond_mass : float
        Residue mass state at start of day.

    NewCond_decomp_days : float
        Cumulative decomposition-day state at start of day.

    NewCond_saturated_water_capacity : float
        Residue saturated water capacity state at start of day.

    NewCond_fraction_cover : float
        Residue fraction cover state at start of day.

    NewCond_residue_water_storage : float
        Residue water storage state at start of day.

    temperature_mean_c : float
        Daily mean air temperature (degC).

    residue : Residue
        Residue parameter object.

    Returns:
    --------
    tuple[float, float, float, float, float]
        Updated states in this order:
        (NewCond_mass,
         NewCond_decomp_days,
         NewCond_saturated_water_capacity,
         NewCond_residue_area_index,
         NewCond_fraction_cover)
    """
    # Read parameters and starting states
    residue_mass_initial = residue.mass * 1000 * (1 / 10000)  # convert to g/m2
    residue_saturated_water_coefficient = residue.saturated_water_coefficient
    residue_water_content = NewCond_residue_water_storage

    # Define k (crop decomposition coefficient g/gDD).
    # Chose a conservative value from Thapa et al. (2022)
    k = 0.025

    residue_water_factor = _calculate_residue_water_factor(
        NewCond_saturated_water_capacity,
        residue_water_content,
    )

    residue_temperature_factor = _calculate_residue_temperature_factor(temperature_mean_c)

    decomposition_today = min(residue_water_factor, residue_temperature_factor)

    NewCond_decomp_days += decomposition_today

    NewCond_mass = residue_mass_initial * math.exp(-k * NewCond_decomp_days) * 10

    NewCond_saturated_water_capacity = _calculate_saturated_water_capacity(
        residue_saturated_water_coefficient,
        NewCond_mass,
    )

    NewCond_residue_area_index = _calculate_residue_area_index(
        NewCond_mass,
        residue.area_covered_per_mass,
        NewCond_fraction_cover,
    )

    NewCond_fraction_cover = 1 - math.exp(-NewCond_residue_area_index)

    return (
        NewCond_mass,
        NewCond_decomp_days,
        NewCond_saturated_water_capacity,
        NewCond_residue_area_index,
        NewCond_fraction_cover,
    )

def _calculate_residue_area_index(mass: float, area_covered_per_mass: float, fraction_cover: float) -> float:
    if fraction_cover <= 0:
        return 0.0

    residue_area_index = (area_covered_per_mass * 1e-5 * mass) / fraction_cover

    return residue_area_index

def _calculate_saturated_water_capacity(residue_saturated_water_coefficient: float,
                                       mass: float) -> float:
    saturated_water_capacity = residue_saturated_water_coefficient * 1e-4 * mass if mass > 0 else 0

    return saturated_water_capacity

def _calculate_residue_temperature_factor(temperature: float) -> float:
    a = 0
    temperature_factor = (2 * (temperature + a) ** 2 * (32 + a) ** 2 - (temperature + a) ** 4) / ((32 + a) ** 4)

    temperature_factor = 0 if temperature_factor < 0 else temperature_factor

    return temperature_factor

def _calculate_residue_water_factor(saturated_water_capacity: float,
                                   water_content: float) -> float:
    if saturated_water_capacity <= 0:
        return 0.1

    water_factor = water_content / saturated_water_capacity

    water_factor = 0.1 if water_factor < 0.1 else water_factor
    water_factor = 1 if water_factor > 1 else water_factor

    return water_factor