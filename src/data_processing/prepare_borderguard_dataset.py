import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_FLIR = RAW_DIR / "FLIR"
RAW_LLVIP = RAW_DIR / "LLVIP"
BORDERGUARD_DIR = BASE_DIR / "data" / "borderguard"

TARGET_CATEGORY_IDS = [1]  # 1: person in FLIR COCO dataset


def convert_coco_bbox(bbox, image_width, image_height):
    x, y, width, height = bbox
    x_center = (x + width / 2) / image_width
    y_center = (y + height / 2) / image_height
    norm_w = width / image_width
    norm_h = height / image_height
    return x_center, y_center, norm_w, norm_h


def process_flir_split(raw_split_dir, split_name, sample_limit=500):
    images_raw_dir = raw_split_dir / "data"
    coco_json_path = raw_split_dir / "coco.json"

    if not coco_json_path.exists():
        print(f"Skipping FLIR {split_name}: {coco_json_path} not found.")
        return 0

    target_images_dir = BORDERGUARD_DIR / "images" / split_name
    target_labels_dir = BORDERGUARD_DIR / "labels" / split_name

    target_images_dir.mkdir(parents=True, exist_ok=True)
    target_labels_dir.mkdir(parents=True, exist_ok=True)

    with coco_json_path.open("r", encoding="utf-8") as f:
        coco = json.load(f)

    images_info = {img["id"]: img for img in coco.get("images", [])}

    labels_by_image = {}
    for ann in coco.get("annotations", []):
        cat_id = ann.get("category_id")
        if cat_id not in TARGET_CATEGORY_IDS:
            continue

        img_id = ann.get("image_id")
        img_info = images_info.get(img_id)
        if not img_info:
            continue

        bbox = ann.get("bbox")
        if not bbox or len(bbox) != 4:
            continue

        w, h = img_info.get("width"), img_info.get("height")
        if not w or not h:
            continue

        xc, yc, nw, nh = convert_coco_bbox(bbox, w, h)
        line = f"0 {xc:.6f} {yc:.6f} {nw:.6f} {nh:.6f}"
        labels_by_image.setdefault(img_id, []).append(line)

    processed_count = 0
    for img_id, labels in list(labels_by_image.items())[:sample_limit]:
        img_info = images_info[img_id]
        file_name = img_info["file_name"]
        stem = Path(file_name).stem

        src_img = images_raw_dir / file_name
        if not src_img.exists():
            found = list(images_raw_dir.glob(f"{stem}.*"))
            if found:
                src_img = found[0]
            else:
                continue

        dest_img = target_images_dir / f"flir_{stem}{src_img.suffix}"
        shutil.copy2(src_img, dest_img)

        dest_label = target_labels_dir / f"flir_{stem}.txt"
        dest_label.write_text("\n".join(labels), encoding="utf-8")

        processed_count += 1

    print(f"[FLIR {split_name.upper()}] Processed {processed_count} images.")
    return processed_count


def process_llvip_dataset(sample_limit=300):
    ann_dir = RAW_LLVIP / "Annotations"
    if not ann_dir.exists():
        print(f"Skipping LLVIP: {ann_dir} not found.")
        return 0

    xml_files = sorted(list(ann_dir.glob("*.xml")))[:sample_limit]
    if not xml_files:
        return 0

    n_train = int(len(xml_files) * 0.7)
    n_val = int(len(xml_files) * 0.2)

    processed_count = 0
    for idx, xml_path in enumerate(xml_files):
        if idx < n_train:
            split_name = "train"
        elif idx < n_train + n_val:
            split_name = "val"
        else:
            split_name = "test"

        target_images_dir = BORDERGUARD_DIR / "images" / split_name
        target_labels_dir = BORDERGUARD_DIR / "labels" / split_name
        target_images_dir.mkdir(parents=True, exist_ok=True)
        target_labels_dir.mkdir(parents=True, exist_ok=True)

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            size_elem = root.find("size")
            width = float(size_elem.find("width").text)
            height = float(size_elem.find("height").text)

            yolo_lines = []
            for obj in root.findall("object"):
                name = obj.find("name").text
                if name.lower() not in ["person", "pedestrian"]:
                    continue

                bnd = obj.find("bndbox")
                xmin = float(bnd.find("xmin").text)
                ymin = float(bnd.find("ymin").text)
                xmax = float(bnd.find("xmax").text)
                ymax = float(bnd.find("ymax").text)

                xc = ((xmin + xmax) / 2.0) / width
                yc = ((ymin + ymax) / 2.0) / height
                w = (xmax - xmin) / width
                h = (ymax - ymin) / height

                line = f"0 {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}"
                yolo_lines.append(line)

            if not yolo_lines:
                continue

            stem = xml_path.stem
            # Search across all subdirectories of RAW_LLVIP for stem image
            found = list(RAW_LLVIP.glob(f"**/{stem}.*"))
            if not found:
                continue
            src_img = found[0]

            dest_img = target_images_dir / f"llvip_{stem}{src_img.suffix}"
            shutil.copy2(src_img, dest_img)

            dest_label = target_labels_dir / f"llvip_{stem}.txt"
            dest_label.write_text("\n".join(yolo_lines), encoding="utf-8")
            processed_count += 1
        except Exception:
            continue

    print(f"[LLVIP] Processed {processed_count} images across splits.")
    return processed_count



def create_data_yaml():
    yaml_content = f"""# BorderGuard AI Combined Dataset Configuration
path: {BORDERGUARD_DIR.as_posix()}
train: images/train
val: images/val
test: images/test

nc: 1
names: ['person']
"""
    yaml_file = BORDERGUARD_DIR / "data.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")
    root_yaml = BASE_DIR / "data.yaml"
    root_yaml.write_text(yaml_content, encoding="utf-8")
    print(f"Created data.yaml at {yaml_file} and {root_yaml}")


def main():
    print("Preparing combined BorderGuard dataset from FLIR + LLVIP raw data...")
    process_flir_split(RAW_FLIR / "images_thermal_train", "train", sample_limit=300)
    process_flir_split(RAW_FLIR / "images_thermal_val", "val", sample_limit=100)
    process_flir_split(RAW_FLIR / "video_thermal_test", "test", sample_limit=50)
    process_llvip_dataset(sample_limit=200)
    create_data_yaml()
    print("Combined dataset preparation complete.")


if __name__ == "__main__":
    main()
