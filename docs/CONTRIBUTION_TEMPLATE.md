# Individual Contribution Statement

**Course:** Brain-Computer Interfaces (BCI)  
**Project Module:** Module 5 — Time-Frequency Analysis  
**Application Name:** NeuroLab: Interactive EEG Time-Frequency Explorer  
**Submission Date:** November 2026  
**Group Number / Name:** Group 5 — Time-Frequency Analysis  

---

## 👥 Student 1 Contribution
- **Full Name:** [Student 1 Name]
- **Student ID:** [ID Number]
- **Assigned Subsystems:** Core Time-Frequency Algorithms & Baseline Processing
- **Detailed Responsibilities:**
  - Implemented continuous Morlet wavelet transform using MNE's `tfr_array_morlet` with user-configurable cycle parameters.
  - Implemented Multitaper spectral estimation using MNE's `tfr_array_multitaper` with DPSS orthogonal sequences.
  - Formulated and verified all baseline correction modes (Mean subtraction, Ratio, Log-ratio, Decibels, Percent change, Z-score) in `core/time_frequency.py`.
  - Authored automated tests in `tests/test_time_frequency.py` achieving 100% pass rate.

---

## 👥 Student 2 Contribution
- **Full Name:** [Student 2 Name]
- **Student ID:** [ID Number]
- **Assigned Subsystems:** Data Ingestion, Multi-Format Parsers & Physiological Benchmarks
- **Detailed Responsibilities:**
  - Built the multi-format EEG loading pipeline in `core/data_loader.py` supporting EDF, FIF, BrainVision (.vhdr), EEGLAB (.set), and custom CSVs.
  - Designed the synthetic benchmark generators in `core/sample_data.py` (Alpha Blocking paradigm with 1/f noise and Motor Imagery C3/C4 sensorimotor rhythm simulation).
  - Designed and implemented parameter bounds validation and Nyquist constraint enforcement in `core/validation.py`.
  - Authored automated tests in `tests/test_data_loading.py` and `tests/test_validation.py`.

---

## 👥 Student 3 Contribution
- **Full Name:** [Student 3 Name]
- **Student ID:** [ID Number]
- **Assigned Subsystems:** Interactive Dashboard UI, Linked Plotly Visualizations & Export Utilities
- **Detailed Responsibilities:**
  - Developed the modern Streamlit web application (`app.py`) with responsive dark neuroscience lab styling.
  - Built the two synchronized, linked Plotly plots in `components/visualizations.py` featuring shared temporal zoom and crosshair inspection.
  - Developed the reproducible Python script generator (`core/export_utils.py`) and JSON parameter export.
  - Engineered the clinical frequency band power trajectories component (Delta, Theta, Alpha, Beta, Gamma).

---

## 👥 Student 4 Contribution (Optional / 4-Member Teams)
- **Full Name:** [Student 4 Name]
- **Student ID:** [ID Number]
- **Assigned Subsystems:** Educational Content, Experiment Lab & Knowledge Check Quiz
- **Detailed Responsibilities:**
  - Researched, authored, and implemented the educational explanations in `components/explain_panel.py` covering 15 core BCI signal-processing topics.
  - Built the interactive **Parameter Playground** with live contextual parameter diagnostics.
  - Programmed the **Experiment Lab** (`components/experiment_lab.py`) with three guided neuroscience studies (Alpha Blocking, Motor Imagery ERD/ERS, Resolution Trade-off).
  - Developed the interactive 10-question Knowledge Check quiz (`components/quiz.py`) with real-time scoring and feedback.

---

## ✍️ Group Confirmation & Sign-off

We certify that the work presented in this project was independently researched, designed, coded, and tested by our group members, and that all third-party scientific libraries (MNE-Python, SciPy, NumPy, Streamlit, Plotly) are appropriately cited and attributed.

| Member Name | Signature | Date |
|---|---|---|
| [Student 1] | ________________________ | __ / __ / 2026 |
| [Student 2] | ________________________ | __ / __ / 2026 |
| [Student 3] | ________________________ | __ / __ / 2026 |
| [Student 4] | ________________________ | __ / __ / 2026 |
