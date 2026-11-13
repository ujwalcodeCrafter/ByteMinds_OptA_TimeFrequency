"""
EEG Frequency Band Power Analysis.

Computes power in standard EEG frequency bands from time-frequency data.
"""

import numpy as np

# Standard EEG frequency bands
FREQUENCY_BANDS = {
    'Delta': (0.5, 4.0),
    'Theta': (4.0, 8.0),
    'Alpha': (8.0, 13.0),
    'Beta': (13.0, 30.0),
    'Gamma': (30.0, 100.0),
}

BAND_COLORS = {
    'Delta': '#FF6B6B',
    'Theta': '#FFA94D',
    'Alpha': '#51CF66',
    'Beta': '#339AF0',
    'Gamma': '#CC5DE8',
}

BAND_DESCRIPTIONS = {
    'Delta': {
        'range': '0.5–4 Hz',
        'states': 'Deep sleep, unconscious states',
        'note': 'Dominant during deep sleep stages (N3). High amplitude, low frequency.',
    },
    'Theta': {
        'range': '4–8 Hz',
        'states': 'Drowsiness, light sleep, meditation, memory tasks',
        'note': 'Associated with memory encoding and creative thinking.',
    },
    'Alpha': {
        'range': '8–13 Hz',
        'states': 'Relaxed wakefulness, eyes closed, meditation',
        'note': 'Prominent over occipital regions when eyes are closed (alpha rhythm). Suppressed when eyes open (alpha blocking).',
    },
    'Beta': {
        'range': '13–30 Hz',
        'states': 'Active thinking, focus, alertness, motor planning',
        'note': 'Dominant during active cognitive and motor tasks. Includes mu rhythm (~10-12 Hz) over motor cortex.',
    },
    'Gamma': {
        'range': '30–100 Hz',
        'states': 'Higher cognitive processing, perception, consciousness',
        'note': 'Associated with binding of different sensory inputs and high-level information processing.',
    },
}


def compute_band_power(power, freqs, band_name=None, fmin=None, fmax=None):
    """
    Compute mean power within a frequency band for each time point.
    
    Parameters
    ----------
    power : np.ndarray, shape (n_freqs, n_times)
    freqs : np.ndarray, shape (n_freqs,)
    band_name : str, optional
        Name from FREQUENCY_BANDS dict.
    fmin, fmax : float, optional
        Custom frequency range. Used if band_name is None.
        
    Returns
    -------
    band_power : np.ndarray, shape (n_times,)
        Mean power in the band at each time point.
    """
    if band_name is not None:
        if band_name not in FREQUENCY_BANDS:
            raise ValueError(f"Unknown band: {band_name}. Available: {list(FREQUENCY_BANDS.keys())}")
        fmin, fmax = FREQUENCY_BANDS[band_name]
    
    if fmin is None or fmax is None:
        raise ValueError("Provide either band_name or both fmin and fmax.")
    
    freq_mask = (freqs >= fmin) & (freqs <= fmax)
    
    if not np.any(freq_mask):
        return np.zeros(power.shape[1])
    
    band_power = power[freq_mask].mean(axis=0)
    return band_power


def compute_all_band_powers(power, freqs):
    """
    Compute power for all standard EEG bands.
    
    Returns
    -------
    band_powers : dict
        {band_name: np.ndarray of shape (n_times,)}
    """
    band_powers = {}
    for band_name in FREQUENCY_BANDS:
        fmin, fmax = FREQUENCY_BANDS[band_name]
        # Only compute if frequencies cover this band
        if freqs[-1] >= fmin and freqs[0] <= fmax:
            band_powers[band_name] = compute_band_power(power, freqs, band_name=band_name)
    return band_powers


def compute_band_power_ratio(power, freqs, band1, band2):
    """Compute power ratio between two bands (band1 / band2)."""
    p1 = compute_band_power(power, freqs, band_name=band1).mean()
    p2 = compute_band_power(power, freqs, band_name=band2).mean()
    if p2 == 0:
        return float('inf')
    return p1 / p2
