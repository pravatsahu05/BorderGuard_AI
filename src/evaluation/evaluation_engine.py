try:
    from evaluation.detection_metrics import (
        precision,
        recall,
        f1_score,
    )
    from evaluation.iou import (
        calculate_iou,
    )
    from evaluation.evaluation_result import (
        DetectionEvaluation,
    )
except ImportError:
    from src.evaluation.detection_metrics import (
        precision,
        recall,
        f1_score,
    )
    from src.evaluation.iou import (
        calculate_iou,
    )
    from src.evaluation.evaluation_result import (
        DetectionEvaluation,
    )



class DetectionEvaluationEngine:

    def evaluate(
        self,
        predictions,
        ground_truth,
        iou_threshold=0.5,
    ):

        true_positives = 0

        false_positives = 0

        false_negatives = 0

        matched_ious = []

        matched_ground_truth = set()

        for prediction_index, prediction in enumerate(predictions):

            best_iou = 0.0

            best_gt_index = None

            for gt_index, gt in enumerate(ground_truth):

                if gt_index in matched_ground_truth:

                    continue

                if prediction["class"] != gt["class"]:

                    continue

                current_iou = calculate_iou(
                    prediction["box"],
                    gt["box"],
                )

                if current_iou > best_iou:

                    best_iou = current_iou

                    best_gt_index = gt_index

            if best_iou >= iou_threshold and best_gt_index is not None:

                true_positives += 1

                matched_ground_truth.add(best_gt_index)

                matched_ious.append(best_iou)

            else:

                false_positives += 1

        false_negatives = len(ground_truth) - len(matched_ground_truth)

        precision_value = precision(
            true_positives,
            false_positives,
        )

        recall_value = recall(
            true_positives,
            false_negatives,
        )

        f1_value = f1_score(
            precision_value,
            recall_value,
        )

        if matched_ious:

            mean_iou = sum(matched_ious) / len(matched_ious)

        else:

            mean_iou = 0.0

        return DetectionEvaluation(
            precision=precision_value,
            recall=recall_value,
            f1_score=f1_value,
            mean_iou=mean_iou,
            total_predictions=(len(predictions)),
            true_positives=(true_positives),
            false_positives=(false_positives),
            false_negatives=(false_negatives),
        )
