from zone import Zone


VIDEO_WIDTH = 960
VIDEO_HEIGHT = 540


SAFE_ZONE = Zone(
    name="SAFE",
    polygon=[
        (0, 0),
        (VIDEO_WIDTH, 0),
        (VIDEO_WIDTH, 180),
        (0, 180),
    ],
)


WARNING_ZONE = Zone(
    name="WARNING",
    polygon=[
        (0, 180),
        (VIDEO_WIDTH, 180),
        (VIDEO_WIDTH, 350),
        (0, 350),
    ],
)


RESTRICTED_ZONE = Zone(
    name="RESTRICTED",
    polygon=[
        (0, 350),
        (VIDEO_WIDTH, 350),
        (VIDEO_WIDTH, VIDEO_HEIGHT),
        (0, VIDEO_HEIGHT),
    ],
)


ZONES = [
    SAFE_ZONE,
    WARNING_ZONE,
    RESTRICTED_ZONE,
]
