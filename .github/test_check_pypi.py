import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from check_pypi import missing_distributions


class PublishedDistributionsTests(unittest.TestCase):
    def setUp(self):
        self.files = [
            {"filename": "gordon_to_regorus-0.15.0.tar.gz", "packagetype": "sdist"},
            *[
                {"filename": f"gordon_to_regorus-0.15.0-cp310-abi3-{platform}.whl", "packagetype": "bdist_wheel"}
                for platform in (
                    "manylinux_2_34_x86_64",
                    "manylinux_2_34_aarch64",
                    "macosx_10_12_x86_64",
                    "macosx_11_0_arm64",
                    "win_amd64",
                )
            ],
        ]

    def check(self, files):
        with patch("check_pypi.urlopen", return_value=io.BytesIO(json.dumps({"urls": files}).encode())):
            return missing_distributions("0.15.0")

    def test_complete_release(self):
        self.assertEqual(self.check(self.files), set())

    def test_each_missing_distribution(self):
        for index, expected in enumerate(("sdist", "linux-x86_64", "linux-aarch64", "macos-x86_64", "macos-arm64", "windows-amd64")):
            with self.subTest(expected=expected):
                self.assertEqual(self.check(self.files[:index] + self.files[index + 1:]), {expected})

    def test_yanked_distribution_is_missing(self):
        self.files[-1]["yanked"] = True
        self.assertEqual(self.check(self.files), {"windows-amd64"})

    def test_multiple_platform_tags(self):
        self.files[1]["filename"] = "gordon_to_regorus-0.15.0-cp310-abi3-manylinux_2_17_x86_64.manylinux2014_x86_64.whl"
        self.assertEqual(self.check(self.files), set())

    def test_missing_release(self):
        with patch("check_pypi.urlopen", side_effect=HTTPError("url", 404, "Not Found", {}, None)):
            self.assertEqual(missing_distributions("0.15.0"), self.check([]))

    def test_server_errors_fail(self):
        for code in (403, 429, 500, 503):
            with self.subTest(code=code), patch("check_pypi.urlopen", side_effect=HTTPError("url", code, "error", {}, None)):
                with self.assertRaises(HTTPError):
                    missing_distributions("0.15.0")

    def test_network_errors_fail(self):
        with patch("check_pypi.urlopen", side_effect=URLError("unavailable")):
            with self.assertRaises(URLError):
                missing_distributions("0.15.0")

    def test_invalid_response_fails(self):
        with patch("check_pypi.urlopen", return_value=io.BytesIO(b"not json")):
            with self.assertRaises(ValueError):
                missing_distributions("0.15.0")


if __name__ == "__main__":
    unittest.main()
