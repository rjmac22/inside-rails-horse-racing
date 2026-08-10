from __future__ import annotations


def test_database_v2_implementation_modules_import() -> None:
    """Catch syntax/import-cycle failures before attempting the full 1.7 GB build."""

    from inside_rails.database import governed_integration_build  # noqa: F401
    from inside_rails.database import governed_integration_candidate  # noqa: F401
    from inside_rails.database import governed_integration_horse_identity  # noqa: F401
    from inside_rails.database import governed_integration_participant_identity  # noqa: F401
    from inside_rails.database import governed_integration_population  # noqa: F401
    from inside_rails.database import governed_integration_references  # noqa: F401
    from inside_rails.database import governed_integration_time  # noqa: F401
    from inside_rails.database import governed_integration_validator  # noqa: F401
