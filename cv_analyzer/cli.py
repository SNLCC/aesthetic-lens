"""CLI entry point for CV analysis — outputs JSON to stdout.

The Reasonix skill calls this as a subprocess and captures stdout.

Usage::

    python -m cv_analyzer.cli path/to/image.jpg
    python -m cv_analyzer.cli path/to/image.jpg --pretty
    python -m cv_analyzer.cli path/to/image.jpg --pretty --with-image
    python -m cv_analyzer.cli path/to/image.jpg > result.json

Exit codes:

- ``0``  — success (or partial success with ``"status": "degraded"``)
- ``1``  — unexpected exception
- ``2``  — data error (e.g. image cannot be read)
"""

import base64
import sys

import click

from ._json_utils import safe_json_dumps
from .analyze import analyze


@click.command()
@click.argument("image_path", type=click.Path(exists=True))
@click.option("--pretty", is_flag=True, help="Pretty-print JSON output")
@click.option("--with-image", is_flag=True, help="Include base64-encoded image in output (for LLM vision)")
def main(image_path, pretty, with_image):
    """Run full CV analysis on IMAGE_PATH and output JSON to stdout."""
    try:
        result = analyze(image_path)

        if with_image:
            with open(image_path, "rb") as f:
                img_bytes = f.read()
            result["image_base64"] = base64.b64encode(img_bytes).decode("ascii")
            # Add a data URL hint for multimodal LLM consumption
            result["image_type"] = "base64"

        indent = 2 if pretty else None
        click.echo(safe_json_dumps(result, indent=indent))
        if result.get("status") == "error":
            sys.exit(2)
    except Exception as e:
        click.echo(safe_json_dumps({"error": str(e)}), err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
