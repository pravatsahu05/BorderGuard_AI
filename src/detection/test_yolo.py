from ultralytics import YOLO


print("=" * 60)
print("          BORDERGUARD AI - YOLO TEST")
print("=" * 60)

# ------------------------------------------------------------
# Load a lightweight pretrained YOLO model.
# ------------------------------------------------------------

model = YOLO("yolo11n.pt")

print("YOLO model loaded successfully.")

print("=" * 60)
print("YOLO test completed successfully.")
print("=" * 60)
