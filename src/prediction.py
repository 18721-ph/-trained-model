def classify_default(
    default_probability,
    decision_threshold
):
    if default_probability >= decision_threshold:
        return "DEFAULT"

    return "NO DEFAULT"