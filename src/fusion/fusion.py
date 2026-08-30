import cv2
import numpy as np


class FusionEngine:
    """
    Combines RGB and thermal-like frames.

    This is a software-level image fusion implementation
    intended for the BorderGuard AI prototype.
    """

    def __init__(
        self,
        rgb_weight: float = 0.60,
        thermal_weight: float = 0.40,
    ):
        """
        Initialize the fusion engine.

        Parameters:
            rgb_weight:
                Contribution of RGB image.

            thermal_weight:
                Contribution of thermal image.
        """

        # ----------------------------------------------------
        # Validate weights.
        # ----------------------------------------------------

        total = rgb_weight + thermal_weight

        if total <= 0:
            raise ValueError("Fusion weights must have a positive total.")

        # Normalize weights so their sum is 1.
        self.rgb_weight = rgb_weight / total
        self.thermal_weight = thermal_weight / total

    def fuse(
        self,
        rgb_frame,
        thermal_frame,
    ):
        """
        Fuse RGB and thermal frames.

        Parameters:
            rgb_frame:
                Original OpenCV BGR frame.

            thermal_frame:
                Thermal-like BGR frame.

        Returns:
            Fused BGR frame.
        """

        # ----------------------------------------------------
        # Check frame sizes.
        # ----------------------------------------------------

        if rgb_frame.shape[:2] != thermal_frame.shape[:2]:

            thermal_frame = cv2.resize(
                thermal_frame,
                (
                    rgb_frame.shape[1],
                    rgb_frame.shape[0],
                ),
            )

        # ----------------------------------------------------
        # Convert images to floating-point representation.
        # ----------------------------------------------------

        rgb_float = rgb_frame.astype(np.float32)

        thermal_float = thermal_frame.astype(np.float32)

        # ----------------------------------------------------
        # Weighted combination.
        # ----------------------------------------------------

        fused = self.rgb_weight * rgb_float + self.thermal_weight * thermal_float

        # ----------------------------------------------------
        # Convert back to valid image range.
        # ----------------------------------------------------

        fused = np.clip(
            fused,
            0,
            255,
        ).astype(np.uint8)

        return fused
