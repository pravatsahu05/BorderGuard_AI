def yolo_to_xyxy(
    class_id,
    x_center,
    y_center,
    width,
    height,
    image_width,
    image_height,
):

    x_center *= image_width

    y_center *= image_height

    width *= image_width

    height *= image_height

    x1 = x_center - width / 2

    y1 = y_center - height / 2

    x2 = x_center + width / 2

    y2 = y_center + height / 2

    return {
        "class_id": int(class_id),
        "box": (
            x1,
            y1,
            x2,
            y2,
        ),
    }
