import argparse
import json
import sys
import typing as t

from rich.console import Console

from cratedb_toolkit import __version__
from cratedb_toolkit.io.mongodb.core import export, extract, translate

console = Console(stderr=True)
rich = console


def extract_parser(subargs):
    parser = subargs.add_parser("extract", help="Extract a schema from a MongoDB database")
    parser.add_argument("--url", default="mongodb://localhost:27017", help="MongoDB URL")
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", default=27017, help="MongoDB port")
    parser.add_argument("--database", required=True, help="MongoDB database")
    parser.add_argument("--collection", help="MongoDB collection to create a schema for")
    parser.add_argument(
        "--scan",
        choices=["full", "partial"],
        help="Whether to fully scan the MongoDB collections or only partially.",
    )
    parser.add_argument("-o", "--out", required=False)


def translate_parser(subargs):
    parser = subargs.add_parser(
        "translate",
        help="Translate a MongoDB schema definition to a CrateDB table schema",
    )
    parser.add_argument("-i", "--infile", help="The JSON file to read the MongoDB schema from")


def export_parser(subargs):
    parser = subargs.add_parser("export", help="Export a MongoDB collection as plain JSON")
    parser.add_argument("--url", default="mongodb://localhost:27017", help="MongoDB URL")
    parser.add_argument("--collection", required=True)
    parser.add_argument("--host", default="localhost", help="MongoDB host")
    parser.add_argument("--port", default=27017, help="MongoDB port")
    parser.add_argument("--database", required=True, help="MongoDB database")


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        help="print package version of pyproject_fmt",
        version=f"%(prog)s ({__version__})",
    )
    subparsers = parser.add_subparsers(dest="command")
    extract_parser(subparsers)
    translate_parser(subparsers)
    export_parser(subparsers)
    return parser.parse_args()


def extract_to_file(args):
    """
    Extract a schema or set of schemas from MongoDB collections into a JSON file.
    """

    schema = extract(args)

    out_label = args.out or "stdout"
    rich.print(f"\nWriting resulting schema to {out_label}")
    fp: t.TextIO
    if args.out:
        fp = open(args.out, "w")
    else:
        fp = sys.stdout
    json.dump(schema, fp=fp, indent=4)
    fp.flush()


def translate_from_file(args):
    """
    Read in a JSON file and extract the schema from it.
    """
    fp: t.TextIO
    if args.infile:
        fp = open(args.infile, "r")
    else:
        fp = sys.stdin
    schema = json.load(fp)
    translate(schema)


def export_to_stdout(args):
    sys.stdout.buffer.write(export(args).read())


def main():
    rich.print("\n[green bold]MongoDB[/green bold] -> [blue bold]CrateDB[/blue bold] Exporter :: Schema Extractor\n\n")
    args = get_args()
    if args.command == "extract":
        extract_to_file(args)
    elif args.command == "translate":
        translate_from_file(args)
    elif args.command == "export":
        export_to_stdout(args)
