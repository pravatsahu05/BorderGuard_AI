from rules import is_restricted_zone_entry


def main():

    test_cases = [
        ("SAFE", "WARNING"),
        ("WARNING", "RESTRICTED"),
        ("SAFE", "RESTRICTED"),
        ("RESTRICTED", "RESTRICTED"),
        ("RESTRICTED", "WARNING"),
        (None, "RESTRICTED"),
    ]

    print("=" * 60)
    print("       BORDERGUARD AI - INTRUSION RULE TEST")
    print("=" * 60)

    for previous, current in test_cases:

        result = is_restricted_zone_entry(
            previous,
            current,
        )

        print(f"{previous} -> {current} " f"=> intrusion={result}")

    print("=" * 60)


if __name__ == "__main__":
    main()
