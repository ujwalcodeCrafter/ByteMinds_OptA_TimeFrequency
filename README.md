# NeuroLab — Interactive EEG Time-Frequency Analysis

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.45%2B-FF4B4B.svg)](https://streamlit.io/)
[![MNE-Python](https://img.shields.io/badge/mne--python-1.6%2B-green.svg)](https://mne.tools/)
[![Tests](https://img.shields.io/badge/pytest-16%20passed-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **"Discover when, where, and how brainwave activity changes."**

**NeuroLab** is an interactive, scientific educational web application designed for university Brain-Computer Interface (BCI) courses. It serves as **Module 5: Time-Frequency Analysis** in the BCI signal-processing pipeline, enabling students and researchers to master how dynamic neural oscillations are decomposed, visualized, and decoded.

---

## 🎯 Module Role in the BCI Curriculum

NeuroLab integrates cleanly into the shared university BCI pipeline:

```
[1. Data Loading] ➔ [2. Filtering] ➔ [3. Artifact Handling] ➔ [4. Epoching & ERP]
                                      │
                                      ▼
                        [5. TIME-FREQUENCY ANALYSIS (NeuroLab)]
                                      │
                                      ▼
[6. Spatial Analysis] ➔ [7. Feature Extraction] ➔ [8. Classification] ➔ [9. Paradigm Explorer]
```

---

## 🚀 Key Features

### 1. Ready-to-Use Datasets & Flexible Uploads
- **Built-in Benchmark 1 (Alpha Blocking):** 10-channel 30s synthetic EEG with realistic 1/f pink noise, occipital alpha (10 Hz), and event annotations (`eyes_closed` ➔ `eyes_open` ➔ `eyes_closed`).
- **Built-in Benchmark 2 (Motor Imagery):** 6-channel 20s sensorimotor rhythm simulation with contralateral mu (11 Hz) and beta (22 Hz) Event-Related Desynchronization (ERD) at C3/C4.
- **Universal EEG File Upload:** Reads **EDF (`.edf`)**, **FIF (`.fif`)**, **BrainVision (`.vhdr`)**, **EEGLAB (`.set`)**, and customizable **CSV (`.csv`)** files.

### 2. Authentic Mathematical Time-Frequency Engine
No fake mockups or static plots. All representations are calculated live via established scientific algorithms:
- **Morlet Wavelet Transform:** Continuous wavelet transform using MNE's `tfr_array_morlet` with user-selectable cycle count ($n_{cycles}$) and frequency-adaptive resolution.
- **Multitaper Method:** DPSS orthogonal eigenspectra using MNE's `tfr_array_multitaper` with time-bandwidth product ($NW$) smoothing.
- **Short-Time Fourier Transform (STFT):** SciPy's `scipy.signal.stft` with adjustable window length, overlap, and tapering windows (Hann, Hamming, Blackman).
- **Baseline Normalization Modes:** None, Additive Mean, Ratio, Log-ratio, Percent Change, Z-score, and Decibels ($10 \log_{10}(P/P_{base})$).

### 3. Synchronized, Linked Dual Visualizations
- **Plot 1 (Top):** Interactive raw EEG potential trace (in $\mu\text{V}$) with event markers, channel label, and ROI time window highlight.
- **Plot 2 (Bottom):** Time-Frequency Spectrogram with calibrated power colorbar and frequency range.
- **Synchronized Linking:** Time-window selection updates and aligns both plots simultaneously with crosshair inspection.
- **Bonus Plot:** Real-time physiological frequency band power trajectories (Delta, Theta, Alpha, Beta, Gamma).

### 4. Guided Experiment Lab
- **Experiment 1 (Occipital Alpha Blocking):** Visual sensory gating over primary visual cortex (Oz).
- **Experiment 2 (Motor Imagery ERD/ERS):** Contralateral sensorimotor rhythm desynchronization during left vs. right hand imagery.
- **Experiment 3 (Heisenberg-Gabor Trade-off):** Empirical demonstration of the fundamental time vs. frequency resolution bound.

### 5. Interactive Explain Panel & Parameter Playground
- Comprehensive explanations for 15 foundational BCI questions.
- Dynamic diagnostic feedback on active parameters.
- Interactive **Parameter Playground** explaining the physical consequences of turning knobs.

### 6. Knowledge Check Quiz
- 10-question multiple-choice interactive quiz with scoring, scientific explanations, and reset capability.

### 7. Export Functionality
- **JSON Configuration:** Complete metadata for analysis reproduction.
- **Reproducible Python Script (`.py`):** Standalone executable script generated with exact student-selected parameters.
- **Power Matrix (`.csv`):** Full numerical frequency $\times$ time energy matrix.

---

## 💻 Technology Stack

- **Application & UI:** Python 3.12+, Streamlit 1.45+
- **EEG & Signal Processing:** MNE-Python 1.6+, SciPy 1.10+, NumPy 1.24+, Pandas 2.0+
- **Interactive Visualizations:** Plotly Graph Objects & Plotly Express
- **Automated Verification:** Pytest test harness

---

## 📦 Project Directory Structure

```
BCI_Time_Frequency_Project/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Dependency specifications
├── .gitignore                  # Git ignore rules
├── .env.example                # Environment variables template
├── README.md                   # Project overview and instructions
│
├── core/                       # Scientific processing engine (UI-independent)
│   ├── __init__.py             # Core package interface
│   ├── data_loader.py          # Multi-format EEG parser (EDF, FIF, VHDR, SET, CSV)
│   ├── sample_data.py          # Synthetic benchmarks (Alpha blocking, Motor imagery)
│   ├── preprocessing.py       # Signal cropping, channel slicing, filtering
│   ├── time_frequency.py       # Morlet, Multitaper, STFT, and baseline correction
│   ├── band_power.py           # Clinical EEG band power computation
│   ├── validation.py           # Parameter bounds & Nyquist constraints
│   └── export_utils.py         # JSON, CSV, and Python code generation
│
├── components/                 # Streamlit UI modules
│   ├── __init__.py
│   ├── sidebar.py              # Navigation and parameter controls
│   ├── visualizations.py       # Linked Plotly figures & band power plots
│   ├── controls.py             # Data source selector & metadata cards
│   ├── explain_panel.py        # Educational explanations & Parameter Playground
│   ├── experiment_lab.py       # Three guided student experiments
│   └── quiz.py                 # Interactive 10-question quiz
│
├── tests/                      # Automated pytest suite (16 tests)
│   ├── test_data_loading.py    # Dimensions, sfreq, annotations, CSV tests
│   ├── test_time_frequency.py  # Morlet, Multitaper, STFT, baselines, band power
│   └── test_validation.py      # Nyquist limits, cycles, window constraints
│
└── docs/                       # Project documentation
    ├── USER_GUIDE.md           # Student walkthrough & operation guide
    ├── DEVELOPER_GUIDE.md      # Architecture & BCI integration guide
    ├── SCIENTIFIC_BACKGROUND.md# Mathematical formulations & neurophysiology
    ├── DEMO_SCRIPT.md          # 10-minute presentation & viva script
    └── CONTRIBUTION_TEMPLATE.md# Individual student contribution form
```

---

## ⚡ Quickstart: One-Line Run Command

### 1. Clone & Navigate
```bash
git clone <repository-url>
cd BCI_Time_Frequency_Project
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application (One-Line Command)
```bash
streamlit run app.py
```
The application opens automatically in your web browser at `http://localhost:8501`.

---

## 🧪 Running the Automated Test Suite

NeuroLab includes an automated test suite verifying data loaders, signal processing pipelines, baseline corrections, and parameter validations:

```bash
pytest tests/ -v
```

Expected output:
```text
tests/test_data_loading.py::test_generate_sample_eeg_structure PASSED        [  6%]
tests/test_data_loading.py::test_sample_data_metadata_and_annotations PASSED [ 12%]
tests/test_data_loading.py::test_motor_imagery_dataset_generation PASSED     [ 18%]
tests/test_data_loading.py::test_extract_data_info PASSED                    [ 25%]
tests/test_data_loading.py::test_csv_data_loader PASSED                      [ 31%]
tests/test_time_frequency.py::test_morlet_wavelet_computation PASSED         [ 37%]
tests/test_time_frequency.py::test_multitaper_computation PASSED             [ 43%]
tests/test_time_frequency.py::test_stft_computation PASSED                   [ 50%]
tests/test_time_frequency.py::test_baseline_correction_modes PASSED          [ 56%]
tests/test_time_frequency.py::test_compute_band_power PASSED                 [ 62%]
tests/test_validation.py::test_frequency_range_validation PASSED             [ 68%]
tests/test_validation.py::test_wavelet_cycles_validation PASSED              [ 75%]
tests/test_validation.py::test_stft_params_validation PASSED                 [ 81%]
tests/test_validation.py::test_time_range_validation PASSED                  [ 87%]
tests/test_validation.py::test_channel_validation PASSED                     [ 93%]
tests/test_validation.py::test_sanitize_parameters PASSED                    [100%]

======================= 16 passed in 2.54s =======================
```

---

## ⚠️ Limitations & Academic Disclaimer

- **Educational Purpose:** NeuroLab is built specifically for academic teaching and university laboratory courses. It is **not** a certified medical diagnostic device and must not be used for clinical diagnoses or patient care.
- **Privacy & Security:** All computation is executed strictly on the local machine; no neural telemetry is uploaded to third-party cloud services.
- **Synthetic Data Disclaimer:** Synthetic datasets are explicitly labeled in the UI to maintain rigorous scientific distinction between simulated benchmarks and clinical human recordings.
