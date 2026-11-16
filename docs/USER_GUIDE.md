# Time-Frequency Analysis — Student User Guide

This guide will explain how to use the Time-Frequency Analysis interactive application in labs and assignments for the BCI course.

## **Why are we doing Time-Frequency Analysis**

Simply analyzing EEG data in Brain-Computer Interfaces in the time domain only gives you half the story. Depending on the task, the brain creates specific neural oscillations:
- Close your eyes and see strong 8-12Hz alpha waves in the occipital area.
- Open your eyes and notice how the oscillation decreases (alpha blocking).

Imagine moving your right hand and notice how betas and mus become weak in the opposite motor cortex (near electrode C3 on the left hemisphere)

A Fourier Transform would indicate that this data contained beta or alpha waves somewhere in the data. However, it would not indicate:
- When this occurred
- How long it lasted
- How it evolved following a stimulus

With this application, you can view both domains simultaneously by loading EEG data, performing actual mathematical decompositions (STFT, Multitaper, Wavelets), adjusting how to balance time and frequency resolution, and examining the resulting time-frequency plots.

---
## Navigation Overview

Using the navigation on the sidebar you can navigate to:

1. **Overview** - A summary of Module 5 within the overall BCI course. Also includes a cheat sheet for common EEG frequencies (Delta, Theta, Alpha, Beta, Gamma).

2. **EEG Data** - Choose from pre-loaded datasets or choose to import your own EEG data.

3. **Time-Frequency Explorer** - Primary area to explore the data. Includes graphs of waveforms and spectrograms (linked), a graph showing how band power changes, and the ability to compare using 3 different methods side-by-side using sliders to adjust the parameters.

4. **Learn the Concepts** - Includes answers to 15 common question about signal processing. Also includes a Parameter Playground.

5. **Knowledge Check** - A quiz with 10 questions (multiple choice) to assess your knowledge before submitting your lab report.

6. **Export Results** - Export current analysis parameters as JSON, create a Python code file to re-create your graphs elsewhere, or export the spectral power matrix as CSV.

7. **About** - Information regarding the project, how this relates to the overall course, and sources.
---

## Step-by-Step Lab Walkthrough

### Step 1: Launch the Application

First, ensure you are using the correct virtual environment. In your terminal, navigate to the project folder and launch Streamlit:

```bash
streamlit run app.py
```

Your browser should automatically open at `http://localhost:8501`. If it does not, please copy and paste this into Firefox or Chrome.

---

### Step 2: Choose or Upload EEG Data

In the sidebar, click on **EEGData**. Here you can either select from two pre-made synthetic data sets or upload your own data.

Option A: Alpha Blocking Benchmark (Default)

- **Signal:** A 30-second sample at 256Hz using 10 channels with realistic 1/f pink noise.
- **What to look for:** Focus on electrode `Oz`. Between 0-10 seconds (eyes closed), you should see a strong 10Hz rhythm. Between 10-20 seconds (eyes open), this rhythm should break down. Between 20-30 seconds (eyes closed), the rhythm should return.
- **Best electrodes to examine:* `Oz`, `O1`, `O2`

Option B: Motor Imagination Benchmark

- **Signal:** A 20-second sample at 256Hz using 6 channels (`F3`, `F4`, `C3`, `Cz`, `C4`, `Pz`).

- **What to look for:**

- When imagining using your left hand (between 5-10 seconds), observe electrode `C4` (opposite side, right motor cortex) to see a reduction in both beta (22Hz) and a dip in mu (11Hz) power.

- When imagining using your right hand (between 15-20 seconds), observe electrode `C3` (opposite side, left motor cortex) to see the same reduction.

- **Best electrodes to examine:** `C3` vs `C4`

Option C: Upload an External EEG File

- If you were provided with your own EEG file by your instructor, select “UploadFile”
- Accepted file formats include:
  - `.edf` (European Data Format)
  - `.fif` (native format for MNE-Python)
  - `.vhdr` (BrainVision header file - keep your `.vmrk` and `.eeg` files in the same folder)
  - `.set` (EEGLAB format)
  - `.csv` (tabular format - you will need to specify the sampling rate and choose which column contains your voltage and time data
---

### Step 3: Run Time-Frequency Decomposition

From the sidebar, navigate to the **Time-Frequency Explorer** page.

#### 1. Choose your Channel and Time Window

- Using the **SignalandChannel** dropdown in the sidebar, select the desired electrode (use `Oz` for alpha related tasks and `C3`/`C4` for motor imagery tasks).
- If you only want to analyze a section of the data, use the **TimeWindow** slider.

#### 2. Choose your Method

Select which type of time-frequency analysis you would like to perform:

- **Morlet Wavelets:** Multiply your data by a Gaussian-windowed complex sine wave.

- **Key control:** Wavelet Cycles (`n_cycles`).

- Using fewer cycles (around 3-5) will create narrower wavelets that provide more precise time-based information but spread out frequencies. Using more cycles (around 8-12) will create wider wavelets with more precise frequency information but may become blurry when determining when a signal begins or ends.

- Using 7 cycles is recommended as a default.

- **Multitaper Method:** This method utilizes many orthogonal discrete prolate spheroidal sequences (DPSS) as tapers.

- **Key control:** Time-Bandwidth Product (`NW`). 

- Using a high value will average over more orthogonal tapers, significantly lowering variance and random noise (though this may slightly blur frequencies).

- **Short-Time Fourier Transform (STFT):** Place a fixed window over the data and calculate a discrete Fourier transform for each window.

- **Key controls:** Window Function (Blackman, Hamming, Hann), Overlap, and Window Length. 

- Using a short window will allow for the detection of quick time changes, while using a longer window will allow for the separation of nearby frequencies.

####  3.Frequency Limits and Grid Granularity


- Input **MinFrequency** (e.g.,1.0Hzor4.0Hz)and **MaxFrequency** (e.g.,30.0Hzor40.0Hz). The tool will ensure that `f_max` does not surpass the Nyquist rate `f_s/2`).
- Use the **FrequencyPoints** slider to select how many vertical frequency bins will be analyzed.
  
#### 4.BaselineCorrection(CrucialforERD/ERS)
  
  Since EEG generally follows a 1/f power law, raw spectral power is often dominated by low frequencies. To reveal frequency changes related to a task:
  
- Select **BaselineMode** as either `db` (Decibels: `10log₁₀(P/P_base)`*) or* `percent`.
- Define the **BaselineInterval** as a pre-stimulus or resting period (e.g., 0.0s to 4.0s).
- On the resulting spectrogram, negative values indicate ERD (desynchronization) and positive values indicate ERS (synchronization).

---
  ### Step4: InterpretingtheVisualizations
####   TheSynchronizedLinkedPlots
- **TopPlot(VoltageTrace)**: Shows the raw EEG signal in microvolts (μV). A bounding box highlights the time period being analyzed, while vertical lines indicate experimentally-defined events.
- **BottomPlot(Spectrogram)**: Visualizes power across both frequency and time.
- **HoverInspection**: When you hover over any point on either plot, you can see the precise frequency, time, and baseline-corrected power.
- **SynchronizedZoom**: Using either plot’s Plotly zoom or pan tools will synchronize the two plots since they both use the same time axis to keep events aligned.

####   MethodComparisonTab
  
  Below the main plot, you can switch between:
- **SingleMethodView**: A detailed spectrogram with numerous settings you can adjust.
- **MethodComparisonView**: Calculates and visualizes both STFT, Multitaper, and Morlet on the same plot side-by-side to compare how different wavelet/Window cycle settings affect data resolution.
####   BandPowerTrajectories
  To see how different frequency bands (Delta, Theta, Alpha, Beta, Gamma) change over time, expand the **Clinical Frequency Band Trajectories**
  
---
###   Step5: ConceptCheckandQuiz
- **Learn the Concepts**: Click the accordion to view the theory questions. Using the interactive **ParameterPlayground**, you can adjust various sliders and see a plain-language explanation of how different settings affect time or frequency resolution.
- **KnowledgeCheck**: Complete a 10-question multiple choice test. After submitting your answers, you will instantly get scored and receive detailed scientific feedback telling you why each response is right or wrong.

---
###   Step6: ExportingDeliverablesforYourLabReport
  Once you have identified suitable parameters that effectively isolate the desired neural oscillation, go to **ExportResults**:
  
  1.**Parameters(.json):** This exports all selected method, window, and filter settings in a well-formatted JSON document that you can include as an appendix to your report.\
  2.**StandalonePythonScript(.py):** This will download a runnable `.py` file that uses NumPy and MNE to regenerate your plots offline without using the Streamlit application.\
  3.**PowerMatrix(.csv):** This exports a 2D numerical power matrix (each row represents a time point, while each column represents a frequency). You can use this data in Excel, MATLAB, or Python to perform statistical analysis.