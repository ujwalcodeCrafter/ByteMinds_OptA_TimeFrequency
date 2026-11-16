"""
Time-Frequency Educational Content - Explain Panel.

Comprehensive explanations of time-frequency analysis concepts for BCI students,
including fundamental principles, mathematical intuition, and an interactive Parameter Playground.
"""
import streamlit as st


def render_explain_panel(current_params=None):
    """
    Render the complete educational content section.
    
    Parameters
    ----------
    current_params : dict, optional
        Currently active analysis parameters for contextual explanations.
    """
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">Understand the Science</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Master the core concepts of EEG Time-Frequency Analysis in Brain-Computer Interfaces.
            Explore theoretical foundations, method comparisons, and intuitive parameter effects.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # If parameters are supplied, display live contextual insights
    if current_params:
        _render_contextual_parameter_insight(current_params)
    
    tab1, tab2, tab3 = st.tabs([
        "EEG & TFA Fundamentals",
        "Time-Frequency Methods",
        "Parameter Playground & Resolution"
    ])
    
    with tab1:
        _render_eeg_fundamentals()
    with tab2:
        _render_method_explanations()
    with tab3:
        _render_parameter_playground(current_params)


def _render_contextual_parameter_insight(params):
    """Display real-time educational feedback on the user's current settings."""
    method = params.get('method', 'morlet')
    fmin = params.get('fmin', 1.0)
    fmax = params.get('fmax', 40.0)
    sfreq = params.get('sfreq', 256.0)
    baseline_mode = params.get('baseline_mode', None)
    
    insights = []
    
    if method == 'morlet':
        n_cycles = params.get('n_cycles', 7.0)
        if n_cycles <= 4.0:
            insights.append("**Low Morlet Cycles (≤ 4):** Prioritizing precise timing of transients at the cost of broader frequency smearing.")
        elif n_cycles >= 12.0:
            insights.append("**High Morlet Cycles (≥ 12):** Sharply tuned frequency bands, but transient events will be smoothed out over time.")
        else:
            insights.append(f"**Balanced Cycles ({n_cycles}):** Standard compromise between temporal and frequency resolution across alpha/beta bands.")
    elif method == 'stft':
        wlen = params.get('window_length', 256)
        dt_win = wlen / sfreq
        df_bin = sfreq / wlen
        insights.append(f"**STFT Window:** {wlen} samples = {dt_win:.2f}s temporal window width, yielding {df_bin:.2f} Hz frequency bin spacing.")
    elif method == 'multitaper':
        tbw = params.get('time_bandwidth', 4.0)
        n_tapers = max(1, int(2 * tbw - 1))
        insights.append(f"**Multitaper Smoothing:** Time-Bandwidth Product = {tbw} uses ~{n_tapers} orthogonal DPSS tapers to suppress variance.")
        
    if baseline_mode:
        insights.append(f"**Baseline Correction Active ({baseline_mode}):** Visualizing task-induced event-related perturbations relative to reference power.")
    else:
        insights.append("**Raw Power Displayed:** 1/f spectral slope dominates; lower frequencies naturally carry higher raw amplitudes.")
        
    with st.expander("Live Parameter Diagnostics & Insights", expanded=True):
        st.markdown(f"**Current Configuration:** `{method.upper()}` | Freq: `{fmin}–{fmax} Hz` | Channel: `{params.get('channel', 'N/A')}`")
        for item in insights:
            st.markdown(f"- {item}")


def _render_eeg_fundamentals():
    with st.expander("1. What is EEG?", expanded=True):
        st.markdown("""
        **Electroencephalography (EEG)** is the recording of electrical activity originating from synchronous post-synaptic potentials in cortical pyramidal neurons via electrodes placed on the scalp.
        
        - **Voltage Scale:** Measured in microvolts (µV), typically 10–100 µV in healthy adults.
        - **Temporal Resolution:** Milliseconds (sub-millisecond sampling), ideal for tracing cognitive dynamics.
        - **Spatial Resolution:** Centimeters, limited by volume conduction through the cerebrospinal fluid, skull, and scalp.
        - **BCI Relevance:** Non-invasive, portable, millisecond-accurate sensorimotor and cognitive telemetry.
        """)
        
    with st.expander("2. What is Time-Frequency Analysis (TFA)?", expanded=True):
        st.markdown("""
        Time-Frequency Analysis decomposes a non-stationary signal simultaneously into:
        
        1. **TIME (t):** Exactly *when* neural events or rhythm changes occur.
        2. **FREQUENCY (f):** *Which* underlying oscillatory network is firing (e.g. 10 Hz alpha, 22 Hz beta).
        3. **POWER (P):** *How strong* or synchronized the neuronal population activity is ($V^2 / \\text{Hz}$ or relative scale).
        
        While time-series plots reveal amplitude envelopes and classical Fourier transforms reveal aggregate spectral peaks, **TFA reveals the dynamic temporal trajectory of oscillatory power**.
        """)
        
    with st.expander("3. Why is Ordinary FFT Not Sufficient for EEG?"):
        st.markdown("""
        Classical **Fast Fourier Transform (FFT)** integrates over the entire recording duration under the mathematical assumption of **stationarity** (spectral properties invariant over time):
        
        $$X(f) = \\int_{-\\infty}^{\\infty} x(t) e^{-j 2\\pi f t} dt$$
        
        **The Problem in EEG:**
        - Brain signals are inherently **non-stationary**: motor preparation produces brief 500ms beta desynchronizations, visual saccades evoke transient bursts, and opening the eyes suppresses alpha within 200ms.
        - An FFT across a 10-second window calculates an *average spectrum*. It cannot tell whether a 10 Hz rhythm occurred in the first 2 seconds, throughout, or as a burst at second 7.
        - **Time-frequency decomposition preserves causality and temporal sequencing.**
        """)

    with st.expander("4. What is a Spectrogram?"):
        st.markdown("""
        A **spectrogram** is a 2D intensity map of spectral energy:
        - **Horizontal Axis (X):** Time in seconds ($s$).
        - **Vertical Axis (Y):** Frequency in Hertz ($Hz$).
        - **Color Dimension (Z):** Power / Power Spectral Density. Warm colors (red/yellow) indicate synchronized oscillatory power; cool colors (blue) denote baseline suppression or low power.
        """)

    with st.expander("5. Physiological EEG Frequency Bands"):
        st.markdown("""
        Scalp oscillations reflect synchronized thalamocortical and corticocortical loops:
        
        | Band | Frequency Range | Characteristic Neural State | Typical Scalp Loci | BCI Application |
        |---|---|---|---|---|
        | **Delta** | 0.5 – 4 Hz | Slow-wave deep sleep (N3), unconsciousness | Frontal / Global | Sleep staging, depth of anesthesia |
        | **Theta** | 4 – 8 Hz | Drowsiness, memory consolidation, mental fatigue | Frontal midline (Fz) | Cognitive workload & alertness indices |
        | **Alpha** | 8 – 13 Hz | Relaxed wakefulness, sensory gating | Occipital (Oz, O1, O2) | Alpha-blocking, relaxation feedback, BCI switch |
        | **Beta** | 13 – 30 Hz | Active processing, alertness, motor inhibition | Sensorimotor (C3, Cz, C4) | Motor imagery BCI (mu/beta ERD/ERS) |
        | **Gamma** | 30 – 100 Hz | Local cross-modal binding, selective attention | Distributed | Cognitive intent, high-rate invasive BCI |
        
        > **Scientific Caveat:** Bands reflect continuous biological spectra. No single band is an exclusive biomarker of a discrete mental state.
        """)

    with st.expander("6. Event-Related Desynchronization (ERD) & Synchronization (ERS)"):
        st.markdown("""
        Introduced by Pfurtscheller & Lopes da Silva (1999):
        - **ERD (Desynchronization):** A decrease in oscillatory band power relative to pre-stimulus baseline. Reflects active cortical processing where neuronal populations desynchronize to perform computation (e.g. motor planning decreases sensorimotor mu/beta power).
        - **ERS (Synchronization):** An increase in band power. Often indicates cortical idling, active sensory inhibition, or post-movement rebound.
        - **In Motor Imagery BCI:** Imagining right-hand clenching triggers contralateral left hemisphere (electrode C3) mu/beta ERD, accompanied by ipsilateral (C4) preservation or ERS.
        """)

    with st.expander("7. Alpha Blocking (Berger Effect)"):
        st.markdown("""
        Discovered by Hans Berger (1929):
        - **Eyes Closed:** In the absence of visual input, visual cortex neurons oscillate synchronously at ~10 Hz (occipital alpha rhythm).
        - **Eyes Open:** Visual sensory input floods the occipital cortex. Pyramidal neurons engage in parallel visual processing, shattering synchronous resonance. Occipital alpha power precipitously drops within 150–300ms.
        - Observe this directly in our **Alpha Blocking Sample Dataset** (channels Oz, O1, O2).
        """)


def _render_method_explanations():
    with st.expander("1. Morlet Wavelet Transform (Continuous Wavelet Transform)", expanded=True):
        st.markdown("""
        A **Morlet wavelet** consists of a complex sinusoidal carrier wave multiplied by a Gaussian window:
        
        $$\\psi(t, f) = A \\cdot e^{-t^2 / (2 \\sigma_t^2)} \\cdot e^{j 2\\pi f t}$$
        
        Where the standard deviation $\\sigma_t$ is determined by frequency $f$ and chosen number of cycles $m$:
        
        $$\\sigma_t = \\frac{m}{2\\pi f}, \\quad \\sigma_f = \\frac{1}{2\\pi \\sigma_t} = \\frac{f}{m}$$
        
        **Key Features:**
        - **Frequency-Adaptive Resolution:** At low frequencies, wavelets span longer time windows (high frequency resolution, coarse time resolution). At high frequencies, wavelets contract in time (high time resolution, coarse frequency resolution).
        - **Natural Match for EEG:** Slow oscillations (e.g. 2 Hz delta) require long durations to define cycles, whereas high-frequency gamma bursts (60 Hz) occur in brief tens-of-milliseconds transients.
        """)

    with st.expander("2. Multitaper Time-Frequency Analysis"):
        st.markdown("""
        Developed by David Thomson (1982), **Multitaper Spectral Estimation** replaces a single tapering window with a family of orthogonal Discrete Prolate Spheroidal Sequences (DPSS / Slepian sequences):
        
        - **The Mechanism:** The signal is windowed by multiple mutually orthogonal DPSS tapers. An individual eigenspectrum is computed for each taper, and the spectra are averaged:
          $$\\hat{S}(f) = \\frac{1}{K} \\sum_{k=1}^K |X_k(f)|^2$$
        - **Time-Bandwidth Product ($NW$):** Governs spectral leakage vs. resolution. The number of optimal orthogonal tapers used is:
          $$K = \\lfloor 2NW \\rfloor - 1$$
        - **BCI Advantage:** Significantly reduces the variance of spectral power estimates compared to standard STFT, eliminating spurious noise spikes in task classification.
        """)

    with st.expander("3. Short-Time Fourier Transform (STFT)"):
        st.markdown("""
        STFT slides a deterministic window function $w(t)$ (e.g. Hann, Hamming, Blackman) across the signal, performing discrete Fourier transforms on overlapping chunks:
        
        $$STFT\\{x(t)\\}(\\tau, f) = \\int_{-\\infty}^{\\infty} x(t) w(t - \\tau) e^{-j 2\\pi f t} dt$$
        
        - **Fixed Grid Limitation:** The window length $N_{perseg}$ is identical for all frequencies. If $N_{perseg} = 256$ at 256 Hz, your time resolution is permanently 1 second and frequency resolution is 1 Hz, regardless of whether you look at 2 Hz or 40 Hz.
        - **Overlap:** Moving the window by fractions of its length (typically 50% to 75% overlap) smoothens the spectrogram temporally.
        """)

    with st.expander("4. Head-to-Head Method Comparison"):
        st.markdown("""
        | Criterion | Morlet Wavelet | Multitaper | STFT |
        |---|---|---|---|
        | **Resolution Behavior** | Adaptive ($Q = f/\\Delta f = \\text{const}$) | Adaptive / Windowed with multi-tapers | Rigid fixed grid ($N_{perseg}$) |
        | **Variance / Noise** | Moderate | **Lowest (Optimal)** | Highest |
        | **Transient Detection** | Excellent at high frequencies | Good | Uniform across frequencies |
        | **Computational Speed** | Fast (FFT convolution) | Moderate (Multiple tapers per chunk) | Extremely Fast |
        | **Primary BCI Usage** | Single-trial ERP/ERD dynamics | Continuous power spectral tracking | Real-time low-latency spectrograms |
        """)


def _render_parameter_playground(current_params):
    st.markdown("""
    ### Parameter Playground: Cause & Effect
    Understand how turning knobs in signal processing alters your scientific representation.
    """)
    
    questions = {
        "What happens when you increase Morlet Wavelet Cycles ($m$)?": """
**Scientific Trade-off:**
- **Increasing Cycles (e.g., $m = 3 \\to 14$):**
  - $\\sigma_t = m / (2\\pi f)$ increases $\\to$ Wavelet spreads wider in time.
  - $\\sigma_f = f / m$ decreases $\\to$ Frequency resolution sharpens substantially.
  - **Visual Effect:** Frequency bands appear razor-sharp horizontally, but transient temporal onsets (like motor bursts) blur and bleed along the time axis.
- **Decreasing Cycles (e.g., $m = 3$):**
  - Excellent time localization (catches the exact millisecond of a spike), but alpha and theta will blur vertically across each other.
""",
        "What happens when you adjust STFT Window Length ($N_{perseg}$)?": """
**The Gabor-Heisenberg Uncertainty Bound:** $\\Delta t \\cdot \\Delta f \\ge \\frac{1}{4\\pi}$.
- **Long Window (e.g. 512 samples = 2.0s):**
  - $\\Delta f = 0.5$ Hz resolution $\\to$ Distinct separation between 9 Hz lower alpha and 11 Hz upper alpha.
  - $\\Delta t = 2.0$s temporal smearing $\\to$ Rapid changes within that 2-second window are lost.
- **Short Window (e.g. 64 samples = 0.25s):**
  - Sharp temporal edges, but $\\Delta f = 4$ Hz $\\to$ Alpha (8–13 Hz) is collapsed into barely two coarse bins.
""",
        "Why is Baseline Correction Essential for ERD/ERS Detection?": """
**Overcoming the 1/f Pink Noise Spectrum:**
Raw EEG power naturally decays following a power-law distribution ($P(f) \\propto 1/f^\\alpha$). Delta and theta carry orders of magnitude more absolute power than beta or gamma.
- **Without Baseline:** A 20% drop in beta power during motor imagery is invisible on a raw color scale dominated by low-frequency baseline power.
- **With Decibel ($10 \\log_{10}(P / P_{base})$) or Percent Change:** The steady-state background is normalized to 0, making subtle event-related fluctuations stand out vividly in positive (ERS) and negative (ERD) dB.
""",
        "How does STFT Overlap affect the Spectrogram?": """
- **High Overlap (75%–90%):** Interpolates and samples the STFT window at fine temporal steps, producing smooth visual heatmaps without temporal blockiness (though physical resolution remains bounded by window length).
- **Zero Overlap (0%):** Distinct blocky temporal bins; computationally lighter, but introduces visual discontinuities.
""",
        "What does the Multitaper Time-Bandwidth Product ($NW$) control?": """
- **Small $NW$ (e.g. 2.0):** Employs fewer tapers ($K \\approx 3$). High spectral resolution, but higher residual variance.
- **Large $NW$ (e.g. 6.0):** Employs ~11 tapers. Substantially suppresses noise and variance across single trials, but broadens spectral peaks (controlled spectral leakage).
"""
    }
    
    for title, desc in questions.items():
        with st.expander(title):
            st.markdown(desc)
