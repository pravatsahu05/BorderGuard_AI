import time


class SimulationEngine:
    """
    Controls the virtual border environment.
    """

    def __init__(
        self,
        objects,
    ):

        self.objects = objects

        self.simulation_time = 0.0

    def update(
        self,
        delta_time: float,
    ):
        """
        Advance the simulation.
        """

        self.simulation_time += delta_time

        for obj in self.objects:

            if obj.active:

                obj.update(delta_time)

    def get_objects(self):

        return [obj for obj in self.objects if obj.active]

    def reset(
        self,
        objects,
    ):

        self.objects = objects

        self.simulation_time = 0.0
