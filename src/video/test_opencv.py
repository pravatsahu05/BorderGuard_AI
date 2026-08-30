import cv2
import numpy as np


print("=" * 50)
print("        BORDERGUARD AI - OPENCV TEST")
print("=" * 50)

print(f"OpenCV version: {cv2.__version__}")

# Create a blank image.
image = np.zeros((480, 640, 3), dtype=np.uint8)

# Add text to the image.
cv2.putText(
    image,
    "BorderGuard AI",
    (150, 240),
    cv2.FONT_HERSHEY_SIMPLEX,
    1.5,
    (255, 255, 255),
    2,
)

# Display the image.
cv2.imshow("OpenCV Test", image)

print("A test window should now be visible.")
print("Press any key inside the window to close it.")

cv2.waitKey(0)
cv2.destroyAllWindows()

print("OpenCV test completed successfully.")
