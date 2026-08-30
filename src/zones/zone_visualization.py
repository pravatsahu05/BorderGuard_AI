import sys
from pathlib import Path

import cv2
import numpy as np

# Ensure src/zones is in sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from zone_manager import ZoneManager
    from border_config import ZONES
except ImportError:
    from src.zones.zone_manager import ZoneManager
    from src.zones.border_config import ZONES



WIDTH = 960
HEIGHT = 540


def main():

    # Create simulated border scene.
    frame = np.zeros(
        (HEIGHT, WIDTH, 3),
        dtype=np.uint8,
    )

    # --------------------------------------------------------
    # Create zone manager.
    # --------------------------------------------------------

    manager = ZoneManager(ZONES)

    # --------------------------------------------------------
    # Draw zones.
    # --------------------------------------------------------

    manager.draw_zones(frame)

    # --------------------------------------------------------
    # Draw example border line.
    # --------------------------------------------------------

    cv2.line(
        frame,
        (0, 350),
        (WIDTH, 350),
        (255, 255, 255),
        3,
    )

    cv2.putText(
        frame,
        "SIMULATED INTERNATIONAL BORDER",
        (260, 525),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    cv2.imshow(
        "BorderGuard AI - Zone Map",
        frame,
    )

    print("Press any key to close.")

    cv2.waitKey(0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
