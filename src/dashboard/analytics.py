import pandas as pd


def events_to_dataframe(events):
    """
    Convert a list of event dictionaries
    into a pandas DataFrame.
    """

    if not events:
        return pd.DataFrame()

    return pd.DataFrame(events)


def risk_distribution_dataframe(distribution):
    """
    Convert risk distribution dictionary
    into a DataFrame.

    Example:

        {
            "LOW": 5,
            "MEDIUM": 8,
            "HIGH": 3,
            "CRITICAL": 1
        }
    """

    if not distribution:
        return pd.DataFrame(
            columns=[
                "Severity",
                "Events",
            ]
        )

    return pd.DataFrame(
        [
            {
                "Severity": severity,
                "Events": count,
            }
            for severity, count in distribution.items()
        ]
    )


def zone_distribution_dataframe(distribution):
    """
    Convert zone distribution dictionary
    into a DataFrame.
    """

    if not distribution:
        return pd.DataFrame(
            columns=[
                "Zone",
                "Events",
            ]
        )

    return pd.DataFrame(
        [
            {
                "Zone": zone,
                "Events": count,
            }
            for zone, count in distribution.items()
        ]
    )


def event_type_dataframe(distribution):
    """
    Convert event-type distribution dictionary
    into a DataFrame.
    """

    if not distribution:
        return pd.DataFrame(
            columns=[
                "Event Type",
                "Events",
            ]
        )

    return pd.DataFrame(
        [
            {
                "Event Type": event_type,
                "Events": count,
            }
            for event_type, count in distribution.items()
        ]
    )
