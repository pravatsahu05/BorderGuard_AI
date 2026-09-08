def generate_summary(
    total_events,
    high_risk,
    critical_events,
    active_alerts,
):
    """
    Generate a simple operator-friendly
    security summary.

    This function does NOT calculate risk.
    It only summarizes already-generated
    security information.
    """

    if critical_events > 0:

        return (
            "🚨 Critical security activity detected. "
            "Immediate operator attention is recommended."
        )

    if high_risk > 0:

        return "⚠️ High-risk security activity detected. " "Monitor active events."

    if active_alerts > 0:

        return "ℹ️ Active security alerts require monitoring."

    if total_events > 0:

        return (
            "🟢 Security events are being recorded. "
            "No high-severity activity is currently detected."
        )

    return "🟢 No security events have been recorded yet."
