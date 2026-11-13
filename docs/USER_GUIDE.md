# NeuroLab — Student User Guide

Welcome to the **NeuroLab User Guide**! This document provides step-by-step instructions for using the NeuroLab application in your Brain-Computer Interface (BCI) course assignments and laboratory sessions.

---

## 🧭 Navigation Overview

NeuroLab features a responsive navigation sidebar with 8 primary sections:

1. **🏠 Overview:** System mission, BCI curriculum context, and canonical frequency band cards.
2. **📊 EEG Data:** Dataset management, built-in benchmarks, file uploader, and channel inspector.
3. **🔬 Time-Frequency Explorer:** Main laboratory with interactive controls and two linked plots.
4. **📚 Learn the Concepts:** 15 modular theory topics and the interactive Parameter Playground.
5. **🧪 Experiment Lab:** Guided student experiments (Alpha Blocking, Motor Imagery ERD/ERS, Resolution Trade-off).
6. **✅ Knowledge Check:** 10-question multiple-choice interactive quiz.
7. **💾 Export Results:** Download parameters as JSON, executable Python scripts, and CSV power matrices.
8. **ℹ️ About:** Academic background, grading rubrics, technology stack, and licensing.

---

## 🛠️ Step-by-Step Student Workflow

### Step 1: Launch NeuroLab
Open your terminal, navigate to the repository directory, and run:
```bash
streamlit run app.py
```
Your default browser will open the application at `http://localhost:8501`.

---

### Step 2: Choose or Upload EEG Data
Navigate to **📊 EEG Data** in the sidebar. You have three choices:

#### Option A: Sample Dataset — Alpha Blocking (Default)
- **What it is:** A 10-channel, 30-second synthetic recording simulating occipital alpha rhythm dynamics.
- **Key Channels:** `Oz`, `O1`, `O2` (occipital electrodes).
- **Phases:** 
  - 0–10s: Eyes Closed (strong 10 Hz alpha oscillation)
  - 10–20s: Eyes Open (alpha blocking / desynchronization)
  - 20–30s: Eyes Closed (recovery of alpha rhythm)

#### Option B: Sample Dataset — Motor Imagery
- **What it is:** A 6-channel, 20-second recording simulating sensorimotor rhythms (electrodes `C3`, `Cz`, `C4`).
- **Phases:**
  - 0–5s: Baseline rest
  - 5–10s: Left-hand imagery (contralateral right-hemisphere ERD at C4)
  - 10–15s: Rest recovery
  - 15–20s: Right-hand imagery (contralateral left-hemisphere ERD at C3)

#### Option C: Upload Your Own EEG File
- Drag and drop or browse for an EEG file. Supported formats:
  - **`.edf`** (European Data Format — standard clinical format)
  - **`.fif`** (Neuromag / MNE raw format)
  - **`.vhdr`** (BrainVision header — ensure associated `.vmrk` and `.eeg` files are in the same folder)
  - **`.set`** (EEGLAB dataset)
  - **`.csv`** (Tabular format: set sampling rate, select time column and channel columns)

---

### Step 3: Run Time-Frequency Decomposition
Switch to **🔬 Time-Frequency Explorer** in the sidebar.

#### 1. Select Electrode Site
Choose the scalp electrode from the **EEG Channel** dropdown (e.g. `Oz` for visual alpha or `C3`/`C4` for motor rhythms).

#### 2. Choose Analysis Algorithm
Select from three established mathematical methods:
- **Morlet Wavelet Transform:**
  - *Setting to adjust:* **Number of Cycles ($n_{cycles}$)**.
  - *Tip:* Use 3–5 cycles for fast temporal transient detection; use 10–14 cycles for sharp frequency separation. Default is 7.0 cycles.
- **Multitaper Method:**
  - *Setting to adjust:* **Time-Bandwidth Product ($NW$)**.
  - *Tip:* Higher values (e.g. 4.0–6.0) average more orthogonal DPSS tapers, reducing variance.
- **Short-Time Fourier Transform (STFT):**
  - *Settings to adjust:* **Window Length (samples)**, **Overlap**, and **Window Function** (Hann, Hamming, Blackman).
  - *Tip:* Longer windows sharpen frequency bins; shorter windows sharpen temporal resolution.

#### 3. Set Frequency Limits
- Choose **Min Freq** (e.g. 1.0 Hz) and **Max Freq** (e.g. 40.0 Hz). Frequencies are validated against the Nyquist bound ($f_{max} \le f_s / 2$).
- Choose **Frequency Points** (slider between 10 and 100) to control vertical spectrogram granularity.

#### 4. Configure Baseline Correction
- Choose a baseline mode: `None`, `mean`, `ratio`, `db`, `percent`, or `zscore`.
- For Event-Related Desynchronization (ERD) studies, select **`db`** and set the baseline interval to a pre-stimulus resting period (e.g. 0.0s to 5.0s).

---

### Step 4: Interact with the Linked Plots
The visualization automatically recalculates when you alter any parameter:
- **Plot 1 (Top Waveform):** Shows instantaneous amplitude in microvolts ($\mu\text{V}$) with event markers. The dashed box highlights your selected time range of interest.
- **Plot 2 (Bottom Spectrogram):** Displays spectral power across time and frequency.
- **Crosshair Inspection:** Hover your cursor anywhere on the spectrogram to view exact values: `Time (s)`, `Frequency (Hz)`, and `Power`.
- **Linked Zooming:** Use the Plotly box-zoom or pan tools. Both plots share a synchronized horizontal time axis.
- **Band Power Trajectories:** Expand the bottom accordion to inspect individual power envelopes for Delta, Theta, Alpha, Beta, and Gamma.

---

### Step 5: Conduct Guided Experiments
Visit **🧪 Experiment Lab** to test your knowledge with three structured neuroscience experiments:
1. **Occipital Alpha Blocking:** Observe how opening the eyes shuts down the 10 Hz rhythm.
2. **Motor Imagery ERD/ERS:** Compare C3 vs. C4 during left vs. right hand imagination.
3. **Resolution Trade-off:** Side-by-side comparison of Morlet wavelets and STFT on identical signals.

---

### Step 6: Test Your Understanding
Navigate to **✅ Knowledge Check** and take the 10-question multiple-choice quiz.
- Select your answers and click **Submit Answers for Grading**.
- Review explanations for both correct and incorrect choices.
- Retake the quiz at any time using **Restart Quiz**.

---

### Step 7: Export Code & Deliverables
Go to **💾 Export Results**:
- Click **Download Parameters (.json)** to save your exact configuration metadata.
- Click **Download Executable Python Script (.py)** to download a complete, standalone script that reproduces your exact figures using MNE and Matplotlib outside Streamlit.
- Click **Download Computed Power Matrix (.csv)** to export the numerical energy surface for MATLAB, R, or Python data science workflows.
