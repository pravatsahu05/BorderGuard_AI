import os
import cv2
import numpy as np


OUTPUT_PATH = "data/simulation/sample.mp4"

WIDTH = 960
HEIGHT = 540
FPS = 30
DURATION_SECONDS = 10

TOTAL_FRAMES = FPS * DURATION_SECONDS

# Ensure output directory exists
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

fourcc = cv2.VideoWriter_fourcc(*"mp4v")

writer = cv2.VideoWriter(OUTPUT_PATH, fourcc, FPS, (WIDTH, HEIGHT))


for frame_number in range(TOTAL_FRAMES):

    # Create a dark surveillance-style background.
    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

    # --------------------------------------------------------
    # Draw simulated terrain
    # --------------------------------------------------------

    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (45, 55, 45), -1)

    # --------------------------------------------------------
    # Draw safe zone
    # --------------------------------------------------------

    cv2.rectangle(frame, (0, 0), (WIDTH, 200), (60, 80, 60), -1)

    # --------------------------------------------------------
    # Draw warning zone
    # --------------------------------------------------------

    cv2.rectangle(frame, (0, 200), (WIDTH, 350), (80, 80, 50), -1)

    # --------------------------------------------------------
    # Draw restricted zone
    # --------------------------------------------------------

    cv2.rectangle(frame, (0, 350), (WIDTH, HEIGHT), (80, 50, 50), -1)

    # --------------------------------------------------------
    # Draw zone labels
    # --------------------------------------------------------

    cv2.putText(
        frame, "SAFE ZONE", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2
    )

    cv2.putText(
        frame,
        "WARNING ZONE",
        (30, 250),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    cv2.putText(
        frame,
        "RESTRICTED ZONE",
        (30, 400),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2,
    )

    # --------------------------------------------------------
    # Simulate a moving person
    # --------------------------------------------------------

    x = 150 + int(frame_number * 5)

    y = 100 + int(frame_number * 2)

    # Keep object inside frame.
    x = min(x, WIDTH - 50)
    y = min(y, HEIGHT - 50)

    # Draw head.
    cv2.circle(frame, (x, y - 20), 12, (200, 200, 200), -1)

    # Draw body.
    cv2.rectangle(frame, (x - 12, y - 8), (x + 12, y + 35), (200, 200, 200), -1)

    # --------------------------------------------------------
    # Simulated camera label
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "SIMULATED BORDER CAMERA",
        (WIDTH - 330, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    writer.write(frame)


writer.release()

print("=" * 50)
print("Synthetic surveillance video created.")
print(f"Location: {OUTPUT_PATH}")
print(f"Frames: {TOTAL_FRAMES}")
print(f"FPS: {FPS}")
print(f"Resolution: {WIDTH} x {HEIGHT}")
print("=" * 50)
