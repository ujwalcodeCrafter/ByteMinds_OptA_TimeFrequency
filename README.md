# Time-Frequency: Interactive EEG Time-Frequency Analysis

This repository contains the code for **Module5: Time-Frequency Analysis**. This was created as part of a project for our university course on Brain-Computer Interface (BCI).

The project uses Python and the Streamlit framework to create an interactive tool to analyze, calculate and visualize how the spectral powers of an EEG signal shift over time using actual signal processing techniques.

---

## Why Time-Frequency Analysis?

In many cases, when using EEG or BCI technology, neural signals are non-stationary – they can vary from one moment to the next based on many factors including movement, stimuli and thoughts.

Using a Fast Fourier Transform (FFT) will allow you to see the frequency spectrum for the entire time window – you will know *what* frequencies are present, but not *when* they were present. On the other hand, simply analyzing the raw EEG data in the time domain will show instantaneous power levels – you will be able to see how oscillations are increasing and decreasing, but you will not know what these oscillations are.

**Time-frequency analysis bridges this gap.** By observing dynamic neural phenomena by placing a signal into both dimensions at the same time. This includes:
- **Event-Related Desynchronization (ERD):** A specific decrease in rhythmic power (suppression of mu and beta rhythms over motor cortex when imagining movement)
- **Event-Related Synchronization (ERS):** A sudden increase or remnant of rhythmic power
- **Rhythmic Gating / Alpha Blocking:** Blocking of occipital alpha waves (8-12Hz) when eyes are open and subsequent return when eyes are closed

---

## Role in the BCI Curriculum

Within the standard 9-module BCI processing pipeline, this tool acts as the bridge between raw signal conditioning and downstream machine learning:

```text
[1. Data Loading] -> [2. Filtering] -> [3. Artifact Handling] -> [4. Epoching & ERP]
                                      |
                                      v
                        [5. TIME-FREQUENCY ANALYSIS]  <-- (This Module)
                                      |
                                      v
[6. Spatial Analysis] -> [7. Feature Extraction] -> [8. Classification] -> [9. Paradigm Explorer]
```

It takes continuous or epoched EEG signals from earlier preprocessing steps and computes the spectral energy distribution that gets passed to spatial filters (like CSP) or feature classifiers.

---

## What the Application Does

- **Multiple Decomposition Methods:**
  - **Morlet Wavelets:** Use `tfr_array_morlet` from MNE with adjustable wavelet cycles to control the time-vs-frequency resolution trade-off.
  - **Multitaper Analysis:** Use `tfr_array_multitaper` from MNE with adjustable time-bandwidth product to obtain smooth estimates of the spectrum with low variance.
  - **Short-Time Fourier Transform (STFT):** Use `scipy.signal.stft` from SciPy to perform a windowed Fourier transform with customizable window shape (Hamming, Hann, Blackman), length, and overlap.
  - **Side-by-Side Method Comparison:** Plot a comparison view to apply STFT, Morlet, and Multitaper on the same signal portion and visualize how the three methods’ spectrograms compare.

- **Baseline Normalization Modes:**
  - Essential for isolating event-related effects from background pink noise ($1/f$). Supports standard baseline modes: Mean subtraction, Ratio, Log-ratio, Decibels ($10 \log_{10}(P/P_{base})$), Percent Change, and Z-score.

- **Data Sources Supported:**
  - **Built-in Benchmark 1 (Alpha Blocking):** 10-channel 30-second synthetic recording with 1/f noise, visual alpha oscillations at Oz/O1/O2, and alternating eyes-closed / eyes-open intervals.
  - **Built-in Benchmark 2 (Motor Imagery):** 6-channel 20-second sensorimotor rhythm simulation showing contralateral mu (11 Hz) and beta (22 Hz) desynchronization at C3 and C4 during left- and right-hand motor imagery.
  - **File Uploads:** Reads `.edf`, `.fif`, `.vhdr` (BrainVision), `.set` (EEGLAB), and `.csv` files.

- **Synchronized Visualizations:**
  - Top waveform plot with raw voltage, marked with events and region of interest indicators. Below is a time-frequency spectrogram that updates when the user pans or zooms on the time axis.
  - Frequency band power trajectory: Delta (1-4Hz), Theta (4-8Hz), Alpha (8-13Hz), Beta (13-30Hz), Gamma (30-40Hz) over time.

- **Educational Tools & Export:**
  - Concept explainers: core signal processing theory discussed, interactive parameter playground explaining the trade-offs of adjusting each knob.
  - Knowledge check quiz to assess understanding with immediate feedback.
  - Ability to export the following for analysis: a configuration file (JSON), a script to reproduce the analysis (Python), and a calculated power matrix (CSV).

---

## Project Structure

```text
BCI_3/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python package dependencies
├── .env.example                # Example configuration
├── .gitignore                  # Git ignore rules
├── README.md                   # This document
│
├── core/                       # Core signal processing functions (no Streamlit dependency)
│   ├── __init__.py
│   ├── data_loader.py          # EEG file loaders (.edf, .fif, .vhdr, .set, .csv)
│   ├── sample_data.py          # Synthetic benchmarks for alpha blocking & motor imagery
│   ├── preprocessing.py       # Slicing, channel selection, filtering
│   ├── time_frequency.py       # Morlet, Multitaper, STFT, and baseline algorithms
│   ├── band_power.py           # Band power trajectory calculations
│   ├── validation.py           # Parameter checking & Nyquist limit enforcement
│   └── export_utils.py         # JSON metadata, CSV export, and Python script generation
│
├── components/                 # Streamlit UI layouts and interactive widgets
│   ├── __init__.py
│   ├── sidebar.py              # Navigation and parameter controls
│   ├── visualizations.py       # Linked Plotly graphs & band trajectories
│   ├── controls.py             # Data source selector & channel metadata displays
│   ├── explain_panel.py        # Theory questions & parameter playground
│   └── quiz.py                 # Self-assessment multiple-choice quiz
│
├── tests/                      # Automated test suite
│   ├── test_data_loading.py    # Tests for loaders, synthetic data, and metadata
│   ├── test_time_frequency.py  # Tests for Morlet, Multitaper, STFT, baselines, band power
│   └── test_validation.py      # Tests for parameter clamps and input validation
│
└── docs/                       # Project documentation
    ├── USER_GUIDE.md           # Student walkthrough for running and using the app
    ├── DEVELOPER_GUIDE.md      # Code architecture and BCI pipeline integration guide
    └── CONTRIBUTION_TEMPLATE.md# Group contribution statement form
```

---

## Setup and Installation

### 1. Prerequisites
- Python 3.12 (Python 3.10+ also works)
- `pip` package manager

### 2. Clone the Repository
```bash
git clone <repository-url>
cd BCI_3
```

### 3. Create a Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the Application
```bash
streamlit run app.py
```
Streamlit will start a local server and open `http://localhost:8501` in your default browser.

---

## Running the Automated Tests

The test suite covers data loading, sample generation, each time-frequency algorithm, baseline corrections, and parameter validations.

Run the tests using `python -m pytest` from the project root:

```bash
python -m pytest tests/ -v
```

All 16 tests should run headless and pass:
- `tests/test_data_loading.py`: 5 tests
- `tests/test_time_frequency.py`: 5 tests
- `tests/test_validation.py`: 6 tests
