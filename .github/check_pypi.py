import json
import re
import sys
from urllib.error import HTTPError
from urllib.request import urlopen


def missing_distributions(version):
    """Returns required distribution types absent from the PyPI release."""
    required = {"sdist", "linux-x86_64", "linux-aarch64", "macos-x86_64", "macos-arm64", "windows-amd64"}
    try:
        with urlopen(f"https://pypi.org/pypi/gordon-to-regorus/{version}/json", timeout=30) as response:
            release = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            return required
        raise

    for distribution in release["urls"]:
        if distribution.get("yanked", False):
            continue
        filename = distribution["filename"]
        if distribution["packagetype"] == "sdist":
            required.discard("sdist")
        elif distribution["packagetype"] == "bdist_wheel":
            platform_tags = filename.removesuffix(".whl").rsplit("-", 1)[-1].split(".")
            for tag in platform_tags:
                if match := re.fullmatch(r"manylinux_[0-9_]+_(x86_64|aarch64)", tag):
                    required.discard("linux-" + match[1])
                elif match := re.fullmatch(r"macosx_[0-9_]+_(x86_64|arm64)", tag):
                    required.discard("macos-" + match[1])
                elif tag == "win_amd64":
                    required.discard("windows-amd64")
    return required


if __name__ == "__main__":
    missing = missing_distributions(sys.argv[1])
    print("Missing distributions: " + ", ".join(sorted(missing)), file=sys.stderr)
    print("true" if missing else "false")
