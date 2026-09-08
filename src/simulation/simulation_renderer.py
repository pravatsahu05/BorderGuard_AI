"""
Renderer for the BorderGuard AI software simulation.
"""

import time

import cv2
import numpy as np

from src.zones.zone_manager import ZoneManager
from src.zones.border_config import ZONES


class SimulationRenderer:
    """
    Draws the simulated border environment.
    """

    def __init__(
        self,
        width: int = 960,
        height: int = 540,
    ) -> None:

        self.width = width

        self.height = height

        self.zone_manager = ZoneManager(ZONES)

    # ======================================================
    # BACKGROUND
    # ======================================================

    def create_frame(self):
        """
        Create a simple virtual border background.
        """

        frame = np.zeros(
            (
                self.height,
                self.width,
                3,
            ),
            dtype=np.uint8,
        )

        # --------------------------------------------------
        # Base background
        # --------------------------------------------------

        frame[:] = (
            35,
            35,
            35,
        )

        # --------------------------------------------------
        # Add horizontal grid lines.
        # --------------------------------------------------

        for y in range(
            0,
            self.height,
            40,
        ):

            cv2.line(
                frame,
                (0, y),
                (self.width, y),
                (65, 65, 65),
                1,
            )

        # --------------------------------------------------
        # Add vertical grid lines.
        # --------------------------------------------------

        for x in range(
            0,
            self.width,
            40,
        ):

            cv2.line(
                frame,
                (x, 0),
                (x, self.height),
                (65, 65, 65),
                1,
            )

        return frame

    # ======================================================
    # HEADER
    # ======================================================

    def draw_header(
        self,
        frame,
        scenario_name: str,
        simulation_time: float,
    ) -> None:

        cv2.putText(
            frame,
            "BORDERGUARD AI",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            "SOFTWARE BORDER SIMULATION",
            (20, 62),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 220, 220),
            1,
        )

        cv2.putText(
            frame,
            f"Scenario: {scenario_name}",
            (620, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (255, 255, 255),
            1,
        )

        cv2.putText(
            frame,
            f"Time: {simulation_time:.1f}s",
            (760, 62),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (220, 220, 220),
            1,
        )

    # ======================================================
    # OBJECT DRAWING
    # ======================================================

    def draw_objects(
        self,
        frame,
        objects,
        zone_states,
    ) -> None:

        for obj in objects:

            x = int(obj.x)

            y = int(obj.y)

            # ------------------------------------------------
            # Don't draw objects completely outside screen.
            # ------------------------------------------------

            if x < -50 or x > self.width + 50 or y < -50 or y > self.height + 50:
                continue

            # ------------------------------------------------
            # Draw object.
            # ------------------------------------------------

            if obj.object_type == "vehicle":

                cv2.rectangle(
                    frame,
                    (
                        x - 18,
                        y - 10,
                    ),
                    (
                        x + 18,
                        y + 10,
                    ),
                    (255, 255, 255),
                    -1,
                )

                cv2.rectangle(
                    frame,
                    (
                        x - 18,
                        y - 10,
                    ),
                    (
                        x + 18,
                        y + 10,
                    ),
                    (0, 0, 0),
                    2,
                )

            else:

                cv2.circle(
                    frame,
                    (x, y),
                    14,
                    (255, 255, 255),
                    -1,
                )

                cv2.circle(
                    frame,
                    (x, y),
                    14,
                    (0, 0, 0),
                    2,
                )

            # ------------------------------------------------
            # Track label.
            # ------------------------------------------------

            cv2.putText(
                frame,
                (f"{obj.object_type} " f"#{obj.track_id}"),
                (
                    x + 20,
                    y - 10,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            # ------------------------------------------------
            # Zone information.
            # ------------------------------------------------

            state = zone_states.get(obj.track_id)

            if state is None:
                continue

            current_zone = state.current_zone

            try:

                dwell_time = zone_states.get_dwell_time(
                    obj.track_id,
                    time.time(),
                )

            except Exception:

                dwell_time = 0.0

            cv2.putText(
                frame,
                f"Zone: {current_zone}",
                (
                    x + 20,
                    y + 10,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

            cv2.putText(
                frame,
                f"Dwell: {dwell_time:.1f}s",
                (
                    x + 20,
                    y + 30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (220, 220, 220),
                1,
            )

    # ======================================================
    # FOOTER
    # ======================================================

    def draw_footer(
        self,
        frame,
    ) -> None:

        cv2.putText(
            frame,
            "Press Q to quit",
            (
                20,
                self.height - 20,
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

    # ======================================================
    # RENDER
    # ======================================================

    def render(
        self,
        objects,
        zone_states,
        scenario_name: str,
        simulation_time: float = 0.0,
    ):

        frame = self.create_frame()

        # --------------------------------------------------
        # Draw configured zones.
        # --------------------------------------------------

        self.zone_manager.draw_zones(frame)

        # --------------------------------------------------
        # Draw UI.
        # --------------------------------------------------

        self.draw_header(
            frame,
            scenario_name,
            simulation_time,
        )

        self.draw_objects(
            frame,
            objects,
            zone_states,
        )

        self.draw_footer(frame)

        return frame
