"""
EEG data loading module supporting multiple file formats.

Supported formats
-----------------
* European Data Format (.edf)
* MNE-Python FIF (.fif)
* BrainVision (.vhdr)
* EEGLAB (.set)
* Generic CSV (.csv)
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Optional, Sequence, Tuple

import mne
import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_eeg_file(
    file_path_or_buffer,
    file_type: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[mne.io.BaseRaw, Dict[str, Any]]:
    """Load an EEG file and return an MNE Raw object with metadata.

    Parameters
    ----------
    file_path_or_buffer : str or path-like or file-like
        Path to the EEG file, or a file-like buffer (e.g. a Streamlit
        ``UploadedFile``).
    file_type : str, optional
        File extension including the dot (e.g. ``'.edf'``).  If *None*,
        the extension is inferred from *file_path_or_buffer*.
    **kwargs
        Additional keyword arguments forwarded to format-specific loaders.
        For CSV files the following are recognised:

        * ``sfreq`` (float): sampling frequency (default 256).
        * ``ch_names`` (list[str]): channel names to select.
        * ``time_col`` (str): name of a time column to drop.

    Returns
    -------
    raw : mne.io.BaseRaw
        Preloaded MNE Raw object.
    info_dict : dict
        Metadata extracted via :func:`extract_data_info`.

    Raises
    ------
    ValueError
        If the file format is not supported.
    """
    # ---- Detect file type ------------------------------------------------
    if file_type is None:
        if hasattr(file_path_or_buffer, "name"):
            file_type = os.path.splitext(file_path_or_buffer.name)[1].lower()
        else:
            file_type = os.path.splitext(str(file_path_or_buffer))[1].lower()

    file_type = file_type.lower()

    # ---- Dispatch --------------------------------------------------------
    raw: mne.io.BaseRaw

    if file_type == ".edf":
        raw = mne.io.read_raw_edf(file_path_or_buffer, preload=True, verbose=False)
    elif file_type == ".fif":
        raw = mne.io.read_raw_fif(file_path_or_buffer, preload=True, verbose=False)
    elif file_type == ".vhdr":
        raw = mne.io.read_raw_brainvision(file_path_or_buffer, preload=True, verbose=False)
    elif file_type == ".set":
        raw = mne.io.read_raw_eeglab(file_path_or_buffer, preload=True, verbose=False)
    elif file_type == ".csv":
        raw = _load_csv(file_path_or_buffer, **kwargs)
    else:
        raise ValueError(
            f"Unsupported file format: '{file_type}'. "
            "Supported: .edf, .fif, .vhdr, .set, .csv"
        )

    info_dict = extract_data_info(raw)
    return raw, info_dict


# ---------------------------------------------------------------------------
# CSV loader (internal)
# ---------------------------------------------------------------------------

def _load_csv(
    file_path_or_buffer,
    sfreq: float = 256.0,
    ch_names: Optional[List[str]] = None,
    time_col: Optional[str] = None,
    **kwargs: Any,
) -> mne.io.RawArray:
    """Load EEG data from a CSV file.

    Each column (except an optional time column) is treated as a channel.
    Values are expected to be in **microvolts**; if the absolute maximum
    exceeds 0.01 the array is scaled by 1e-6 to convert to volts (MNE
    convention).

    Parameters
    ----------
    file_path_or_buffer : str or file-like
        Path or buffer.
    sfreq : float
        Sampling frequency in Hz.
    ch_names : list[str], optional
        Subset of columns to keep as channels.
    time_col : str, optional
        Name of the time column to drop before processing.

    Returns
    -------
    raw : mne.io.RawArray
    """
    df = pd.read_csv(file_path_or_buffer)

    # Drop time column if specified
    if time_col and time_col in df.columns:
        df = df.drop(columns=[time_col])

    # Select requested channels
    if ch_names:
        available = [c for c in ch_names if c in df.columns]
        if not available:
            raise ValueError(
                f"None of the specified channels found in CSV. "
                f"Available columns: {list(df.columns)}"
            )
        df = df[available]
        ch_names = available
    else:
        ch_names = list(df.columns)

    data = df.values.T.astype(np.float64)  # (n_channels, n_samples)

    # Auto-scale: if values look like microvolts, convert to volts
    if np.max(np.abs(data)) > 1e-2:
        data = data * 1e-6

    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    raw = mne.io.RawArray(data, info, verbose=False)
    return raw


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_data_info(raw: mne.io.BaseRaw) -> Dict[str, Any]:
    """Extract metadata from an MNE Raw object.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Loaded EEG data.

    Returns
    -------
    info_dict : dict
        Dictionary with keys ``n_channels``, ``ch_names``, ``sfreq``,
        ``n_samples``, ``duration``, ``annotations``, ``ch_types``.
    """
    annotations = None
    if raw.annotations is not None and len(raw.annotations) > 0:
        annotations = [
            {
                "onset": float(ann["onset"]),
                "duration": float(ann["duration"]),
                "description": str(ann["description"]),
            }
            for ann in raw.annotations
        ]

    return {
        "n_channels": len(raw.ch_names),
        "ch_names": list(raw.ch_names),
        "sfreq": float(raw.info["sfreq"]),
        "n_samples": int(raw.n_times),
        "duration": float(raw.times[-1] - raw.times[0]) if len(raw.times) > 1 else 0.0,
        "annotations": annotations,
        "ch_types": [
            mne.channel_type(raw.info, i) for i in range(len(raw.ch_names))
        ],
    }


# ---------------------------------------------------------------------------
# Streamlit upload helper
# ---------------------------------------------------------------------------

def save_uploaded_file(uploaded_file) -> str:
    """Save a Streamlit ``UploadedFile`` to a temporary location.

    Parameters
    ----------
    uploaded_file : streamlit.runtime.uploaded_file_manager.UploadedFile
        File uploaded through ``st.file_uploader``.

    Returns
    -------
    path : str
        Absolute path to the saved temporary file.
    """
    suffix = os.path.splitext(uploaded_file.name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.getbuffer())
        return tmp.name
