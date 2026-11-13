# NeuroLab — 10-Minute Group Demonstration & Viva Script

This script provides a structured timeline and speaking points for your 10-minute university course demonstration and viva defense.

---

## ⏱️ Timeline Breakdown (Total: 10 Minutes)

| Time | Segment | Presenter Role | Key Screen / Feature Shown |
|---|---|---|---|
| **00:00 – 01:30** | Introduction & Academic Context | Speaker 1 | Landing Page (`Overview`) |
| **01:30 – 03:30** | Architecture, Data Loading & Formats | Speaker 2 | `EEG Data` & Multi-format loader |
| **03:30 – 06:30** | Live Time-Frequency Analysis & Linked Plots | Speaker 3 | `Time-Frequency Explorer` |
| **06:30 – 08:00** | Guided Neuroscience Experiments | Speaker 1 or 2 | `Experiment Lab` (Alpha Blocking & MI) |
| **08:00 – 09:00** | Educational Quiz & Reproducible Export | Speaker 3 | `Knowledge Check` & `Export Results` |
| **09:00 – 10:00** | Conclusion, Viva Q&A Defense | All Speakers | `About` & Codebase Architecture |

---

## 🎤 Detailed Speaking Script

### Minute 0:00 – 1:30: Introduction & Theoretical Need
**Speaker 1:**
> "Good morning, Professor and classmates. Our team is presenting **Module 5: Time-Frequency Analysis** of the BCI signal-processing pipeline, implemented in our platform, **NeuroLab**.
> 
> In Brain-Computer Interfaces, standard time-domain signals tell us *amplitude*, and classic Fourier transforms tell us *what frequencies exist*. But because brain states change from millisecond to millisecond—such as when a user prepares to move or opens their eyes—ordinary FFT averages all timing away. Time-Frequency Analysis solves this by answering three questions at once: **When** does neural activity happen, at **what frequency**, and with **what power**?"
> 
> *(Navigate to Overview: show the 5 clinical frequency bands reference cards)*

---

### Minute 1:30 – 3:30: Data Handling & Integrity
**Speaker 2:**
> "Let's examine how data enters NeuroLab. Under the **EEG Data** tab, we support real laboratory standards: EDF, FIF, BrainVision, EEGLAB, and raw CSVs.
> 
> For repeatable educational learning, we also provide two deterministic physiological benchmarks:
> 1. An **Alpha Blocking Benchmark** with 10 channels, 1/f pink noise background, and synchronized event markers.
> 2. A **Motor Imagery Benchmark** simulating contralateral mu and beta desynchronization across C3 and C4.
> 
> Let's inspect channel `Oz` over the occipital lobe on our raw waveform viewer."
> 
> *(Show channel preview, annotations, and sample rate metrics)*

---

### Minute 3:30 – 6:30: Core Engine & The Two Linked Plots (Key Viva Requirement)
**Speaker 3:**
> "Now we enter the heart of our module: the **Time-Frequency Explorer**.
> 
> Notice that we have implemented all three core mathematical methods using true scientific libraries: MNE Morlet Wavelets, MNE Multitaper with DPSS tapers, and SciPy Short-Time Fourier Transform.
> 
> Look at our **Two Linked Plots**:
> - The top plot shows the raw microvolt potential fluctuations with condition intervals.
> - The bottom plot displays the computed energy surface spectrogram.
> - Both plots share a linked temporal axis. If I zoom into the transition at second 10, both the waveform and spectrogram focus simultaneously.
> 
> Now watch what happens when I adjust parameters:
> - If I increase Morlet wavelet cycles from 3 to 14, observe how the frequency resolution sharpens horizontally while temporal boundaries blur.
> - If I activate **Decibel Baseline Normalization**, the 1/f background slope is removed, and task-related power changes become immediately obvious.
> - Below the linked plots, we also render an automatic clinical band power evolution plot tracking Delta, Theta, Alpha, Beta, and Gamma."

---

### Minute 6:30 – 8:00: Guided Experiments & Scientific Proof
**Speaker 1:**
> "To guide students through empirical neuroscience concepts, we built the **Experiment Lab**:
> 
> 1. In **Experiment 1 (Alpha Blocking)**, students observe the Hans Berger effect: when the eyes open at second 10, 10 Hz alpha power plummets by over 75%.
> 2. In **Experiment 2 (Motor Imagery)**, students view the sensorimotor cortex: during imagined left-hand movement, electrode C4 over the right hemisphere exhibits prominent blue Event-Related Desynchronization (ERD), while C3 remains neutral.
> 3. In **Experiment 3**, students directly visualize the Heisenberg-Gabor resolution trade-off."

---

### Minute 8:00 – 9:00: Knowledge Check & Reproducible Code Export
**Speaker 3:**
> "To test retention, students can take our 10-question **Knowledge Check**, which grades answers and provides full scientific explanations.
> 
> Finally, in the **Export Results** tab:
> - Students can download their parameter configuration as clean JSON.
> - They can download an automatically generated, standalone Python script that reproduces their exact figures using MNE and Matplotlib outside Streamlit.
> - They can export the raw frequency-by-time numerical energy matrix as a CSV."

---

### Minute 9:00 – 10:00: Viva Defense & Anticipated Questions
**All Speakers:**
> "We welcome any questions from the instructor."

#### Anticipated Viva Questions & Answers:
1. **Q: Why use Morlet wavelets instead of STFT for event-related EEG?**
   - *A:* "STFT uses a fixed window size for all frequencies. Morlet wavelets have frequency-adaptive resolution: wider in time for low frequencies (like 2 Hz delta) and narrower in time for high frequencies (like 40 Hz gamma), which matches natural brain oscillation dynamics."
2. **Q: How does your baseline correction prevent division by zero?**
   - *A:* "In `core/time_frequency.py`, we enforce `np.maximum(baseline_power, np.finfo(float).eps)` before computing ratios or taking logarithms for dB scaling."
3. **Q: How do you enforce Nyquist limits?**
   - *A:* "In `core/validation.py`, we check `fmax <= sfreq / 2`. If a user attempts to set `fmax` above the Nyquist boundary, the sanitizer rejects it with an explicit warning."
4. **Q: Are all computations executed live?**
   - *A:* "Yes, every time a parameter is altered, MNE and SciPy functions execute directly in memory on the selected EEG array."
