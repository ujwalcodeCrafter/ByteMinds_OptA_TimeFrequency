"""
NeuroLab Guided Learning Activities - Experiment Lab.

Interactive guided laboratory experiments:
1. Alpha Blocking (Eyes-Closed vs Eyes-Open)
2. Motor Imagery (Sensorimotor Mu/Beta ERD/ERS)
3. Time-Frequency Resolution Trade-off
"""
import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from core.sample_data import generate_sample_eeg, generate_motor_imagery_data
from core.time_frequency import compute_morlet_tfr, compute_stft, apply_baseline_correction
from core.band_power import compute_band_power, FREQUENCY_BANDS


def render_experiment_lab():
    """Render the guided experiments section."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">🧪 Experiment Lab: Guided Scientific Studies</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Step through three structured neuroscience experiments to experience how oscillatory
            brain rhythms respond to sensory input, cognitive motor intent, and mathematical analysis parameters.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    experiment = st.selectbox(
        "Select an Experiment to Conduct:",
        [
            "🔬 Experiment 1: Occipital Alpha Blocking (Eyes-Closed vs. Eyes-Open)",
            "🧠 Experiment 2: Sensorimotor Motor Imagery (Mu & Beta ERD/ERS)",
            "⚖️ Experiment 3: Heisenberg Resolution Trade-off (Wavelets vs. STFT)"
        ]
    )
    
    if "Experiment 1" in experiment:
        _render_experiment_alpha_blocking()
    elif "Experiment 2" in experiment:
        _render_experiment_motor_imagery()
    elif "Experiment 3" in experiment:
        _render_experiment_resolution_tradeoff()


def _render_experiment_alpha_blocking():
    """Guided Experiment 1: Alpha Blocking."""
    st.markdown("""
    ### 🔬 Experiment 1: Occipital Alpha Blocking
    **Objective:** Investigate how opening and closing the eyes dramatically modulates 10 Hz alpha oscillatory power over visual cortex.
    
    > ℹ️ **Dataset Notice:** This experiment uses a simulated EEG dataset synthesized with known physiological ground truth (10 Hz oscillation suppressed between 10.0s and 20.0s) for repeatable educational learning.
    """)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        channel = st.selectbox("Electrode Site", ["Oz", "O1", "O2", "Fz", "Cz"], index=0,
                               help="Oz/O1/O2 lie directly above primary visual cortex.")
    with col2:
        method = st.selectbox("Method", ["morlet", "stft"], format_func=lambda x: "Morlet Wavelet" if x == "morlet" else "STFT")
    with col3:
        baseline = st.checkbox("Apply dB Baseline Correction (0–5s)", value=True)
        
    # Generate data
    raw = generate_sample_eeg(duration=30.0, sfreq=256.0)
    sfreq = raw.info['sfreq']
    ch_idx = raw.ch_names.index(channel)
    data = raw.get_data()[ch_idx]
    times = raw.times
    
    # Compute TF
    with st.spinner("Computing time-frequency representation..."):
        if method == "morlet":
            power, freqs, tfr_times = compute_morlet_tfr(
                data, sfreq=sfreq, fmin=4.0, fmax=30.0, n_freqs=35, n_cycles=7.0
            )
        else:
            power, freqs, tfr_times = compute_stft(
                data, sfreq=sfreq, window_length=256, overlap=192, fmin=4.0, fmax=30.0
            )
            
        if baseline:
            power_disp = apply_baseline_correction(power, tfr_times, baseline=(0.0, 5.0), mode='db')
            cbar_label = "Relative Power (dB)"
        else:
            power_disp = power
            cbar_label = "Raw Power (V²/Hz)"

    # Compute Alpha power trace over time
    alpha_power = compute_band_power(power, freqs, band_name='Alpha')
    
    # Plotting
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.07,
        subplot_titles=(
            f'Raw EEG Waveform — Channel {channel}',
            f'Time-Frequency Spectrogram ({method.capitalize()})',
            'Occipital Alpha Band Power (8–13 Hz) Trajectory'
        ),
        row_heights=[0.25, 0.45, 0.30]
    )
    
    # 1. Waveform
    fig.add_trace(
        go.Scatter(x=times, y=data * 1e6, mode='lines', line=dict(color='#00BCD4', width=1), name='EEG (µV)'),
        row=1, col=1
    )
    
    # Condition shading
    conditions = [
        (0.0, 10.0, 'Eyes Closed', 'rgba(76, 175, 80, 0.15)'),
        (10.0, 20.0, 'Eyes Open (Alpha Block)', 'rgba(244, 67, 54, 0.15)'),
        (20.0, 30.0, 'Eyes Closed (Recovery)', 'rgba(76, 175, 80, 0.15)')
    ]
    for onset, offset, label, col in conditions:
        for r in [1, 2, 3]:
            fig.add_vrect(x0=onset, x1=offset, fillcolor=col, layer='below', line_width=0, row=r, col=1)
        fig.add_annotation(x=(onset + offset)/2, y=1.05, text=label, showarrow=False,
                           font=dict(color='#ECEFF1', size=11), xref='x', yref='y domain', row=1, col=1)
            
    # 2. Spectrogram
    fig.add_trace(
        go.Heatmap(x=tfr_times, y=freqs, z=power_disp, colorscale='RdYlBu_r',
                   colorbar=dict(title=dict(text=cbar_label, side='right'), len=0.45, y=0.5)),
        row=2, col=1
    )
    
    # 3. Alpha power
    t_alpha = np.linspace(times[0], times[-1], len(alpha_power))
    fig.add_trace(
        go.Scatter(x=t_alpha, y=alpha_power, mode='lines', line=dict(color='#51CF66', width=2.5),
                   name='Alpha Power', fill='tozeroy', fillcolor='rgba(81, 207, 102, 0.2)'),
        row=3, col=1
    )
    
    fig.update_layout(
        height=800, template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)', plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5'), showlegend=False, margin=dict(l=60, r=30, t=50, b=40)
    )
    fig.update_yaxes(title_text='µV', row=1, col=1)
    fig.update_yaxes(title_text='Hz', row=2, col=1)
    fig.update_yaxes(title_text='Alpha Power', row=3, col=1)
    fig.update_xaxes(title_text='Time (s)', row=3, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Observations & Takeaways
    st.markdown("""
    #### 🔍 What to Observe:
    1. **At Occipital Sites (Oz, O1, O2):** A strong horizontal band of concentrated energy appears around **10 Hz** during 0–10s (eyes closed).
    2. **At Second 10.0 (Eyes Open):** The 10 Hz band immediately extinguishes. Notice how the bottom band power plot plummets by >75%.
    3. **At Second 20.0 (Eyes Closed Again):** Alpha rhythm rebounds promptly.
    4. **Electrode Comparison:** Switch the electrode from `Oz` to `Fz` or `Cz`. Notice how alpha blocking is substantially attenuated over frontal and central sites, demonstrating spatial specificity!
    
    #### 💡 Scientific Explanation:
    Hans Berger discovered this phenomenon in 1929. The occipital alpha rhythm is generated when the visual cortex is disengaged from active visual computation (cortical idling / sensory gating). When eyes open, thalamocortical inputs flood the primary visual cortex, causing pyramidal cells to desynchronize their collective firing to process complex visual stimuli.
    
    **BCI Key Takeaway:** Alpha blocking can be used as a voluntary, low-effort binary BCI switch (e.g. for emergency call alarms or simple menu selection).
    """)


def _render_experiment_motor_imagery():
    """Guided Experiment 2: Sensorimotor Motor Imagery ERD/ERS."""
    st.markdown("""
    ### 🧠 Experiment 2: Sensorimotor Motor Imagery (Mu & Beta ERD/ERS)
    **Objective:** Observe Event-Related Desynchronization (ERD) in sensorimotor rhythms (Mu ~11 Hz and Beta ~22 Hz) during imagined left-hand vs. right-hand movements.
    
    > ℹ️ **Dataset Notice:** This experiment uses a simulated motor imagery EEG dataset (electrodes C3, Cz, C4 over primary motor cortex) with contralateral ERD ground truth.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        task_focus = st.radio("Focus Comparison:", ["Compare C3 (Left Cortex) vs C4 (Right Cortex)", "Inspect Single Channel"], horizontal=True)
    with col2:
        baseline_opt = st.checkbox("Baseline Normalization (dB relative to Rest 0–5s)", value=True)
        
    raw = generate_motor_imagery_data(duration=20.0, sfreq=256.0)
    sfreq = raw.info['sfreq']
    
    # Compute for C3 and C4
    c3_data = raw.get_data()[raw.ch_names.index('C3')]
    c4_data = raw.get_data()[raw.ch_names.index('C4')]
    
    p_c3, freqs, t_tfr = compute_morlet_tfr(c3_data, sfreq=sfreq, fmin=5.0, fmax=35.0, n_freqs=35, n_cycles=7.0)
    p_c4, _, _ = compute_morlet_tfr(c4_data, sfreq=sfreq, fmin=5.0, fmax=35.0, n_freqs=35, n_cycles=7.0)
    
    if baseline_opt:
        p_c3_disp = apply_baseline_correction(p_c3, t_tfr, baseline=(0.5, 4.5), mode='db')
        p_c4_disp = apply_baseline_correction(p_c4, t_tfr, baseline=(0.5, 4.5), mode='db')
        cbar_title = "ERD/ERS (dB)"
    else:
        p_c3_disp = p_c3
        p_c4_disp = p_c4
        cbar_title = "Power (V²/Hz)"
        
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        subplot_titles=('C3 (Left Motor Cortex — Controls Right Hand)', 'C4 (Right Motor Cortex — Controls Left Hand)'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Heatmap(x=t_tfr, y=freqs, z=p_c3_disp, colorscale='RdBu_r', zmid=0 if baseline_opt else None,
                   colorbar=dict(title=dict(text=cbar_title, side='right'), len=0.45, y=0.75)),
        row=1, col=1
    )
    fig.add_trace(
        go.Heatmap(x=t_tfr, y=freqs, z=p_c4_disp, colorscale='RdBu_r', zmid=0 if baseline_opt else None,
                   colorbar=dict(title=dict(text=cbar_title, side='right'), len=0.45, y=0.25)),
        row=2, col=1
    )
    
    intervals = [
        (0.0, 5.0, 'Rest Baseline', 'rgba(120, 144, 156, 0.1)'),
        (5.0, 10.0, 'Left Hand Imagery (C4 Active)', 'rgba(233, 30, 99, 0.15)'),
        (10.0, 15.0, 'Rest Recovery', 'rgba(120, 144, 156, 0.1)'),
        (15.0, 20.0, 'Right Hand Imagery (C3 Active)', 'rgba(156, 39, 176, 0.15)')
    ]
    for onset, offset, label, col in intervals:
        for r in [1, 2]:
            fig.add_vrect(x0=onset, x1=offset, fillcolor=col, layer='below', line_width=0, row=r, col=1)
        fig.add_annotation(x=(onset + offset)/2, y=1.05, text=label, showarrow=False,
                           font=dict(color='#ECEFF1', size=11), xref='x', yref='y domain', row=1, col=1)
            
    fig.update_layout(
        height=650, template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)', plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5'), margin=dict(l=60, r=30, t=50, b=40)
    )
    fig.update_yaxes(title_text='Hz', row=1, col=1)
    fig.update_yaxes(title_text='Hz', row=2, col=1)
    fig.update_xaxes(title_text='Time (s)', row=2, col=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    #### 🔍 What to Observe:
    - **Interval 5–10s (Left Hand Imagery):**
      - Notice the deep blue depression (negative dB = ERD) around 11 Hz and 22 Hz on **C4** (contralateral right hemisphere).
      - Meanwhile, **C3** displays neutral or slightly positive power (ERS / idling).
    - **Interval 15–20s (Right Hand Imagery):**
      - The pattern mirrors! **C3** exhibits pronounced ERD (blue cooling) while **C4** remains stable.
      
    #### 💡 Scientific Explanation:
    The motor cortex is crossed: the right cerebral hemisphere controls the left limbs, and the left hemisphere controls the right limbs. Mental rehearsal of motor action (motor imagery) activates sensorimotor neural assemblies identically to physical execution, desynchronizing idling mu (~11 Hz) and beta (~22 Hz) rhythms.
    
    **BCI Key Takeaway:** This contralateral ERD contrast is the foundational feature extracted by Common Spatial Patterns (CSP) and classifiers in motor neuroprosthetics and wheelchair navigation.
    """)


def _render_experiment_resolution_tradeoff():
    """Guided Experiment 3: Resolution Trade-off."""
    st.markdown("""
    ### ⚖️ Experiment 3: The Time-Frequency Resolution Trade-off
    **Objective:** Empirically demonstrate the Heisenberg-Gabor uncertainty bound in signal processing by comparing Morlet Wavelet cycle lengths and STFT window sizes on an identical signal.
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🌊 Morlet Wavelet Cycles ($n_{cycles}$)")
        n_cycles_test = st.select_slider("Choose Wavelet Cycles:", options=[3.0, 7.0, 16.0], value=7.0)
    with col2:
        st.markdown("#### ⏱️ STFT Window Length ($N_{perseg}$)")
        win_len_test = st.select_slider("Choose STFT Window Samples:", options=[64, 256, 512], value=256)
        
    raw = generate_sample_eeg(duration=15.0, sfreq=256.0)
    sfreq = raw.info['sfreq']
    data = raw.get_data()[raw.ch_names.index('Oz')]
    
    # Compute both
    p_wavelet, freqs_w, t_w = compute_morlet_tfr(data, sfreq=sfreq, fmin=4.0, fmax=30.0, n_freqs=40, n_cycles=n_cycles_test)
    p_stft, freqs_s, t_s = compute_stft(data, sfreq=sfreq, window_length=win_len_test, overlap=win_len_test//2, fmin=4.0, fmax=30.0)
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f'Morlet Wavelets (Cycles = {n_cycles_test})',
            f'STFT (Window = {win_len_test} samples = {win_len_test/sfreq:.2f}s)'
        ),
        horizontal_spacing=0.08
    )
    
    fig.add_trace(
        go.Heatmap(x=t_w, y=freqs_w, z=p_wavelet, colorscale='Viridis', showscale=False),
        row=1, col=1
    )
    fig.add_trace(
        go.Heatmap(x=t_s, y=freqs_s, z=p_stft, colorscale='Viridis', showscale=False),
        row=1, col=2
    )
    
    fig.update_layout(
        height=450, template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)', plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5'), margin=dict(l=50, r=20, t=50, b=40)
    )
    fig.update_yaxes(title_text='Frequency (Hz)', row=1, col=1)
    fig.update_xaxes(title_text='Time (s)', row=1, col=1)
    fig.update_xaxes(title_text='Time (s)', row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown(f"""
    #### 🔬 Comparison & Diagnosis:
    - **Wavelet with {n_cycles_test} cycles:**
      {'Notice the wide vertical smearing of frequency bands, but sharp temporal precision (burst boundaries are well preserved).' if n_cycles_test <= 4 else ('Notice how sharply defined the 10 Hz alpha band is, but time boundaries at second 10 bleed horizontally.' if n_cycles_test >= 14 else 'Balanced time and frequency representation suitable for general EEG exploration.')}
    - **STFT with {win_len_test} samples ({win_len_test/sfreq:.2f} seconds):**
      {'Short window produces wide horizontal bands (frequency bins are coarse: Δf = 4.0 Hz).' if win_len_test <= 64 else ('Long window provides crisp 0.5 Hz frequency resolution, but temporal changes take 2 seconds to transition (blocky in time).' if win_len_test >= 512 else 'Standard compromise between 1 Hz frequency bins and 1.0s windowing.')}
      
    **Key Takeaway:** There is no universally 'optimal' parameter setting. Analysis parameters must be chosen based on whether your research question asks **when** an event happened (use fewer cycles / shorter window) or **at what exact frequency** resonance occurred (use more cycles / longer window).
    """)
