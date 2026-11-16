# Time-Frequency Analysis — Developer & Integration Guide

Intended audience: This guide is for developers, instructors, and team members who would like to contribute to or include this code within the other modules used in the BCI course pipeline (Classification, SpatialAnalysis, Epoching, Filtering, etc.)

---

## Architecture and Design Principles

The codebase is organized around a strict separation between computational signal processing and the user interface:

- **`core/` (Scientific Signal Processing):** Generic Python functions that return and take in Python types, MNE data structures, or NumPy arrays. Because there are no Streamlit imports in `core/`, this code can be used in a Jupyter notebook, a command line, or any other offline processing (without starting the web server).
- **`components/` (Presentation & Widgets):** Cards, forms, Plotly graph generators, and other Streamlit UI elements.
- **`app.py` (Application Orchestrator):** Routes between pages, manages session state, invokes  `core/` functions based on user input, and sends data to `components/` for display.


```text
       Streamlit Frontend (Browser)
                    │
            components/ (Plotly, UI)
                    │
               app.py (State & Routing)
                    │
    ┌───────────────┴───────────────┐
    ▼                               ▼
core/time_frequency.py          core/data_loader.py
core/sample_data.py             core/preprocessing.py
core/band_power.py              core/validation.py
core/export_utils.py
```

---

## Core Module API Reference

### 1. Time-Frequency Engine (`core/time_frequency.py`)

This module performs the actual mathematical transformations:

- `compute_morlet_tfr(data, sfreq, freqs=None, n_cycles=7.0, fmin=1.0, fmax=40.0, n_freqs=30, output='power', decim=1)`:
  - Wraps MNE's `mne.time_frequency.tfr_array_morlet`.
  - Reshapes 1D channel data into `(1, 1, n_times)`, computes the complex Morlet wavelets, extracts power as the squared magnitude, and returns `(power, freqs, times)`.
  - The `decim` parameter enables temporal downsampling when processing long recordings to preserve rendering speed.

- `compute_multitaper_tfr(data, sfreq, freqs=None, fmin=1.0, fmax=40.0, n_freqs=30, time_bandwidth=4.0, decim=1)`:
  - Wraps `mne.time_frequency.tfr_array_multitaper` using DPSS (Discrete Prolate Spheroidal Sequences) tapers.
  - Frequency cycles adaptively scale as `n_cycles = freqs / 2.0`.
  - Returns `(power, freqs, times)`.

- `compute_stft(data, sfreq, window_length=256, overlap=None, fmin=0.0, fmax=None, window='hann')`:
  - Uses `scipy.signal.stft` to calculate windowed Fourier power.
  - Computes power as $|Z_{xx}|^2$.
  - Returns `(power, freqs, times)`.

- `apply_baseline_correction(power, times, baseline=None, mode='mean')`:
  - Normalizes a 2D power array against a baseline time window $[t_{start}, t_{end}]$.
  - Supported modes: `'mean'` (additive), `'ratio'`, `'logratio'`, `'percent'`, `'zscore'`, and `'db'` ($10 \log_{10}(P / P_{base})$).
  - Includes a floating-point epsilon safeguard (`np.finfo(float).eps`) to prevent division by zero or log of zero.

- `compute_tfr(data, sfreq, method='morlet', **kwargs)`:
  - Unified dispatcher function that routes requests to `compute_morlet_tfr`, `compute_multitaper_tfr`, or `compute_stft` based on the `method` argument.

---

### 2. Data Loading & Parsers (`core/data_loader.py`)

- `load_eeg_file(file_path_or_buffer, file_type=None, **kwargs)`:
  - Detects and loads `.edf`, `.fif`, `.vhdr`, `.set`, or `.csv` files into an `mne.io.Raw` object.
  - Returns a tuple of `(raw_instance, metadata_dict)`.
- `extract_data_info(raw)`:
  - Extracts key recording metadata: channel count, channel names, sampling rate ($s_{freq}$), sample count, duration in seconds, event annotations, and channel types.

---

### 3. Benchmark Generators (`core/sample_data.py`)

- `generate_sample_eeg(duration=30.0, sfreq=256.0, random_seed=42)`:
  - Produces a 10-channel synthetic EEG recording with realistic $1/f$ pink noise and simulated occipital alpha waves (10 Hz).
  - Includes event annotations for `eyes_closed` (0–10s), `eyes_open` (10–20s), and `eyes_closed` (20–30s).
- `generate_motor_imagery_data(duration=20.0, sfreq=256.0, random_seed=123)`:
  - Produces a 6-channel sensorimotor benchmark with contralateral mu (11 Hz) and beta (22 Hz) Event-Related Desynchronization (ERD) at electrodes `C3` and `C4`.

---

### 4. Input Validation & Safety Clamps (`core/validation.py`)

All user inputs from the UI pass through validation routines before reaching numerical processing:
- `validate_frequency_range(fmin, fmax, sfreq)`: Ensures $0 < f_{min} < f_{max} \le f_s / 2$ (Nyquist boundary).
- `validate_wavelet_cycles(n_cycles, freqs)`: Enforces positive cycle limits and ensures wavelets fit within the data buffer.
- `validate_stft_params(window_length, overlap, n_samples)`: Ensures window length does not exceed sample length and that overlap is strictly less than window length.
- `validate_time_range(tmin, tmax, total_duration)`: Verifies timestamps remain within file bounds.
- `sanitize_parameters(params_dict)`: Cleans and provides safe defaults for all incoming UI controls.

---

### 5. Export Utilities (`core/export_utils.py`)

- `export_parameters_json(params)`: Serializes analysis metadata and parameter settings to formatted JSON.
- `generate_python_script(params)`: Generates a self-contained, standalone Python script that re-runs the exact analysis using MNE and Matplotlib offline.
- `export_power_matrix_csv(power, freqs, times)`: Dumps the 2D energy matrix into a tabular CSV format (rows = frequencies, columns = timestamps) with numerical headers.

---

## Integrating with Other BCI Pipeline Modules

If your project is part of a larger course platform combining all BCI stages, here is how Module 5 interfaces with upstream and downstream components:

```python
# Integration example: Connecting Module 4 (Epoching/ERP) -> Module 5 -> Module 6 (CSP)
import numpy as np
from core.time_frequency import compute_tfr, apply_baseline_correction

def process_bci_time_frequency(epoched_data, sfreq, target_channel="C3"):
    """
    Accepts epoched data from Module 4, computes time-frequency spectral power,
    and returns feature vectors for Module 6 (Spatial Analysis) or Module 8 (Classifier).
    
    Parameters:
        epoched_data: 2D numpy array of shape (n_channels, n_times)
        sfreq: Sampling rate in Hz
        target_channel: Name of channel to analyze
        
    Returns:
        dict containing power matrix, frequency bins, and time coordinates.
    """
    # 1. Compute Morlet wavelet time-frequency decomposition
    power, freqs, times = compute_tfr(
        data=epoched_data,
        sfreq=sfreq,
        method="morlet",
        fmin=4.0,
        fmax=35.0,
        n_freqs=32,
        n_cycles=7.0
    )
    
    # 2. Apply decibel baseline normalization against a pre-stimulus baseline window
    normalized_power = apply_baseline_correction(
        power=power,
        times=times,
        baseline=(0.0, 1.0),
        mode="db"
    )
    
    # 3. Hand off the spectral power matrix to downstream feature extractors / classifiers
    return {
        "features": normalized_power,
        "freqs": freqs,
        "times": times,
        "channel": target_channel
    }
```

---

## How to Add a New Time-Frequency Method

If you want to implement an additional spectral method (for example, Stockwell Transform or Wigner-Ville Distribution):

1. **Implement the algorithm in `core/time_frequency.py`:**
   Write a function matching the standard signature returning `(power, freqs, times)`:
   ```python
   def compute_custom_tfr(data, sfreq, freqs=None, ...):
       # Your signal processing logic here
       # Ensure power shape is (n_freqs, n_times)
       return power, freqs, times
   ```

2. **Add a branch in `compute_tfr()`:**
   ```python
   elif method == 'custom':
       return compute_custom_tfr(data, sfreq, **kwargs)
   ```

3. **Add user controls in `components/sidebar.py`:**
   Add any new parameters to `render_analysis_controls()` inside the sidebar.

4. **Add test coverage in `tests/test_time_frequency.py`:**
   Write unit tests to verify output shapes, dtype consistency, and boundary handling.

---

## Running the Automated Test Suite

We use `pytest` for unit tests. Always run pytest via `python -m pytest` so that Python adds the repository root to `sys.path`:

```bash
python -m pytest tests/ -v
```

The test suite executes headlessly in a few seconds and tests:
- Synthetic benchmark generation and raw signal integrity (`tests/test_data_loading.py`) 
- Numerical validity of Morlet, Multitaper, STFT, baseline normalization modes and bandpower calculations (`tests/test_time_frequency.py`)
- Parameter clamps, Nyquist checks and sanitization (`tests/test_validation.py`)
