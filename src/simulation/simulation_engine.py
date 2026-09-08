"""
Simulation engine for virtual border objects.
"""


class SimulationEngine:
    """
    Controls simulation time and object movement.
    """

    def __init__(
        self,
        objects,
        time_scale: float = 1.0,
    ) -> None:

        self.objects = objects

        self.simulation_time = 0.0

        self.time_scale = time_scale

    def update(
        self,
        delta_time: float,
    ) -> None:
        """
        Advance simulation time and update objects.
        """

        # --------------------------------------------------
        # Apply simulation speed.
        # --------------------------------------------------

        scaled_delta = delta_time * self.time_scale

        self.simulation_time += scaled_delta

        # --------------------------------------------------
        # Update active objects.
        # --------------------------------------------------

        for obj in self.objects:

            if obj.active:

                obj.update(scaled_delta)

    def get_objects(self):
        """
        Return currently active objects.
        """

        return [obj for obj in self.objects if obj.active]

    def reset(
        self,
        objects,
    ) -> None:
        """
        Reset the simulation.
        """

        self.objects = objects

        self.simulation_time = 0.0
