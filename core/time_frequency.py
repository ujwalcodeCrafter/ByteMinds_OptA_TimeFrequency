"""
Time-Frequency Analysis Engine.

Implements three methods:
1. Morlet Wavelet Transform (via MNE)
2. Multitaper Method (via MNE) 
3. Short-Time Fourier Transform (via SciPy)

All methods return consistent output format:
    power: np.ndarray of shape (n_freqs, n_times)
    freqs: np.ndarray of frequency values
    times: np.ndarray of time values
"""

import numpy as np
from scipy import signal as scipy_signal
import mne
from mne.time_frequency import tfr_array_morlet, tfr_array_multitaper


def compute_morlet_tfr(data, sfreq, freqs=None, n_cycles=7.0, 
                       fmin=1.0, fmax=40.0, n_freqs=30,
                       output='power', decim=1, tstart=0.0, **kwargs):
    """
    Compute Morlet wavelet time-frequency representation.
    
    Parameters
    ----------
    data : np.ndarray, shape (n_times,)
        Single-channel EEG time series.
    sfreq : float
        Sampling frequency in Hz.
    freqs : np.ndarray, optional
        Specific frequency values. If None, computed from fmin/fmax/n_freqs.
    n_cycles : float or np.ndarray
        Number of wavelet cycles. More cycles = better frequency resolution,
        worse temporal resolution.
    fmin, fmax : float
        Frequency range limits.
    n_freqs : int
        Number of frequency points.
    output : str
        'power' or 'complex'
    decim : int or 'auto'
        Decimation factor for time points. Use 'auto' for fast responsive visualization.
    tstart : float
        Start timestamp in seconds (default 0.0).
        
    Returns
    -------
    power : np.ndarray, shape (n_freqs, n_times)
    freqs : np.ndarray, shape (n_freqs,)
    times : np.ndarray, shape (n_times,)
    """
    if freqs is None:
        freqs = np.linspace(fmin, fmax, n_freqs)
    
    if decim == 'auto':
        # Target ~500-750 points for fast, smooth interactive browser rendering
        decim_val = max(1, len(data) // 600)
    else:
        decim_val = max(1, int(decim))
    
    # Reshape for MNE: (n_epochs, n_channels, n_times)
    data_3d = data.reshape(1, 1, -1)
    
    # Compute TFR
    tfr = tfr_array_morlet(data_3d, sfreq=sfreq, freqs=freqs,
                           n_cycles=n_cycles, output=output, 
                           decim=decim_val, verbose=False)
    
    # tfr shape: (n_epochs, n_channels, n_freqs, n_times)
    power = np.abs(tfr[0, 0]) ** 2 if output == 'complex' else tfr[0, 0]
    
    n_times_out = power.shape[1]
    times = np.linspace(tstart, tstart + len(data) / sfreq, n_times_out)
    
    return power, freqs, times


def compute_multitaper_tfr(data, sfreq, freqs=None,
                           fmin=1.0, fmax=40.0, n_freqs=30,
                           time_bandwidth=4.0, decim=1, tstart=0.0, **kwargs):
    """
    Compute multitaper time-frequency representation.
    
    The multitaper method uses multiple orthogonal tapers (DPSS windows)
    to estimate spectral power with controlled smoothing.
    
    Parameters
    ----------
    data : np.ndarray, shape (n_times,)
    sfreq : float
    freqs : np.ndarray, optional
    fmin, fmax : float
    n_freqs : int
    time_bandwidth : float
        Time x bandwidth product. Controls frequency smoothing.
        Higher values = more smoothing = lower variance estimates.
    decim : int or 'auto'
    tstart : float
        
    Returns
    -------
    power : np.ndarray, shape (n_freqs, n_times)
    freqs : np.ndarray
    times : np.ndarray
    """
    if freqs is None:
        freqs = np.linspace(fmin, fmax, n_freqs)
    
    if decim == 'auto':
        decim_val = max(1, len(data) // 600)
    else:
        decim_val = max(1, int(decim))
    
    data_3d = data.reshape(1, 1, -1)
    
    # n_cycles for multitaper: use freqs / 2 as a reasonable default
    # that provides good frequency resolution
    n_cycles = freqs / 2.0
    n_cycles = np.maximum(n_cycles, 1.0)  # At least 1 cycle
    
    tfr = tfr_array_multitaper(data_3d, sfreq=sfreq, freqs=freqs,
                                n_cycles=n_cycles,
                                time_bandwidth=time_bandwidth,
                                output='power', decim=decim_val,
                                verbose=False)
    
    power = tfr[0, 0]  # (n_freqs, n_times)
    n_times_out = power.shape[1]
    times = np.linspace(tstart, tstart + len(data) / sfreq, n_times_out)
    
    return power, freqs, times


def compute_stft(data, sfreq, window_length=256, overlap=None,
                 fmin=0.0, fmax=None, window='hann', tstart=0.0, **kwargs):
    """
    Compute Short-Time Fourier Transform.
    
    STFT uses a sliding window to compute local spectra, providing
    a fixed time-frequency resolution determined by window length.
    
    Parameters
    ----------
    data : np.ndarray, shape (n_times,)
    sfreq : float
    window_length : int
        Length of each segment in samples.
    overlap : int, optional
        Number of overlapping samples. Default: window_length // 2.
    fmin, fmax : float
        Frequency range to return.
    window : str
        Window function name (e.g., 'hann', 'hamming', 'blackman').
    tstart : float
        Start timestamp in seconds.
        
    Returns
    -------
    power : np.ndarray, shape (n_freqs, n_times)
    freqs : np.ndarray
    times : np.ndarray
    """
    if len(data) < 2:
        raise ValueError("Signal too short for STFT analysis.")
        
    window_length = max(2, min(int(window_length), len(data)))
    
    if overlap is None:
        overlap = window_length // 2
    else:
        overlap = max(0, min(int(overlap), window_length - 1))
    
    if fmax is None:
        fmax = sfreq / 2
    
    # Compute STFT using scipy with proper PSD scaling
    f, t, Zxx = scipy_signal.stft(data, fs=sfreq, window=window,
                                   nperseg=window_length, 
                                   noverlap=overlap,
                                   scaling='psd')
    
    # Compute power spectral density
    power = np.abs(Zxx) ** 2
    
    # Apply frequency limits
    freq_mask = (f >= fmin) & (f <= fmax)
    if not np.any(freq_mask):
        freq_mask = np.ones(len(f), dtype=bool)
        
    power = power[freq_mask]
    f = f[freq_mask]
    
    return power, f, t + tstart


def apply_baseline_correction(power, times, baseline=None, mode='mean'):
    """
    Apply baseline correction to power data.
    
    Parameters
    ----------
    power : np.ndarray, shape (n_freqs, n_times)
    times : np.ndarray, shape (n_times,)
    baseline : tuple (tmin, tmax) or None
        Time interval for baseline. None = no correction.
    mode : str
        'mean': subtract mean baseline power
        'ratio': divide by mean baseline power
        'logratio': log10 of ratio
        'percent': percentage change from baseline
        'zscore': z-score relative to baseline
        'db': 10 * log10(power / baseline_mean) - decibel scale
        
    Returns
    -------
    power_corrected : np.ndarray
    """
    if baseline is None:
        return power.copy()
    
    bmin, bmax = baseline
    baseline_mask = (times >= bmin) & (times <= bmax)
    
    if not np.any(baseline_mask):
        # If no time points in baseline, return uncorrected
        return power.copy()
    
    baseline_power = power[:, baseline_mask].mean(axis=1, keepdims=True)
    
    # Avoid division by zero
    baseline_power = np.maximum(baseline_power, np.finfo(float).eps)
    
    if mode == 'mean':
        return power - baseline_power
    elif mode == 'ratio':
        return power / baseline_power
    elif mode == 'logratio':
        return np.log10(power / baseline_power)
    elif mode == 'percent':
        return (power - baseline_power) / baseline_power * 100
    elif mode == 'zscore':
        baseline_std = power[:, baseline_mask].std(axis=1, keepdims=True)
        baseline_std = np.maximum(baseline_std, np.finfo(float).eps)
        return (power - baseline_power) / baseline_std
    elif mode == 'db':
        return 10 * np.log10(power / baseline_power)
    else:
        raise ValueError(f"Unknown baseline mode: {mode}. Use 'mean', 'ratio', 'logratio', 'percent', 'zscore', or 'db'.")


def compute_tfr(data, sfreq, method='morlet', **kwargs):
    """
    Unified interface for time-frequency computation.
    
    Parameters
    ----------
    data : np.ndarray, shape (n_times,)
    sfreq : float
    method : str
        'morlet', 'multitaper', or 'stft'
    **kwargs : dict
        Method-specific parameters
        
    Returns
    -------
    power, freqs, times : np.ndarrays
    """
    if method == 'morlet':
        return compute_morlet_tfr(data, sfreq, **kwargs)
    elif method == 'multitaper':
        return compute_multitaper_tfr(data, sfreq, **kwargs)
    elif method == 'stft':
        return compute_stft(data, sfreq, **kwargs)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'morlet', 'multitaper', or 'stft'.")
