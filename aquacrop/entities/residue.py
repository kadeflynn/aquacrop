from typing import Optional
import math

# to do:
#- replicated read_field_management for residue parameters OR in param strucure just directly assing residue object like what is done with soil object. Second option makes sense since residue types are defined by name, similar to soil types 
#-add read in of residue parameters to core
#- add new conditions for residue

class Residue:
    '''
    A class to define a residue layer. A residue layer is an organic mulch layer that covers the soil surface. 

    Unlike the mulch object in field management, the residue layer is characterized by percent cover and mass. Residue decomposes and the mass and percent cover of residue are updated.

    Parameters
    ----------
    type : str
        Type of residue.
    initial_fraction_cover : float
        Initial fraction of soil surface covered with residue.
    '''

    def __init__(self, type: str, initial_fraction_cover: Optional[float] = None, initial_mass: Optional[float] = None):
        self.type = type
        self.initial_fraction_cover = initial_fraction_cover
        self.initial_mass = initial_mass
        self.area_covered_per_mass = None
        self.saturated_water_coefficient = None
        #self.mulch_area_index = None this is calculated in the residue decomposition function and updated as residue decomposes, so not defined here
        self.extinction_coefficient = None
        #self.albedo = 0.45

        self.__get_constants()
        self._calc_initial_mass()
        self._calc_initial_fraction_cover()


    def __get_constants(self):
        # residue constants of ('area_covered_per_mass', 'saturated_water_coefficient', 'extinction_coefficient') for different residue types
        residue_constants = {
            'corn': (30, 3.5, 0.86),
            'soybean': (32, 3.8, 0.50),
            'winter wheat': (45, 5.0, 0.85),
            'rye': (42, 3.8, 0.81),
            'clover': (40, 3.5, 0.80),
        }

        if self.type in residue_constants:
            self.area_covered_per_mass, self.saturated_water_coefficient, self.extinction_coefficient=residue_constants[self.type]
        else:
            raise ValueError("Invalid residue type")

    def _calc_initial_mass(self):
        '''Calculate mass of surface mulch (kg/ha) given fractional soil coverage'''
        if self.initial_fraction_cover != None:
            self.initial_mass = math.log(1 - self.initial_fraction_cover) / -(self.area_covered_per_mass * 1e-5)
        else:
            pass

    def _calc_initial_fraction_cover(self):
        '''Calcualte fractional soil coverage of residue given the mass of surface mulch (kg/ha)'''
        if self.initial_mass != None:
            self.initial_fraction_cover = 1 - math.exp(-(self.area_covered_per_mass * 1e-5) * self.initial_mass)
        else:
            pass

    # def _calc_mulch_area_index(self):
    #     self.mulch_area_index = (self.area_covered_per_mass * 1e-5 * self.mass) / self.fraction_cover
    