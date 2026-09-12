from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DATA_DIR = (
    PROJECT_ROOT / "data" / "processed"
)

FINAL_DATA_DIR = (
    PROJECT_ROOT / "data" / "borderguard"
)


FLIR_RAW_DIR = (
    RAW_DATA_DIR / "flir"
)

LLVIP_RAW_DIR = (
    RAW_DATA_DIR / "llvip"
)


FLIR_PROCESSED_DIR = (
    PROCESSED_DATA_DIR / "flir"
)

LLVIP_PROCESSED_DIR = (
    PROCESSED_DATA_DIR / "llvip"
)


CLASS_NAMES = {
    0: "person",
}