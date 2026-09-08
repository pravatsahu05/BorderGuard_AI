from dataclasses import dataclass


@dataclass
class DetectionEvaluation:

    precision: float

    recall: float

    f1_score: float

    mean_iou: float

    total_predictions: int

    true_positives: int

    false_positives: int

    false_negatives: int
