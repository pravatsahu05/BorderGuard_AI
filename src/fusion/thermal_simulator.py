import cv2
import numpy as np


class ThermalSimulator:
    """
    Creates a thermal-like visualization from an RGB frame.

    Important:
        This is NOT real thermal sensing.
        It is a software visualization intended for
        simulation and demonstration purposes.
    """

    def __init__(
        self,
        blur_size: int = 5,
        contrast: float = 1.5,
    ):
        """
        Initialize the thermal simulator.

        Parameters:
            blur_size:
                Size of Gaussian blur kernel.

            contrast:
                Contrast multiplier.
        """

        self.blur_size = blur_size
        self.contrast = contrast

    def generate(self, frame):
        """
        Convert an RGB/BGR frame into a thermal-like frame.

        Parameters:
            frame:
                OpenCV BGR frame.

        Returns:
            Thermal-like BGR frame.
        """

        # ----------------------------------------------------
        # Step 1: Convert BGR image to grayscale.
        # ----------------------------------------------------

        grayscale = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY,
        )

        # ----------------------------------------------------
        # Step 2: Apply slight blur.
        # ----------------------------------------------------

        if self.blur_size > 1:

            grayscale = cv2.GaussianBlur(
                grayscale,
                (
                    self.blur_size,
                    self.blur_size,
                ),
                0,
            )

        # ----------------------------------------------------
        # Step 3: Improve contrast.
        # ----------------------------------------------------

        enhanced = cv2.convertScaleAbs(
            grayscale,
            alpha=self.contrast,
            beta=0,
        )

        # ----------------------------------------------------
        # Step 4: Normalize intensity.
        # ----------------------------------------------------

        normalized = cv2.normalize(
            enhanced,
            None,
            0,
            255,
            cv2.NORM_MINMAX,
        )

        # ----------------------------------------------------
        # Step 5: Apply thermal-style colormap.
        # ----------------------------------------------------

        thermal = cv2.applyColorMap(
            normalized,
            cv2.COLORMAP_INFERNO,
        )

        return thermal
