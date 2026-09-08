from pathlib import Path
from collections import Counter


def count_classes(
    label_directory,
):

    label_directory = Path(label_directory)

    counts = Counter()

    for label_file in label_directory.glob("*.txt"):

        with label_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                parts = line.strip().split()

                if not parts:

                    continue

                class_id = int(parts[0])

                counts[class_id] += 1

    return counts


counts = count_classes("data/borderguard/labels/train")

print("Class distribution:")

for class_id, count in sorted(counts.items()):

    print(f"Class {class_id}: {count}")
