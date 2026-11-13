"""
Synthetic EEG data generators for educational demonstrations.

All generators use deterministic random seeds so that outputs are fully
reproducible across sessions and platforms.
"""

from __future__ import annotations

import numpy as np
import mne


# ---------------------------------------------------------------------------
# Main sample dataset – Alpha-blocking paradigm
# ---------------------------------------------------------------------------

def generate_sample_eeg(
    duration: float = 30.0,
    sfreq: float = 256.0,
    random_seed: int = 42,
) -> mne.io.RawArray:
    """Generate a synthetic multi-channel EEG dataset for educational purposes.

    Creates realistic-looking EEG with:

    * **Channels**: Fz, Cz, C3, C4, Pz, Oz, O1, O2, T7, T8
    * **Alpha** (10 Hz) oscillation prominent at Oz, O1, O2
    * **Alpha blocking**: first 10 s eyes-closed (strong alpha),
      10–20 s eyes-open (reduced alpha), 20–30 s eyes-closed again
    * **Beta** (20 Hz) activity at C3, C4
    * **Theta** (6 Hz) at Fz
    * **1/f pink noise** background on all channels
    * Event annotations at 0 s (eyes_closed), 10 s (eyes_open),
      20 s (eyes_closed)

    Parameters
    ----------
    duration : float
        Total duration in seconds (default 30).
    sfreq : float
        Sampling frequency in Hz (default 256).
    random_seed : int
        Seed for the NumPy random number generator.

    Returns
    -------
    raw : mne.io.RawArray
        Continuous EEG data with annotations.
    """
    np.random.seed(random_seed)
    n_samples = int(duration * sfreq)
    t = np.arange(n_samples) / sfreq

    ch_names = ["Fz", "Cz", "C3", "C4", "Pz", "Oz", "O1", "O2", "T7", "T8"]
    n_channels = len(ch_names)

    # ------------------------------------------------------------------
    # 1/f pink noise background for every channel
    # ------------------------------------------------------------------
    data = np.zeros((n_channels, n_samples))
    for i in range(n_channels):
        white = np.random.randn(n_samples)
        freqs_fft = np.fft.rfftfreq(n_samples, d=1.0 / sfreq)
        freqs_fft[0] = 1.0  # avoid division by zero
        pink_filter = 1.0 / np.sqrt(freqs_fft)
        white_fft = np.fft.rfft(white)
        pink = np.fft.irfft(white_fft * pink_filter, n=n_samples)
        data[i] = pink * 5e-6  # Scale to ~5 µV

    # ------------------------------------------------------------------
    # Alpha oscillation (10 Hz) – modulated by eyes open / closed
    # ------------------------------------------------------------------
    alpha_envelope = np.ones(n_samples)
    eyes_open_start = int(10.0 * sfreq)
    eyes_open_end = int(20.0 * sfreq)
    alpha_envelope[eyes_open_start:eyes_open_end] = 0.2  # Alpha blocking

    alpha_signal = alpha_envelope * np.sin(2 * np.pi * 10 * t) * 15e-6

    # Occipital channels: Oz (idx 5), O1 (idx 6), O2 (idx 7)
    for idx in [5, 6, 7]:
        data[idx] += alpha_signal * (1.0 if idx == 5 else 0.7)
    # Smaller alpha propagation at Pz (idx 4)
    data[4] += alpha_signal * 0.3

    # ------------------------------------------------------------------
    # Beta (20 Hz) & mu (10 Hz) at C3, C4 – motor cortex
    # ------------------------------------------------------------------
    beta_signal = np.sin(2 * np.pi * 20 * t) * 5e-6

    mu_envelope = np.ones(n_samples)
    mu_envelope[eyes_open_start:eyes_open_end] = 0.4  # Simulated motor-imagery ERD
    mu_signal = mu_envelope * np.sin(2 * np.pi * 10 * t) * 8e-6

    data[2] += beta_signal + mu_signal        # C3
    data[3] += beta_signal * 0.8 + mu_signal * 0.8  # C4

    # ------------------------------------------------------------------
    # Theta (6 Hz) at Fz
    # ------------------------------------------------------------------
    theta_signal = np.sin(2 * np.pi * 6 * t) * 8e-6
    data[0] += theta_signal
    data[1] += theta_signal * 0.5

    # ------------------------------------------------------------------
    # Build MNE RawArray
    # ------------------------------------------------------------------
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    try:
        info.set_montage("standard_1020", on_missing="ignore")
    except Exception:
        pass
    raw = mne.io.RawArray(data, info, verbose=False)

    # Dynamic annotations that fit the requested duration
    seg_dur = duration / 3.0
    raw.set_annotations(
        mne.Annotations(
            onset=[0.0, seg_dur, 2 * seg_dur],
            duration=[seg_dur, seg_dur, max(0.01, duration - 2 * seg_dur)],
            description=["eyes_closed", "eyes_open", "eyes_closed"],
        )
    )

    return raw


# ---------------------------------------------------------------------------
# Metadata helper
# ---------------------------------------------------------------------------

def get_sample_data_info() -> dict:
    """Return metadata about the sample dataset.

    Returns
    -------
    info : dict
        Human-readable metadata dictionary.
    """
    return {
        "name": "Simulated EEG – Alpha Blocking Paradigm",
        "description": (
            "Synthetic multi-channel EEG demonstrating alpha blocking. "
            "Contains 30 seconds of simulated data with eyes-closed (0–10 s), "
            "eyes-open (10–20 s), and eyes-closed (20–30 s) conditions. "
            "Alpha (10 Hz) oscillations are prominent at occipital channels "
            "during eyes-closed conditions and suppressed during eyes-open."
        ),
        "channels": ["Fz", "Cz", "C3", "C4", "Pz", "Oz", "O1", "O2", "T7", "T8"],
        "sfreq": 256.0,
        "duration": 30.0,
        "n_samples": 7680,
        "conditions": ["eyes_closed", "eyes_open", "eyes_closed"],
        "is_synthetic": True,
        "source": "Generated using NumPy with deterministic seed for reproducibility",
        "frequency_content": {
            "alpha": "10 Hz at Oz, O1, O2 (modulated by condition)",
            "beta": "20 Hz at C3, C4",
            "theta": "6 Hz at Fz",
            "background": "1/f pink noise on all channels",
        },
    }


# ---------------------------------------------------------------------------
# Motor-imagery dataset
# ---------------------------------------------------------------------------

def generate_motor_imagery_data(
    duration: float = 20.0,
    sfreq: float = 256.0,
    random_seed: int = 123,
) -> mne.io.RawArray:
    """Generate synthetic EEG for motor imagery demonstration.

    Simulates:

    * **Rest** (0–5 s): baseline mu and beta rhythms at C3, C4.
    * **Left-hand imagery** (5–10 s): ERD at C3 (contralateral),
      slight ERS at C4.
    * **Rest** (10–15 s): recovery.
    * **Right-hand imagery** (15–20 s): ERD at C4, slight ERS at C3.

    Parameters
    ----------
    duration : float
        Total duration in seconds (default 20).
    sfreq : float
        Sampling frequency in Hz (default 256).
    random_seed : int
        Seed for the NumPy random number generator.

    Returns
    -------
    raw : mne.io.RawArray
        Continuous EEG data with annotations.
    """
    np.random.seed(random_seed)
    n_samples = int(duration * sfreq)
    t = np.arange(n_samples) / sfreq

    ch_names = ["Fz", "Cz", "C3", "C4", "Pz", "Oz"]
    n_channels = len(ch_names)

    # ------------------------------------------------------------------
    # Pink noise background
    # ------------------------------------------------------------------
    data = np.zeros((n_channels, n_samples))
    for i in range(n_channels):
        white = np.random.randn(n_samples)
        freqs_fft = np.fft.rfftfreq(n_samples, d=1.0 / sfreq)
        freqs_fft[0] = 1.0
        pink_filter = 1.0 / np.sqrt(freqs_fft)
        white_fft = np.fft.rfft(white)
        pink = np.fft.irfft(white_fft * pink_filter, n=n_samples)
        data[i] = pink * 5e-6

    # ------------------------------------------------------------------
    # Mu-rhythm envelopes for C3 / C4
    # ------------------------------------------------------------------
    mu_c3 = np.ones(n_samples)
    mu_c3[int(5 * sfreq) : int(10 * sfreq)] = 0.3   # Left MI → ERD at C3
    mu_c3[int(15 * sfreq) : int(20 * sfreq)] = 1.3   # Right MI → slight ERS at C3

    mu_c4 = np.ones(n_samples)
    mu_c4[int(5 * sfreq) : int(10 * sfreq)] = 1.3    # Left MI → slight ERS at C4
    mu_c4[int(15 * sfreq) : int(20 * sfreq)] = 0.3   # Right MI → ERD at C4

    mu_signal = np.sin(2 * np.pi * 11 * t) * 10e-6
    beta_signal = np.sin(2 * np.pi * 22 * t) * 4e-6

    data[2] += mu_c3 * mu_signal + mu_c3 * beta_signal  # C3
    data[3] += mu_c4 * mu_signal + mu_c4 * beta_signal  # C4

    # Tonic alpha at Oz
    data[5] += np.sin(2 * np.pi * 10 * t) * 12e-6

    # ------------------------------------------------------------------
    # Build MNE RawArray
    # ------------------------------------------------------------------
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types="eeg")
    try:
        info.set_montage("standard_1020", on_missing="ignore")
    except Exception:
        pass
    raw = mne.io.RawArray(data, info, verbose=False)

    seg_dur = duration / 4.0
    raw.set_annotations(
        mne.Annotations(
            onset=[0.0, seg_dur, 2 * seg_dur, 3 * seg_dur],
            duration=[seg_dur, seg_dur, seg_dur, max(0.01, duration - 3 * seg_dur)],
            description=["rest", "left_hand_mi", "rest", "right_hand_mi"],
        )
    )

    return raw
