"""JSON serialization helpers — handles numpy types safely."""

import json
from typing import Any


class SafeEncoder(json.JSONEncoder):
    """JSON encoder that converts numpy / non-serializable types."""

    def default(self, obj: Any) -> Any:
        try:
            import numpy as np

            if isinstance(obj, np.integer):
                return int(obj)
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
        except ImportError:
            pass
        # Fallback: try to convert to something serializable
        try:
            return str(obj)
        except Exception:
            return super().default(obj)


def safe_json_dumps(data: Any, indent: int = 2, **kwargs) -> str:
    """json.dumps with SafeEncoder."""
    return json.dumps(data, indent=indent, cls=SafeEncoder, **kwargs)


def safe_json_dump(data: Any, fp, indent: int = 2, **kwargs) -> None:
    """json.dump with SafeEncoder."""
    return json.dump(data, fp, indent=indent, cls=SafeEncoder, **kwargs)
