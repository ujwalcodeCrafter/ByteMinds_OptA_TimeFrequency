"""
EEG preprocessing utilities for time-frequency analysis.

Provides bandpass filtering, single-channel extraction, and epoching
helpers that sit between raw data loading and TF computation.
"""

from __future__ import annotations

from typing import Optional, Tuple

import mne
import numpy as np


def apply_bandpass_filter(
    raw: mne.io.BaseRaw,
    l_freq: float = 0.5,
    h_freq: float = 100.0,
) -> mne.io.BaseRaw:
    """Apply a zero-phase FIR bandpass filter to raw data.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Input EEG data (will **not** be modified in-place).
    l_freq : float
        Lower passband edge in Hz.
    h_freq : float
        Upper passband edge in Hz.

    Returns
    -------
    filtered : mne.io.BaseRaw
        A filtered copy of the input data.
    """
    filtered = raw.copy().filter(l_freq=l_freq, h_freq=h_freq, verbose=False)
    return filtered


def get_channel_data(
    raw: mne.io.BaseRaw,
    channel_name: str,
    tmin: Optional[float] = None,
    tmax: Optional[float] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Extract single-channel data with optional time cropping.

    Parameters
    ----------
    raw : mne.io.BaseRaw
        Input EEG data.
    channel_name : str
        Name of the channel to extract.
    tmin : float, optional
        Start time in seconds.  *None* means the beginning of the recording.
    tmax : float, optional
        End time in seconds.  *None* means the end of the recording.

    Returns
    -------
    data : np.ndarray, shape (n_times,)
        Channel data in volts.
    times : np.ndarray, shape (n_times,)
        Corresponding time vector in seconds.

    Raises
    ------
    ValueError
        If *channel_name* is not present in the data.
    """
    if channel_name not in raw.ch_names:
        raise ValueError(
            f"Channel '{channel_name}' not found. "
            f"Available: {raw.ch_names}"
        )

    data_raw = raw.copy()
    if tmin is not None or tmax is not None:
        data_raw = data_raw.crop(tmin=tmin, tmax=tmax)

    ch_idx = data_raw.ch_names.index(channel_name)
    data = data_raw.get_data()[ch_idx]
    times = data_raw.times
    return data, times


def create_epochs_array(
    data: np.ndarray,
    sfreq: float,
    epoch_length: Optional[float] = None,
) -> np.ndarray:
    """Reshape continuous single-channel data into epochs.

    This is a lightweight utility for preparing data for TF functions
    that expect an ``(n_epochs, n_channels, n_times)`` array (e.g.
    ``mne.time_frequency.tfr_array_morlet``).

    Parameters
    ----------
    data : np.ndarray, shape (n_times,)
        Continuous single-channel time series.
    sfreq : float
        Sampling frequency in Hz.
    epoch_length : float, optional
        Desired epoch duration in seconds.  If *None* the entire signal
        is returned as a single epoch.

    Returns
    -------
    epochs : np.ndarray, shape (n_epochs, 1, n_times_per_epoch)
        Epoched data suitable for MNE TF functions.
    """
    if epoch_length is None:
        return data.reshape(1, 1, -1)

    n_samples_per_epoch = int(epoch_length * sfreq)
    n_epochs = len(data) // n_samples_per_epoch

    if n_epochs == 0:
        return data.reshape(1, 1, -1)

    data_trimmed = data[: n_epochs * n_samples_per_epoch]
    epochs = data_trimmed.reshape(n_epochs, 1, n_samples_per_epoch)
    return epochs
