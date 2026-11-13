"""
Test Suite: Parameter Validation and Edge Case Handling
========================================================
"""
import pytest
import numpy as np

from core.validation import (
    validate_frequency_range,
    validate_wavelet_cycles,
    validate_stft_params,
    validate_time_range,
    validate_baseline,
    validate_channel,
    sanitize_parameters,
)


def test_frequency_range_validation():
    """Verify frequency limits and Nyquist constraint enforcement."""
    # Valid range
    valid, msg = validate_frequency_range(fmin=1.0, fmax=40.0, sfreq=256.0)
    assert valid is True
    assert msg == ""
    
    # fmin >= fmax
    valid, msg = validate_frequency_range(fmin=40.0, fmax=10.0, sfreq=256.0)
    assert valid is False
    assert "strictly less" in msg
    
    # fmin == fmax
    valid, msg = validate_frequency_range(fmin=10.0, fmax=10.0, sfreq=256.0)
    assert valid is False
    
    # fmax exceeds Nyquist limit (256/2 = 128)
    valid, msg = validate_frequency_range(fmin=1.0, fmax=130.0, sfreq=256.0)
    assert valid is False
    assert "Nyquist" in msg
    
    # Negative / zero fmin
    valid, msg = validate_frequency_range(fmin=0.0, fmax=30.0, sfreq=256.0)
    assert valid is False


def test_wavelet_cycles_validation():
    """Verify Morlet wavelet cycles validation."""
    freqs = np.linspace(4.0, 30.0, 10)
    
    # Valid positive scalar
    valid, msg = validate_wavelet_cycles(n_cycles=7.0, freqs=freqs)
    assert valid is True
    
    # Negative cycles
    valid, msg = validate_wavelet_cycles(n_cycles=-3.0, freqs=freqs)
    assert valid is False
    assert "positive" in msg
    
    # Zero cycles
    valid, msg = validate_wavelet_cycles(n_cycles=0.0, freqs=freqs)
    assert valid is False
    
    # Valid matching array
    cycles_arr = freqs / 2.0
    valid, msg = validate_wavelet_cycles(n_cycles=cycles_arr, freqs=freqs)
    assert valid is True
    
    # Mismatched array length
    valid, msg = validate_wavelet_cycles(n_cycles=np.ones(5), freqs=freqs)
    assert valid is False


def test_stft_params_validation():
    """Verify STFT window length, overlap, and sample size constraints."""
    # Valid configuration
    valid, msg = validate_stft_params(window_length=256, overlap=128, n_samples=1000)
    assert valid is True
    
    # Overlap >= window_length
    valid, msg = validate_stft_params(window_length=256, overlap=256, n_samples=1000)
    assert valid is False
    assert "strictly less" in msg
    
    valid, msg = validate_stft_params(window_length=256, overlap=300, n_samples=1000)
    assert valid is False
    
    # Window length > total signal samples
    valid, msg = validate_stft_params(window_length=2000, overlap=100, n_samples=1000)
    assert valid is False
    assert "exceed" in msg
    
    # Negative overlap
    valid, msg = validate_stft_params(window_length=256, overlap=-10, n_samples=1000)
    assert valid is False


def test_time_range_validation():
    """Verify time interval bounds checking."""
    # Valid interval
    valid, msg = validate_time_range(tmin=0.0, tmax=10.0, total_duration=30.0)
    assert valid is True
    
    # tmin >= tmax
    valid, msg = validate_time_range(tmin=15.0, tmax=10.0, total_duration=30.0)
    assert valid is False
    
    # tmax > total_duration
    valid, msg = validate_time_range(tmin=0.0, tmax=35.0, total_duration=30.0)
    assert valid is False
    
    # Negative tmin
    valid, msg = validate_time_range(tmin=-2.0, tmax=10.0, total_duration=30.0)
    assert valid is False


def test_channel_validation():
    """Verify channel lookup in available channel lists."""
    channels = ['Fz', 'Cz', 'C3', 'C4', 'Oz']
    
    valid, msg = validate_channel('Oz', channels)
    assert valid is True
    
    valid, msg = validate_channel('InvalidChannel', channels)
    assert valid is False
    assert "not found" in msg


def test_sanitize_parameters():
    """Verify comprehensive dictionary sanitization."""
    raw_params = {
        'channel': 'Oz',
        'available_channels': ['Oz', 'Cz'],
        'sfreq': '256.0',
        'fmin': '2.0',
        'fmax': '40.0',
        'method': 'morlet',
        'n_cycles': '7.0',
        'freqs': np.linspace(2.0, 40.0, 20),
    }
    
    cleaned, errors = sanitize_parameters(raw_params)
    assert len(errors) == 0
    assert isinstance(cleaned['sfreq'], float)
    assert isinstance(cleaned['fmin'], float)
    assert isinstance(cleaned['fmax'], float)
    assert cleaned['channel'] == 'Oz'
