import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def new_path_with_timestamp(path: Path, ext: Optional[str] = None) -> Path:
    now = f"{datetime.now():_%y%m%d_%H%M%S}"
    stem = path.stem
    rematch = re.search(r"_\d{6}_\d{6}$", stem)
    if rematch is not None:
        stem = stem[: rematch.start()]
    ext = ext or path.suffix
    return path.with_name(f"{stem}{now}{ext}")
