import cv2

from thermal_simulator import ThermalSimulator
from fusion import FusionEngine


IMAGE_PATH = "data/simulation/image..jpg"


def main():

    print("=" * 60)
    print("         BORDERGUARD AI - FUSION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Load RGB image.
    # --------------------------------------------------------

    rgb = cv2.imread(IMAGE_PATH)

    if rgb is None:
        raise RuntimeError(f"Could not load image: {IMAGE_PATH}")

    print("RGB image loaded.")

    # --------------------------------------------------------
    # Generate thermal-like image.
    # --------------------------------------------------------

    thermal_simulator = ThermalSimulator()

    thermal = thermal_simulator.generate(rgb)

    print("Thermal-like image generated.")

    # --------------------------------------------------------
    # Create fusion engine.
    # --------------------------------------------------------

    fusion_engine = FusionEngine(
        rgb_weight=0.60,
        thermal_weight=0.40,
    )

    # --------------------------------------------------------
    # Fuse RGB and thermal.
    # --------------------------------------------------------

    fused = fusion_engine.fuse(
        rgb,
        thermal,
    )

    print("Fusion completed.")

    # --------------------------------------------------------
    # Display all three.
    # --------------------------------------------------------

    cv2.imshow(
        "RGB",
        rgb,
    )

    cv2.imshow(
        "Thermal",
        thermal,
    )

    cv2.imshow(
        "Fused",
        fused,
    )

    print("\nPress any key to close.")

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    print("=" * 60)
    print("Fusion test completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
