def precision(
    true_positive,
    false_positive,
):

    denominator = true_positive + false_positive

    if denominator == 0:

        return 0.0

    return true_positive / denominator


def recall(
    true_positive,
    false_negative,
):

    denominator = true_positive + false_negative

    if denominator == 0:

        return 0.0

    return true_positive / denominator


def f1_score(
    precision_value,
    recall_value,
):

    denominator = precision_value + recall_value

    if denominator == 0:

        return 0.0

    return 2 * precision_value * recall_value / denominator
