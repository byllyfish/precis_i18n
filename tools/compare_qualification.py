"""Compare full source and installed-wheel scenario identities."""

from argparse import ArgumentParser
from pathlib import Path
from xml.etree import ElementTree


def results(path):
    found = {}
    for node in ElementTree.parse(path).iter("testcase"):
        identity = node.attrib["classname"], node.attrib["name"]
        if identity in found:
            raise ValueError("Qualification has a duplicate scenario identifier.")
        if node.find("failure") is not None or node.find("error") is not None:
            raise ValueError("Qualification contains a failure.")
        skipped = node.find("skipped")
        found[identity] = None if skipped is None else skipped.get("message")
    if not found:
        raise ValueError("Qualification contains no scenarios.")
    return found


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("results", type=Path)
    parser.add_argument("interpreters", nargs="+")
    options = parser.parse_args()
    for interpreter in options.interpreters:
        source = results(options.results / f"source-{interpreter}.xml")
        wheel = results(options.results / f"wheel-{interpreter}.xml")
        if source != wheel:
            raise ValueError(f"Source and wheel scenarios differ on {interpreter}.")
        passing = sum(outcome is None for outcome in source.values())
        print(f"{interpreter}: {passing} matching passing scenarios, {len(source) - passing} matching skips")


if __name__ == "__main__":
    main()
