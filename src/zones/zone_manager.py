from typing import Optional

import cv2
import numpy as np

from zone import Zone


class ZoneManager:
    """
    Manages surveillance zones and determines
    which zone contains a tracked object.
    """

    def __init__(
        self,
        zones: list[Zone],
    ):

        self.zones = zones

    def get_zone(
        self,
        point: tuple[float, float],
    ) -> Optional[Zone]:
        """
        Determine which zone contains a point.

        Parameters:
            point:
                (x, y) coordinate.

        Returns:
            Matching Zone or None.
        """

        x, y = point

        for zone in self.zones:

            polygon = np.array(
                zone.polygon,
                dtype=np.int32,
            )

            result = cv2.pointPolygonTest(
                polygon,
                (float(x), float(y)),
                False,
            )

            if result >= 0:
                return zone

        return None

    def draw_zones(
        self,
        frame,
    ):
        """
        Draw all configured zones on a frame.
        """

        for zone in self.zones:

            polygon = np.array(
                zone.polygon,
                dtype=np.int32,
            )

            cv2.polylines(
                frame,
                [polygon],
                isClosed=True,
                color=(255, 255, 255),
                thickness=2,
            )

            # Use the first polygon point for label placement.
            label_x, label_y = zone.polygon[0]

            cv2.putText(
                frame,
                zone.name,
                (
                    label_x + 10,
                    label_y + 30,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )

        return frame
