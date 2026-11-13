"""
Test Suite: Time-Frequency Computation Engine
============================================
"""
import pytest
import numpy as np

from core.time_frequency import (
    compute_morlet_tfr,
    compute_multitaper_tfr,
    compute_stft,
    apply_baseline_correction,
    compute_tfr,
)
from core.band_power import compute_band_power, compute_all_band_powers


@pytest.fixture
def synthetic_signal():
    """Create a 4-second test signal with known 10 Hz oscillation."""
    sfreq = 256.0
    duration = 4.0
    t = np.arange(int(duration * sfreq)) / sfreq
    # 10 Hz pure sine wave with small noise
    sig = 10e-6 * np.sin(2 * np.pi * 10 * t) + 1e-6 * np.random.randn(len(t))
    return sig, sfreq, t


def test_morlet_wavelet_computation(synthetic_signal):
    """Verify Morlet Wavelet decomposition outputs valid shapes and finite power."""
    sig, sfreq, _ = synthetic_signal
    n_freqs = 20
    fmin, fmax = 4.0, 30.0
    
    power, freqs, times = compute_morlet_tfr(
        sig, sfreq=sfreq, fmin=fmin, fmax=fmax, n_freqs=n_freqs, n_cycles=5.0
    )
    
    assert power.shape[0] == n_freqs, f"Expected {n_freqs} frequency bins, got {power.shape[0]}"
    assert power.shape[1] == len(sig), f"Expected {len(sig)} temporal points, got {power.shape[1]}"
    assert len(freqs) == n_freqs
    assert len(times) == len(sig)
    assert np.all(np.isfinite(power)), "Power values must be finite (no NaNs or Infs)"
    assert np.all(power >= 0), "Raw power values must be non-negative"
    
    # Check that 10 Hz peak has higher power than 25 Hz
    idx_10hz = np.argmin(np.abs(freqs - 10.0))
    idx_25hz = np.argmin(np.abs(freqs - 25.0))
    assert np.mean(power[idx_10hz]) > np.mean(power[idx_25hz]) * 2, "Expected 10 Hz power peak"


def test_multitaper_computation(synthetic_signal):
    """Verify Multitaper method outputs valid dimensions and spectral content."""
    sig, sfreq, _ = synthetic_signal
    n_freqs = 15
    fmin, fmax = 5.0, 35.0
    
    power, freqs, times = compute_multitaper_tfr(
        sig, sfreq=sfreq, fmin=fmin, fmax=fmax, n_freqs=n_freqs, time_bandwidth=4.0
    )
    
    assert power.shape[0] == n_freqs
    assert power.shape[1] == len(sig)
    assert np.all(np.isfinite(power))
    assert np.all(power >= 0)


def test_stft_computation(synthetic_signal):
    """Verify SciPy STFT calculation produces valid frequencies and time points."""
    sig, sfreq, _ = synthetic_signal
    window_length = 128
    overlap = 64
    fmin, fmax = 2.0, 40.0
    
    power, freqs, times = compute_stft(
        sig, sfreq=sfreq, window_length=window_length, overlap=overlap, fmin=fmin, fmax=fmax
    )
    
    assert power.ndim == 2
    assert len(freqs) == power.shape[0]
    assert len(times) == power.shape[1]
    assert np.all(freqs >= fmin) and np.all(freqs <= fmax)
    assert np.all(np.isfinite(power))
    assert np.all(power >= 0)


def test_baseline_correction_modes():
    """Verify all baseline correction modes (mean, ratio, db, percent, zscore)."""
    n_freqs = 5
    n_times = 100
    times = np.linspace(0.0, 5.0, n_times)
    # Power is 1.0 during baseline (0-1s), 4.0 after
    power = np.ones((n_freqs, n_times))
    power[:, times > 1.0] = 4.0
    baseline = (0.0, 1.0)
    
    # 1. Mean subtraction
    corr_mean = apply_baseline_correction(power, times, baseline=baseline, mode='mean')
    assert np.allclose(corr_mean[:, times <= 1.0], 0.0, atol=1e-5)
    assert np.allclose(corr_mean[:, times > 1.0], 3.0, atol=1e-5)
    
    # 2. Ratio
    corr_ratio = apply_baseline_correction(power, times, baseline=baseline, mode='ratio')
    assert np.allclose(corr_ratio[:, times <= 1.0], 1.0, atol=1e-5)
    assert np.allclose(corr_ratio[:, times > 1.0], 4.0, atol=1e-5)
    
    # 3. Decibel (10 * log10(power / base)) -> 10 * log10(4) ≈ 6.02 dB
    corr_db = apply_baseline_correction(power, times, baseline=baseline, mode='db')
    assert np.allclose(corr_db[:, times <= 1.0], 0.0, atol=1e-5)
    assert np.allclose(corr_db[:, times > 1.0], 10 * np.log10(4.0), atol=1e-5)
    
    # 4. Percent change ((power - base) / base * 100) -> 300%
    corr_pct = apply_baseline_correction(power, times, baseline=baseline, mode='percent')
    assert np.allclose(corr_pct[:, times <= 1.0], 0.0, atol=1e-5)
    assert np.allclose(corr_pct[:, times > 1.0], 300.0, atol=1e-5)


def test_compute_band_power():
    """Verify frequency band power calculation."""
    freqs = np.linspace(1.0, 40.0, 40)  # 1 Hz spacing
    times = np.linspace(0.0, 2.0, 50)
    power = np.ones((len(freqs), len(times)))
    
    # Set 10 Hz (Alpha band 8-13 Hz) to high power
    alpha_mask = (freqs >= 8.0) & (freqs <= 13.0)
    power[alpha_mask] = 10.0
    
    alpha_power = compute_band_power(power, freqs, band_name='Alpha')
    assert len(alpha_power) == len(times)
    assert np.allclose(alpha_power, 10.0)
    
    all_bands = compute_all_band_powers(power, freqs)
    assert 'Delta' in all_bands
    assert 'Alpha' in all_bands
    assert 'Beta' in all_bands
