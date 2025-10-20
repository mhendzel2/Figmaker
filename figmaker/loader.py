"""
Data loading and fingerprinting for reproducible figure generation.

This module handles loading various data formats and creating fingerprints
for provenance tracking.
"""

from __future__ import annotations
import hashlib
import json
import os
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass(frozen=True)
class Fingerprint:
    """Represents a file fingerprint for provenance tracking."""
    path: str
    size: int
    mtime: float
    sha256: str


def _sha256(path: str, nbytes: int = 1_000_000) -> str:
    """Compute SHA256 hash of file (first nbytes for large files)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(nbytes))
    return h.hexdigest()


def fingerprint(path: str) -> Fingerprint:
    """
    Create a fingerprint for a file.
    
    Args:
        path: Path to the file
        
    Returns:
        Fingerprint containing path, size, modification time, and hash
    """
    st = os.stat(path)
    return Fingerprint(
        path=path,
        size=st.st_size,
        mtime=st.st_mtime,
        sha256=_sha256(path)
    )


def load_table(path: str, sheet: Optional[str] = None) -> pd.DataFrame:
    """
    Load a data table from various formats.
    
    Args:
        path: Path to the data file
        sheet: Sheet name for Excel files (default: first sheet)
        
    Returns:
        DataFrame containing the loaded data
        
    Raises:
        ValueError: If file format is not supported
    """
    path_obj = Path(path)
    ext = path_obj.suffix.lower()
    
    if ext == ".csv":
        return pd.read_csv(path)
    elif ext in (".tsv", ".txt"):
        return pd.read_csv(path, sep="\t")
    elif ext in (".xls", ".xlsx"):
        return pd.read_excel(path, sheet_name=sheet or 0)
    elif ext == ".parquet":
        return pd.read_parquet(path)
    elif ext == ".json":
        return pd.read_json(path)
    else:
        raise ValueError(f"Unsupported format: {ext}")


def save_metadata(meta_path: str, payload: Dict[str, Any]) -> None:
    """
    Save metadata to a JSON file.
    
    Args:
        meta_path: Path where metadata should be saved
        payload: Dictionary containing metadata
    """
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)


# Figmaker-specific image loading
def load_image_with_fingerprint(path: str) -> tuple[Any, Fingerprint]:
    """
    Load an image and create its fingerprint.
    
    Args:
        path: Path to image file
        
    Returns:
        Tuple of (PIL Image, Fingerprint)
    """
    from PIL import Image
    
    image = Image.open(path)
    image.load()  # Ensure image data is loaded into memory
    fp = fingerprint(path)
    
    return image, fp


def create_project_fingerprint(panels: list, settings: dict) -> Dict[str, Any]:
    """
    Create a fingerprint for an entire Figmaker project.
    
    Args:
        panels: List of panel data
        settings: Project settings dictionary
        
    Returns:
        Dictionary containing project fingerprint information
    """
    import platform
    import sys
    from datetime import datetime
    
    # Create fingerprints for all image files
    file_fingerprints = {}
    for panel in panels:
        if 'original_path' in panel and os.path.exists(panel['original_path']):
            try:
                fp = fingerprint(panel['original_path'])
                file_fingerprints[panel['name']] = fp.__dict__
            except (OSError, IOError):
                # Handle cases where file is no longer accessible
                file_fingerprints[panel['name']] = {"error": "File not accessible"}
    
    return {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "file_fingerprints": file_fingerprints,
        "settings": settings,
        "panel_count": len(panels),
    }