import os
from enum import Enum


class ChangelogType(Enum):
    # default
    STANDARD = 0

    # follows the Conventional Commit Spec
    CONVENTIONAL = 1

    @staticmethod
    def from_environment():
        _type = os.getenv("CHANGELOG_TYPE")
        if _type is None:
            return ChangelogType.STANDARD

        for i in ChangelogType:
            if _type.isdigit() and int(_type) == i.value or _type == i.name:
                return i

        # fall back to the default
        return ChangelogType.STANDARD
