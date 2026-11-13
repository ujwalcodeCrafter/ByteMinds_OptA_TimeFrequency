# NeuroLab — Developer & Integration Guide

This guide is intended for developers, researchers, and instructors extending NeuroLab or integrating it into a shared BCI educational platform alongside other modules (Filtering, Epoching, Spatial Analysis, Classification).

---

## 🏛️ Architecture & Design Philosophy

NeuroLab is architected under strict **separation of concerns**:
- **`core/`:** Pure, framework-agnostic scientific signal processing. Every function takes and returns standard NumPy arrays, MNE objects, or primitive Python types. It has **no dependencies on Streamlit**. This allows `core/` functions to be imported into command-line pipelines, batch scripts, Jupyter notebooks, or other GUI frameworks.
- **`components/`:** Streamlit-specific presentation components (Plotly charts, sidebars, educational panels, quiz modules).
- **`app.py`:** Orchestrator that binds user inputs to core processing functions and renders UI components.

```
       User Interface (Streamlit)
               │
        components/ (Plotly, UI cards)
               │
          app.py (Orchestrator)
               │
  ┌────────────┴────────────┐
  ▼                         ▼
core/time_frequency.py    core/data_loader.py
core/sample_data.py       core/preprocessing.py
core/band_power.py        core/validation.py
core/export_utils.py
```

---

## 📁 Core Module Interface Reference

### 1. `core.time_frequency`
- `compute_morlet_tfr(data, sfreq, freqs=None, n_cycles=7.0, fmin=1.0, fmax=40.0, n_freqs=30, output='power', decim=1)`:
  - Uses `mne.time_frequency.tfr_array_morlet`. Reshapes 1D data to `(1, 1, n_times)` for MNE, extracts `[0, 0]`.
  - Returns `(power, freqs, times)`.
- `compute_multitaper_tfr(data, sfreq, freqs=None, fmin=1.0, fmax=40.0, n_freqs=30, time_bandwidth=4.0, decim=1)`:
  - Uses `mne.time_frequency.tfr_array_multitaper` with adaptive cycles (`n_cycles = freqs / 2.0`).
  - Returns `(power, freqs, times)`.
- `compute_stft(data, sfreq, window_length=256, overlap=None, fmin=0.0, fmax=None, window='hann')`:
  - Uses `scipy.signal.stft`. Power is computed as $|Z_{xx}|^2$.
  - Returns `(power, freqs, times)`.
- `apply_baseline_correction(power, times, baseline=None, mode='mean')`:
  - Modes: `'mean'`, `'ratio'`, `'logratio'`, `'percent'`, `'zscore'`, `'db'`.
  - Includes division-by-zero protection via `np.finfo(float).eps`.
- `compute_tfr(data, sfreq, method='morlet', **kwargs)`:
  - Unified dispatcher.

### 2. `core.data_loader`
- `load_eeg_file(file_path_or_buffer, file_type=None, **kwargs)`:
  - Supports `.edf`, `.fif`, `.vhdr`, `.set`, `.csv`.
  - Returns `(raw: mne.io.Raw, info_dict: dict)`.
- `extract_data_info(raw)`:
  - Returns metadata dictionary: `n_channels`, `ch_names`, `sfreq`, `n_samples`, `duration`, `annotations`, `ch_types`.

### 3. `core.sample_data`
- `generate_sample_eeg(duration=30.0, sfreq=256.0, random_seed=42)`:
  - Generates 10-channel benchmark with alpha oscillation, 1/f noise, and alpha blocking event markers.
- `generate_motor_imagery_data(duration=20.0, sfreq=256.0, random_seed=123)`:
  - Generates 6-channel benchmark with sensorimotor mu/beta ERD/ERS at C3/C4.

### 4. `core.validation`
- `validate_frequency_range(fmin, fmax, sfreq)`
- `validate_wavelet_cycles(n_cycles, freqs)`
- `validate_stft_params(window_length, overlap, n_samples)`
- `validate_time_range(tmin, tmax, total_duration)`
- `validate_baseline(baseline, tmin, tmax)`
- `validate_channel(channel, available_channels)`
- `sanitize_parameters(params_dict)`

---

## 🔌 How to Integrate into the Unified BCI Platform

To incorporate NeuroLab into a multi-group monolithic Streamlit application:

```python
# In main_bci_platform.py
import streamlit as st
from core.time_frequency import compute_tfr, apply_baseline_correction
from components.visualizations import create_linked_plots

def render_module_5_time_frequency(preprocessed_raw):
    """
    Module 5 Entrypoint: Accepts preprocessed MNE Raw object from Module 4 (Epoching & ERP)
    and passes computed spectral features to Module 6 (Spatial Analysis / CSP).
    """
    st.subheader("Module 5: Time-Frequency Analysis")
    
    # 1. Extract channel
    ch_name = st.selectbox("Select Channel", preprocessed_raw.ch_names)
    data = preprocessed_raw.get_data()[preprocessed_raw.ch_names.index(ch_name)]
    sfreq = preprocessed_raw.info['sfreq']
    
    # 2. Compute TFR
    power, freqs, times = compute_tfr(data, sfreq, method='morlet', fmin=4.0, fmax=40.0)
    
    # 3. Render linked plots
    fig = create_linked_plots(data, preprocessed_raw.times, power, freqs, times, ch_name, "Morlet")
    st.plotly_chart(fig, use_container_width=True)
    
    # 4. Return feature tensor for Module 6 / Module 7
    return {
        'power_matrix': power,
        'freqs': freqs,
        'times': times,
        'channel': ch_name
    }
```

---

## ➕ How to Add a New Time-Frequency Method

To add a new algorithm (e.g. Hilbert-Huang Transform or Wigner-Ville Distribution):
1. In `core/time_frequency.py`, implement your function returning `(power, freqs, times)`:
   ```python
   def compute_hilbert_tfr(data, sfreq, ...):
       # Computation logic
       return power, freqs, times
   ```
2. Add the method name to `compute_tfr()`:
   ```python
   elif method == 'hilbert':
       return compute_hilbert_tfr(data, sfreq, **kwargs)
   ```
3. Add UI parameter inputs in `components/sidebar.py`.
4. Add automated test cases in `tests/test_time_frequency.py`.

---

## 🧪 Automated Testing Instructions

Run pytest with coverage or verbose mode:
```bash
pytest tests/ -v
```
All tests are strictly headless and execute within seconds without opening graphical windows.
