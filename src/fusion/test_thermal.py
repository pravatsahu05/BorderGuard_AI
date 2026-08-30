import cv2

from thermal_simulator import ThermalSimulator


IMAGE_PATH = "data/simulation/image..jpg"


def main():

    print("=" * 60)
    print("       BORDERGUARD AI - THERMAL SIMULATION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Load image.
    # --------------------------------------------------------

    image = cv2.imread(IMAGE_PATH)

    if image is None:
        raise RuntimeError(f"Could not load image: {IMAGE_PATH}")

    print("Input image loaded successfully.")

    # --------------------------------------------------------
    # Create thermal simulator.
    # --------------------------------------------------------

    simulator = ThermalSimulator(
        blur_size=5,
        contrast=1.5,
    )

    # --------------------------------------------------------
    # Generate thermal-like image.
    # --------------------------------------------------------

    thermal = simulator.generate(image)

    print("Thermal-like representation generated.")

    # --------------------------------------------------------
    # Display RGB and thermal images.
    # --------------------------------------------------------

    cv2.imshow(
        "RGB Input",
        image,
    )

    cv2.imshow(
        "Simulated Thermal",
        thermal,
    )

    print("\nPress any key to close.")

    cv2.waitKey(0)

    cv2.destroyAllWindows()

    print("=" * 60)
    print("Thermal simulation test completed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
