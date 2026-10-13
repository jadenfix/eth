"""Install the maintained, official Linux CLI only after verifying its SHA256."""

import hashlib
import io
from pathlib import Path
import platform
import sys
import urllib.request
import zipfile

VERSION = "1.15.9"
ARCHIVE_SHA256 = "76edd0b22d2f27d3d2e097cd793209646f719cf60f02ff3af626b07361137da1"
URL = f"https://releases.hashicorp.com/terraform/{VERSION}/terraform_{VERSION}_linux_amd64.zip"


def install(destination):
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "amd64"):
        raise RuntimeError("This verified installer supports Linux amd64 only")
    with urllib.request.urlopen(URL, timeout=60) as response:
        archive = response.read()
    actual = hashlib.sha256(archive).hexdigest()
    if actual != ARCHIVE_SHA256:
        raise RuntimeError(f"Terraform archive checksum mismatch: {actual}")
    directory = Path(destination).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        binary = bundle.read("terraform")
    target = directory / "terraform"
    target.write_bytes(binary)
    target.chmod(0o755)
    print(f"Verified Terraform {VERSION} archive SHA256 {actual}")
    return target


if __name__ == "__main__":
    install(sys.argv[1])
