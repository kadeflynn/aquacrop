
from typing import Tuple

def residue_rainfall_interception(Infl: float, residue_fraction_cover: float, residue_water_content: float, residue_saturated_water_capacity: float) -> Tuple[float, float]:
    '''
    Calculate the amount of rainfall intercepted by the residue layer and the new infiltration after interception.

    Citation is Scopel et al. (2004)

    Parameters
    ----------
    Infl : float
        Infiltration (mm) before interception.
    residue_fraction_cover : float
        Fractional soil coverage of residue.
    residue_water_content : float
        Current water content of the residue layer (mm).
    residue_saturated_water_capacity : float
        Saturated water capacity of the residue layer (mm).

    Returns
    -------
    Tuple[float, float]
        A tuple containing the new infiltration after interception (mm) and the new residue water content after interception (mm).
    '''
    if residue_fraction_cover <= 0 or residue_saturated_water_capacity <= 0:
        return Infl, 0
    
    # Determine residue storage capacity
    residue_storage_capacity = max(0, residue_saturated_water_capacity - residue_water_content)

    # Calculate potential interception based on fractional cover and saturated water capacity
    potential_interception = min(Infl * residue_fraction_cover, residue_storage_capacity)

    # Actual interception is the minimum of potential interception and available infiltration
    actual_interception = min(potential_interception, Infl)

    # New infiltration after interception
    new_infiltration = Infl - actual_interception

    # New residue water content after interception
    new_residue_water_content = residue_water_content + actual_interception

    return new_infiltration, new_residue_water_content