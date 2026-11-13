"""
Validation utilities for BCI Time-Frequency Analysis parameters.

Every public function returns a tuple ``(is_valid: bool, message: str)``
where *message* is an empty string on success or a human-readable error
description on failure.
"""

from __future__ import annotations

import numbers
from typing import Any, Dict, List, Sequence, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# Frequency validation
# ---------------------------------------------------------------------------

def validate_frequency_range(
    fmin: float,
    fmax: float,
    sfreq: float,
) -> Tuple[bool, str]:
    """Validate a frequency range against the Nyquist criterion.

    Checks
    ------
    * ``fmin`` and ``fmax`` are finite numbers.
    * ``fmin > 0``.
    * ``fmin < fmax``.
    * ``fmax <= sfreq / 2`` (Nyquist frequency).
    * ``sfreq > 0``.

    Parameters
    ----------
    fmin : float
        Lower bound of the frequency range in Hz.
    fmax : float
        Upper bound of the frequency range in Hz.
    sfreq : float
        Sampling frequency of the data in Hz.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    # --- type / finiteness checks ---
    for name, val in [("fmin", fmin), ("fmax", fmax), ("sfreq", sfreq)]:
        if not isinstance(val, numbers.Real):
            return False, f"{name} must be a real number, got {type(val).__name__}."
        if not np.isfinite(val):
            return False, f"{name} must be finite, got {val}."

    if sfreq <= 0:
        return False, f"Sampling frequency must be positive, got {sfreq} Hz."

    if fmin <= 0:
        return False, f"Minimum frequency must be > 0 Hz, got {fmin} Hz."

    if fmin >= fmax:
        return False, (
            f"Minimum frequency ({fmin} Hz) must be strictly less than "
            f"maximum frequency ({fmax} Hz)."
        )

    nyquist = sfreq / 2.0
    if fmax > nyquist:
        return False, (
            f"Maximum frequency ({fmax} Hz) exceeds the Nyquist frequency "
            f"({nyquist} Hz) for sampling rate {sfreq} Hz."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Wavelet cycles
# ---------------------------------------------------------------------------

def validate_wavelet_cycles(
    n_cycles: Union[float, np.ndarray, Sequence[float]],
    freqs: Union[np.ndarray, Sequence[float]],
) -> Tuple[bool, str]:
    """Validate the *n_cycles* parameter used for Morlet wavelet TF analysis.

    Checks
    ------
    * ``n_cycles`` is a positive scalar **or** a 1-D array whose length
      matches ``freqs``.
    * Every element of ``n_cycles`` is > 0.
    * ``freqs`` is a non-empty 1-D array of positive values.

    Parameters
    ----------
    n_cycles : float or array-like
        Number of wavelet cycles (scalar broadcasts to all frequencies).
    freqs : array-like
        Frequency array in Hz.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    # --- freqs ---
    try:
        freqs_arr = np.asarray(freqs, dtype=float)
    except (ValueError, TypeError):
        return False, "freqs must be convertible to a numeric array."

    if freqs_arr.ndim != 1 or freqs_arr.size == 0:
        return False, "freqs must be a non-empty 1-D array."

    if np.any(freqs_arr <= 0):
        return False, "All frequencies must be positive."

    if not np.all(np.isfinite(freqs_arr)):
        return False, "All frequencies must be finite."

    # --- n_cycles ---
    try:
        cycles_arr = np.asarray(n_cycles, dtype=float)
    except (ValueError, TypeError):
        return False, "n_cycles must be convertible to a numeric value or array."

    if cycles_arr.ndim == 0:
        # scalar
        if cycles_arr <= 0 or not np.isfinite(cycles_arr):
            return False, f"n_cycles must be a positive finite number, got {n_cycles}."
    elif cycles_arr.ndim == 1:
        if cycles_arr.size != freqs_arr.size:
            return False, (
                f"When n_cycles is an array it must have the same length as freqs "
                f"({freqs_arr.size}), got {cycles_arr.size}."
            )
        if np.any(cycles_arr <= 0):
            return False, "All n_cycles values must be positive."
        if not np.all(np.isfinite(cycles_arr)):
            return False, "All n_cycles values must be finite."
    else:
        return False, f"n_cycles must be a scalar or 1-D array, got {cycles_arr.ndim}-D."

    return True, ""


# ---------------------------------------------------------------------------
# STFT parameters
# ---------------------------------------------------------------------------

def validate_stft_params(
    window_length: int,
    overlap: int,
    n_samples: int,
) -> Tuple[bool, str]:
    """Validate Short-Time Fourier Transform parameters.

    Checks
    ------
    * All values are positive integers.
    * ``overlap < window_length``.
    * ``window_length <= n_samples``.
    * ``window_length`` is at least 2 (need at least two points for an FFT).

    Parameters
    ----------
    window_length : int
        Length of the STFT window in samples.
    overlap : int
        Overlap between successive windows in samples.
    n_samples : int
        Total number of samples in the signal.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    for name, val in [
        ("window_length", window_length),
        ("overlap", overlap),
        ("n_samples", n_samples),
    ]:
        if not isinstance(val, (int, np.integer)):
            return False, f"{name} must be an integer, got {type(val).__name__}."

    if window_length < 2:
        return False, f"window_length must be >= 2, got {window_length}."

    if overlap < 0:
        return False, f"overlap must be >= 0, got {overlap}."

    if n_samples < 1:
        return False, f"n_samples must be >= 1, got {n_samples}."

    if overlap >= window_length:
        return False, (
            f"overlap ({overlap}) must be strictly less than "
            f"window_length ({window_length})."
        )

    if window_length > n_samples:
        return False, (
            f"window_length ({window_length}) must not exceed "
            f"n_samples ({n_samples})."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Time range
# ---------------------------------------------------------------------------

def validate_time_range(
    tmin: float,
    tmax: float,
    total_duration: float,
) -> Tuple[bool, str]:
    """Validate a time window against the recording duration.

    Checks
    ------
    * ``tmin`` and ``tmax`` are finite numbers.
    * ``tmin >= 0``.
    * ``tmin < tmax``.
    * ``tmax <= total_duration``.
    * ``total_duration > 0``.

    Parameters
    ----------
    tmin : float
        Start time in seconds.
    tmax : float
        End time in seconds.
    total_duration : float
        Total recording duration in seconds.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    for name, val in [("tmin", tmin), ("tmax", tmax), ("total_duration", total_duration)]:
        if not isinstance(val, numbers.Real):
            return False, f"{name} must be a real number, got {type(val).__name__}."
        if not np.isfinite(val):
            return False, f"{name} must be finite, got {val}."

    if total_duration <= 0:
        return False, f"total_duration must be positive, got {total_duration} s."

    if tmin < 0:
        return False, f"tmin must be >= 0, got {tmin} s."

    if tmin >= tmax:
        return False, (
            f"tmin ({tmin} s) must be strictly less than tmax ({tmax} s)."
        )

    if tmax > total_duration:
        return False, (
            f"tmax ({tmax} s) exceeds total duration ({total_duration} s)."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------

def validate_baseline(
    baseline: Tuple[float, float],
    tmin: float,
    tmax: float,
) -> Tuple[bool, str]:
    """Validate a baseline interval against the analysis time window.

    Checks
    ------
    * ``baseline`` is a two-element tuple/list of finite numbers.
    * ``baseline[0] < baseline[1]``.
    * The baseline interval is contained within ``[tmin, tmax]``.

    Parameters
    ----------
    baseline : tuple[float, float]
        ``(start, end)`` of the baseline period in seconds.
    tmin : float
        Start of the analysis window.
    tmax : float
        End of the analysis window.

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    if baseline is None:
        return True, ""  # None means "no baseline correction"

    if not isinstance(baseline, (tuple, list)) or len(baseline) != 2:
        return False, "baseline must be a two-element tuple (start, end) or None."

    bmin, bmax = baseline

    for name, val in [("baseline start", bmin), ("baseline end", bmax)]:
        if not isinstance(val, numbers.Real):
            return False, f"{name} must be a real number, got {type(val).__name__}."
        if not np.isfinite(val):
            return False, f"{name} must be finite, got {val}."

    if bmin >= bmax:
        return False, (
            f"Baseline start ({bmin} s) must be strictly less than "
            f"baseline end ({bmax} s)."
        )

    if bmin < tmin:
        return False, (
            f"Baseline start ({bmin} s) is before the analysis window start "
            f"({tmin} s)."
        )

    if bmax > tmax:
        return False, (
            f"Baseline end ({bmax} s) exceeds the analysis window end "
            f"({tmax} s)."
        )

    return True, ""


# ---------------------------------------------------------------------------
# Channel
# ---------------------------------------------------------------------------

def validate_channel(
    channel: str,
    available_channels: Sequence[str],
) -> Tuple[bool, str]:
    """Validate that a channel name exists in the available channels.

    Parameters
    ----------
    channel : str
        Requested channel name.
    available_channels : sequence of str
        Available channel names (e.g. ``raw.ch_names``).

    Returns
    -------
    (is_valid, message) : tuple[bool, str]
    """
    if not isinstance(channel, str) or not channel.strip():
        return False, "Channel name must be a non-empty string."

    available = list(available_channels)
    if not available:
        return False, "No channels available in the dataset."

    if channel not in available:
        return False, (
            f"Channel '{channel}' not found. "
            f"Available channels: {available}"
        )

    return True, ""


# ---------------------------------------------------------------------------
# Sanitize a full parameter dictionary
# ---------------------------------------------------------------------------

def sanitize_parameters(params_dict: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Sanitize and validate a complete parameter dictionary.

    The function recognises the following optional keys and runs the
    appropriate validator for each one present:

    * ``fmin``, ``fmax``, ``sfreq`` → :func:`validate_frequency_range`
    * ``n_cycles``, ``freqs`` → :func:`validate_wavelet_cycles`
    * ``window_length``, ``overlap``, ``n_samples`` → :func:`validate_stft_params`
    * ``tmin``, ``tmax``, ``total_duration`` → :func:`validate_time_range`
    * ``baseline``, ``tmin``, ``tmax`` → :func:`validate_baseline`
    * ``channel``, ``available_channels`` → :func:`validate_channel`

    Unknown keys are passed through unchanged.

    Parameters
    ----------
    params_dict : dict
        Raw parameters from the user interface.

    Returns
    -------
    (cleaned_params, errors) : tuple[dict, list[str]]
        *cleaned_params* is a copy of *params_dict* with numeric values
        cast to the expected types.  *errors* is a list of error strings
        (empty when everything is valid).
    """
    cleaned: Dict[str, Any] = dict(params_dict)
    errors: List[str] = []

    # --- Numeric type coercion helpers ---
    def _float(key: str) -> float | None:
        val = cleaned.get(key)
        if val is None:
            return None
        try:
            cleaned[key] = float(val)
            return cleaned[key]
        except (ValueError, TypeError):
            errors.append(f"'{key}' must be numeric, got {val!r}.")
            return None

    def _int(key: str) -> int | None:
        val = cleaned.get(key)
        if val is None:
            return None
        try:
            cleaned[key] = int(val)
            return cleaned[key]
        except (ValueError, TypeError):
            errors.append(f"'{key}' must be an integer, got {val!r}.")
            return None

    # --- Coerce common numeric keys ---
    _float("fmin")
    _float("fmax")
    _float("sfreq")
    _float("tmin")
    _float("tmax")
    _float("total_duration")
    _int("window_length")
    _int("overlap")
    _int("n_samples")

    # If coercion produced errors, return early
    if errors:
        return cleaned, errors

    # --- Frequency range ---
    if all(k in cleaned for k in ("fmin", "fmax", "sfreq")):
        ok, msg = validate_frequency_range(cleaned["fmin"], cleaned["fmax"], cleaned["sfreq"])
        if not ok:
            errors.append(msg)

    # --- Wavelet cycles ---
    if "n_cycles" in cleaned and "freqs" in cleaned:
        ok, msg = validate_wavelet_cycles(cleaned["n_cycles"], cleaned["freqs"])
        if not ok:
            errors.append(msg)

    # --- STFT parameters ---
    if all(k in cleaned for k in ("window_length", "overlap", "n_samples")):
        ok, msg = validate_stft_params(
            cleaned["window_length"], cleaned["overlap"], cleaned["n_samples"]
        )
        if not ok:
            errors.append(msg)

    # --- Time range ---
    if all(k in cleaned for k in ("tmin", "tmax", "total_duration")):
        ok, msg = validate_time_range(
            cleaned["tmin"], cleaned["tmax"], cleaned["total_duration"]
        )
        if not ok:
            errors.append(msg)

    # --- Baseline ---
    if "baseline" in cleaned and "tmin" in cleaned and "tmax" in cleaned:
        ok, msg = validate_baseline(cleaned["baseline"], cleaned["tmin"], cleaned["tmax"])
        if not ok:
            errors.append(msg)

    # --- Channel ---
    if "channel" in cleaned and "available_channels" in cleaned:
        ok, msg = validate_channel(cleaned["channel"], cleaned["available_channels"])
        if not ok:
            errors.append(msg)

    return cleaned, errors
