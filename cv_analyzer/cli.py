"""CLI entry point for CV analysis — outputs JSON to stdout.

The Reasonix skill calls this as a subprocess and captures stdout.

Usage::

    python -m cv_analyzer.cli path/to/image.jpg
    python -m cv_analyzer.cli path/to/image.jpg --pretty
    python -m cv_analyzer.cli path/to/image.jpg > result.json

Exit codes:

- ``0``  — success (or partial success with ``"status": "degraded"``)
- ``1``  — unexpected exception
- ``2``  — data error (e.g. image cannot be read)
"""

import json
import sys

import click

from .analyze import analyze


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output")
def main(image_path, pretty):
    """Run full CV analysis on IMAGE_PATH and output JSON to stdout."""
    try:
        result = analyze(image_path)
        indent = 2 if pretty else None
        click.echo(json.dumps(result, indent=indent))
        if result.get("status") == "error":
            sys.exit(2)
    except Exception as e:
        click.echo(json.dumps({"error": str(e)}), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
