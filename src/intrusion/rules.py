RESTRICTED_ZONE = "RESTRICTED"


def is_restricted_zone_entry(
    previous_zone,
    current_zone,
):
    """
    Determine whether an object has entered
    the restricted zone.
    """

    if current_zone != RESTRICTED_ZONE:
        return False

    if previous_zone is None:
        return False

    if previous_zone == RESTRICTED_ZONE:
        return False

    return True
