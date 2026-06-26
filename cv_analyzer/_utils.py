"""Unicode-safe image I/O — supports Chinese / non-ASCII paths on Windows.

``cv2.imread`` uses C ``fopen`` under the hood, which on Windows is limited
to the system locale encoding (e.g. GBK) and silently returns ``None`` for
paths containing characters outside that encoding (Chinese, Japanese, …).

The workaround is to read the raw file bytes with ``numpy.fromfile`` (which
delegates to Python's Unicode-aware ``open``) and then decode with
``cv2.imdecode``.

Reference: https://github.com/opencv/opencv/issues/17585
"""

from typing import Optional

import cv2
import numpy as np


def imread_color(path: str) -> Optional[np.ndarray]:
    """Read a color (BGR) image with Unicode path support.

    Returns ``None`` when the file cannot be read (same contract as
    ``cv2.imread``).
    """
    try:
        bytes_ = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(bytes_, cv2.IMREAD_COLOR)
    except Exception:
        return None


def imread_grayscale(path: str) -> Optional[np.ndarray]:
    """Read a grayscale image with Unicode path support.

    Returns ``None`` when the file cannot be read.
    """
    try:
        bytes_ = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(bytes_, cv2.IMREAD_GRAYSCALE)
    except Exception:
        return None


def imread_unchanged(path: str) -> Optional[np.ndarray]:
    """Read an image as-is (including alpha channel) with Unicode path support.

    Returns ``None`` when the file cannot be read.
    """
    try:
        bytes_ = np.fromfile(path, dtype=np.uint8)
        return cv2.imdecode(bytes_, cv2.IMREAD_UNCHANGED)
    except Exception:
        return None
