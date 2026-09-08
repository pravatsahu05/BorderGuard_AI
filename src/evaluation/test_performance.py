import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))
if str(BASE_DIR / "src") not in sys.path:
    sys.path.append(str(BASE_DIR / "src"))

try:
    from evaluation.performance_metrics import (
        PerformanceTimer,
    )
except ImportError:
    from src.evaluation.performance_metrics import (
        PerformanceTimer,
    )


timer = PerformanceTimer()

timer.start()


for _ in range(100):
    time.sleep(0.01)
    timer.frame_processed()


print(
    "Frames:",
    timer.frame_count,
)

print(
    "Elapsed:",
    round(
        timer.get_elapsed_time(),
        3,
    ),
    "seconds",
)

print(
    "FPS:",
    round(
        timer.get_fps(),
        2,
    ),
)
