"""
Test file for residue interception functionality.

Checks whether the residue layer intercepts infiltration (Infl) as expected.
"""
import os
os.environ['DEVELOPMENT'] = 'True'
import unittest
import pandas as pd

from aquacrop import (
    AquaCropModel,
    Soil,
    Crop,
    InitialWaterContent,
    FieldMngt,
)
from aquacrop.entities.residue import Residue
from aquacrop.utils import prepare_weather, get_filepath


class TestResidueInterception(unittest.TestCase):
    """
    Tests that a residue layer intercepts infiltration (Infl) and stores water.
    """

    _sim_start = "1982/05/01"
    _sim_end = "1983/10/30"

    weather_file_path = get_filepath("champion_climate.txt")
    _weather_data = prepare_weather(weather_file_path)

    _soil = Soil(soil_type="SandyLoam")
    _crop = Crop("Maize", planting_date="05/01")
    _initial_water_content = InitialWaterContent(value=["FC"])

    def _run_model(self, field_management=None):
        model = AquaCropModel(
            sim_start_time=self._sim_start,
            sim_end_time=self._sim_end,
            weather_df=self._weather_data,
            soil=self._soil,
            crop=self._crop,
            initial_water_content=self._initial_water_content,
            field_management=field_management,
        )
        model.run_model(till_termination=True)
        return model.get_water_flux()

    def test_residue_reduces_infl_on_rainy_days(self):
        """
        Infl should be lower (or equal) on rainy days when residue is present
        versus when there is no residue.
        """
        residue = Residue(type="corn", initial_mass=3000)
        field_mgmt_with_residue = FieldMngt(residue=residue)

        flux_no_residue = self._run_model(field_management=None)
        flux_with_residue = self._run_model(field_management=field_mgmt_with_residue)

        print("\n--- Water Flux columns ---")
        print(flux_no_residue.columns.tolist())

        # Identify rainy days (precipitation proxy: Infl > 0 in baseline run)
        rainy_mask = flux_no_residue["Infl"] > 0

        infl_no_residue = flux_no_residue.loc[rainy_mask, "Infl"]
        infl_with_residue = flux_with_residue.loc[rainy_mask, "Infl"]

        print("\n--- Infl comparison on rainy days (first 10 rows) ---")
        comparison = pd.DataFrame({
            "Infl_no_residue": infl_no_residue.values,
            "Infl_with_residue": infl_with_residue.values,
            "intercepted": (infl_no_residue.values - infl_with_residue.values),
        })
        print(comparison.head(10))

        total_intercepted = (infl_no_residue.values - infl_with_residue.values).sum()
        print(f"\nTotal intercepted infiltration (mm): {total_intercepted:.2f}")

        # Residue should intercept some water on at least one rainy day
        self.assertGreater(
            total_intercepted,
            0,
            msg="Residue layer should intercept some infiltration on rainy days.",
        )

        # Infl with residue should never exceed Infl without residue
        self.assertTrue(
            (infl_with_residue.values <= infl_no_residue.values).all(),
            msg="Infl with residue should not exceed Infl without residue on any rainy day.",
        )

    def test_residue_water_storage_accumulates(self):
        """
        residue_water_storage in NewCond should increase on rainy days.
        This is checked indirectly: total Infl with residue < total Infl without residue.
        """
        residue = Residue(type="winter wheat", initial_mass=4000)
        field_mgmt_with_residue = FieldMngt(residue=residue)

        flux_no_residue = self._run_model(field_management=None)
        flux_with_residue = self._run_model(field_management=field_mgmt_with_residue)

        total_infl_no_residue = flux_no_residue["Infl"].sum()
        total_infl_with_residue = flux_with_residue["Infl"].sum()

        print(f"\n--- Seasonal totals ---")
        print(f"Total Infl without residue: {total_infl_no_residue:.2f} mm")
        print(f"Total Infl with residue:    {total_infl_with_residue:.2f} mm")
        print(f"Difference (intercepted):   {total_infl_no_residue - total_infl_with_residue:.2f} mm")

        self.assertLess(
            total_infl_with_residue,
            total_infl_no_residue,
            msg="Total seasonal Infl should be lower when a residue layer is present.",
        )


if __name__ == "__main__":
    unittest.main()
