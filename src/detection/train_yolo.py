import shutil
from pathlib import Path
from ultralytics import YOLO

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_YAML = BASE_DIR / "data" / "borderguard" / "data.yaml"
MODELS_DIR = BASE_DIR / "models"


def train_model(epochs=1, batch_size=16, imgsz=640):
    print(f"Starting YOLO model training for {epochs} epoch(s)...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    model = YOLO("yolo11n.pt")  # Use YOLO11 nano model

    results = model.train(
        data=str(DATA_YAML),
        epochs=epochs,
        batch=batch_size,
        imgsz=imgsz,
        project=str(BASE_DIR / "runs" / "detect"),
        name="borderguard_train",
        exist_ok=True,
        verbose=True,
    )

    # Locate best.pt
    save_dir = Path(results.save_dir)
    best_weights = save_dir / "weights" / "best.pt"
    if not best_weights.exists():
        best_weights = save_dir / "weights" / "last.pt"

    target_weights = MODELS_DIR / "best.pt"
    if best_weights.exists():
        shutil.copy2(best_weights, target_weights)
        print(f"Successfully copied {best_weights} -> {target_weights}")
    else:
        print(f"Warning: {best_weights} not found.")

    return results, target_weights


if __name__ == "__main__":
    import sys

    epochs = 10
    batch_size = 8

    for i in range(1, len(sys.argv)):
        if sys.argv[i] == "--epochs" and i + 1 < len(sys.argv):
            epochs = int(sys.argv[i + 1])
        elif sys.argv[i] == "--batch" and i + 1 < len(sys.argv):
            batch_size = int(sys.argv[i + 1])

    train_model(epochs=epochs, batch_size=batch_size, imgsz=640)

