import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from evaluation.dataset_validator import (
        validate_split,
    )
except ImportError:
    from src.evaluation.dataset_validator import (
        validate_split,
    )


DATASET_ROOT = "data/borderguard"


splits = [
    "train",
    "val",
    "test",
]


for split in splits:

    print()
    print("=" * 50)
    print(f"VALIDATING: {split.upper()}")
    print("=" * 50)

    result = validate_split(
        f"{DATASET_ROOT}/images/{split}",
        f"{DATASET_ROOT}/labels/{split}",
    )

    print(
        "Images:",
        result["images"],
    )

    print(
        "Images without labels:",
        len(result["images_without_labels"]),
    )

    print(
        "Invalid label entries:",
        len(result["invalid_labels"]),
    )
