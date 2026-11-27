"""Canonicalize a locally built sdist and check both wheel build paths."""

import argparse
import gzip
from email import message_from_bytes
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
from zipfile import ZipFile


def canonical_sdist(raw, output, epoch):
    with tarfile.open(raw, "r:gz") as source, output.open("wb") as file:
        with gzip.GzipFile(filename="", fileobj=file, mode="wb", mtime=epoch) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                seen = set()
                for original in sorted(source.getmembers(), key=lambda member: member.name):
                    name = PurePosixPath(original.name)
                    if name.is_absolute() or ".." in name.parts or name in seen:
                        raise ValueError("Source archive contains an unexpected path.")
                    if not (original.isdir() or original.isfile()):
                        raise ValueError("Source archive contains an unexpected entry.")
                    seen.add(name)
                    entry = tarfile.TarInfo(str(name))
                    entry.mtime = epoch
                    entry.mode = 0o755 if original.isdir() or original.mode & 0o111 else 0o644
                    entry.size = original.size
                    entry.type = original.type
                    if original.isfile():
                        with source.extractfile(original) as payload:
                            archive.addfile(entry, payload)
                    else:
                        archive.addfile(entry)


def verify_wheel(root, direct, rebuilt):
    if direct.read_bytes() != rebuilt.read_bytes():
        raise ValueError("Direct and sdist-built wheels differ.")
    source = root / "precis_i18n"
    required = {
        f"precis_i18n/{path.name}": path.read_bytes()
        for path in source.iterdir()
        if path.is_file() and (path.suffix in {".py", ".pyi", ".json"} or path.name == "py.typed")
    }
    with ZipFile(direct) as wheel:
        entries = wheel.namelist()
        if len(entries) != len(set(entries)):
            raise ValueError("Wheel contains a duplicate path.")
        package = {path: wheel.read(path) for path in entries if path.startswith("precis_i18n/")}
        if package != required:
            raise ValueError("Installed package content differs from source.")
        (metadata_path,) = [path for path in entries if path.endswith(".dist-info/METADATA")]
        dist_info = metadata_path.split("/", 1)[0]
        if any(not path.startswith(("precis_i18n/", dist_info + "/")) for path in entries):
            raise ValueError("Wheel contains an unexpected payload.")
        metadata = message_from_bytes(wheel.read(metadata_path))
        if metadata["Name"].lower().replace("_", "-") != "precis-i18n":
            raise ValueError("The existing distribution name must be preserved.")
        if metadata["Requires-Python"] != ">=3.7":
            raise ValueError("Wheel must declare the supported Python floor.")
        if metadata.get_all("Requires-Dist") or metadata.get_all("Provides-Extra"):
            raise ValueError("The existing base runtime has no dependency declarations.")
        for name in ("LICENSE.txt", "UNICODE-LICENSE.txt"):
            payload = root / name
            if payload.exists():
                (member,) = [path for path in entries if path.rsplit("/", 1)[-1] == name]
                if wheel.read(member) != payload.read_bytes():
                    raise ValueError("Wheel notice differs from source.")


def install_runtime_wheel(wheel):
    pip = [sys.executable, "-I", "-m", "pip"]

    def dependency_check():
        result = subprocess.run([*pip, "check"], capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    # Some interpreter distributions seed packages with unresolved dependencies.
    # The qualification checks whether installing this wheel changes that state.
    before = dependency_check()
    subprocess.run([*pip, "install", "--no-deps", "--no-index", str(wheel)], check=True)
    after = dependency_check()
    if before != after or before[0] not in (0, 1) or before[2]:
        raise ValueError("Wheel installation did not preserve the dependency check: {!r}".format(after))
    print("Dependency check before and after installation: {}".format(after[1].strip()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    archive = commands.add_parser("sdist")
    archive.add_argument("raw", type=Path)
    archive.add_argument("output", type=Path)
    archive.add_argument("epoch", type=int)
    wheel = commands.add_parser("wheel")
    wheel.add_argument("root", type=Path)
    wheel.add_argument("direct", type=Path)
    wheel.add_argument("rebuilt", type=Path)
    install = commands.add_parser("install")
    install.add_argument("wheel", type=Path)
    args = parser.parse_args()
    if args.operation == "sdist":
        canonical_sdist(args.raw, args.output, args.epoch)
    elif args.operation == "wheel":
        verify_wheel(args.root, args.direct, args.rebuilt)
    else:
        install_runtime_wheel(args.wheel)


if __name__ == "__main__":
    main()
