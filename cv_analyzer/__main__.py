"""Entry point for ``python -m cv_analyzer <image>``.

Usage::

    cd aesthetic-lens
    python -m cv_analyzer path/to/image.jpg --pretty
    python -m cv_analyzer path/to/image.jpg > result.json
"""

from .cli import main

if __name__ == "__main__":
    main()
