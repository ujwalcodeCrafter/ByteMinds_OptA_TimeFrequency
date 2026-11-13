"""
NeuroLab: Interactive EEG Time-Frequency Analysis Web Application
==================================================================

A comprehensive educational platform for Brain-Computer Interface (BCI) students
to master Time-Frequency Analysis in EEG signal processing.

Author: BCI Course Project Group (Module 5: Time-Frequency Analysis)
License: MIT
"""

import streamlit as st
import numpy as np
import pandas as pd
import json
import os
import datetime

# Core modules
from core.sample_data import generate_sample_eeg, get_sample_data_info, generate_motor_imagery_data
from core.data_loader import load_eeg_file, extract_data_info, save_uploaded_file
from core.preprocessing import get_channel_data
from core.time_frequency import compute_tfr, apply_baseline_correction
from core.band_power import compute_all_band_powers, FREQUENCY_BANDS, BAND_DESCRIPTIONS
from core.validation import sanitize_parameters
from core.export_utils import export_parameters_json, generate_python_script, export_power_matrix_csv

# UI Components
from components.sidebar import render_sidebar, render_analysis_controls
from components.visualizations import create_linked_plots, create_band_power_plot, create_single_eeg_plot
from components.controls import render_data_source_selector, render_dataset_info
from components.explain_panel import render_explain_panel
from components.quiz import render_quiz
from components.experiment_lab import render_experiment_lab


# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NeuroLab — EEG Time-Frequency Explorer",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Neuroscience Dashboard Styling
st.markdown("""
<style>
    /* Dark lab aesthetic */
    .stApp {
        background-color: #0a0f1d;
        color: #e0e6ed;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Headers & Accent colors */
    h1, h2, h3 {
        color: #00BCD4 !important;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    /* Cards and containers */
    .metric-card {
        background: rgba(19, 27, 46, 0.75);
        border: 1px solid rgba(0, 188, 212, 0.25);
        border-radius: 10px;
        padding: 1.25rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        margin-bottom: 1rem;
    }
    
    .band-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin-right: 6px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #00838F, #00BCD4);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #0097A7, #26C6DA);
        box-shadow: 0 4px 12px rgba(0, 188, 212, 0.4);
        transform: translateY(-1px);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #070b14;
        border-right: 1px solid rgba(0, 188, 212, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #131b2e;
        border-radius: 6px;
        color: #90caf9;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00BCD4 !important;
        color: #0a0f1d !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "raw_data" not in st.session_state:
    # Initialize with default alpha blocking sample data
    with st.spinner("Initializing NeuroLab sample EEG data..."):
        st.session_state.raw_data = generate_sample_eeg(duration=30.0, sfreq=256.0)
        st.session_state.raw_info = extract_data_info(st.session_state.raw_data)
        st.session_state.dataset_name = "Alpha Blocking Paradigm (Simulated)"
        st.session_state.is_synthetic = True

if "last_params" not in st.session_state:
    st.session_state.last_params = None

if "cached_tfr" not in st.session_state:
    st.session_state.cached_tfr = None


# -----------------------------------------------------------------------------
# Navigation & Sidebar
# -----------------------------------------------------------------------------
selected_page = render_sidebar()


# -----------------------------------------------------------------------------
# PAGE 1: OVERVIEW / LANDING
# -----------------------------------------------------------------------------
if "Overview" in selected_page:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #071526, #102a45); padding: 2.5rem; border-radius: 14px; border: 1px solid #00BCD4; margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(0, 188, 212, 0.15);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
                <span style="background: rgba(0, 188, 212, 0.2); color: #00BCD4; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; text-transform: uppercase;">
                    🎓 BCI Curriculum • Module 5 of 9
                </span>
                <h1 style="color: #ECEFF1; font-size: 2.6rem; margin: 0.8rem 0 0.3rem 0; font-weight: 700;">
                    NEUROLAB
                </h1>
                <h3 style="color: #00BCD4; font-size: 1.3rem; margin: 0; font-weight: 400;">
                    Interactive EEG Time-Frequency Analysis
                </h3>
                <p style="color: #B0BEC5; font-size: 1.05rem; margin-top: 1rem; max-width: 780px; line-height: 1.6;">
                    <em>"Discover when, where, and how brainwave activity changes."</em><br>
                    Welcome to the university Brain-Computer Interface (BCI) educational laboratory. 
                    Explore dynamic neural oscillations, evaluate time-frequency resolution trade-offs, 
                    and decode cognitive states with authentic signal-processing algorithms.
                </p>
            </div>
            <div style="text-align: right; display: none; @media (min-width: 768px) { display: block; }">
                <span style="font-size: 4rem;">🧠⚡</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_nav1, col_nav2, col_nav3 = st.columns(3)
    with col_nav1:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #00BCD4; margin-top: 0;">🔬 Time-Frequency Explorer</h4>
            <p style="color: #90A4AE; font-size: 0.9rem;">
                Run real Morlet Wavelet, Multitaper, and STFT computations with two linked live-updating plots.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_nav2:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #00BCD4; margin-top: 0;">🧪 Experiment Lab</h4>
            <p style="color: #90A4AE; font-size: 0.9rem;">
                Guided experiments on Occipital Alpha Blocking, Motor Imagery ERD/ERS, and Resolution Trade-offs.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col_nav3:
        st.markdown("""
        <div class="metric-card">
            <h4 style="color: #00BCD4; margin-top: 0;">✅ Knowledge Check</h4>
            <p style="color: #90A4AE; font-size: 0.9rem;">
                Reinforce your understanding with 10 interactive multiple-choice questions with scientific feedback.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🌈 Physiological EEG Frequency Bands Reference")
    st.markdown("Scalp EEG decomposes into distinct canonical frequency bands reflecting underlying thalamocortical networks:")
    
    cols = st.columns(5)
    band_items = list(FREQUENCY_BANDS.items())
    colors = ['#FF6B6B', '#FFA94D', '#51CF66', '#339AF0', '#CC5DE8']
    
    for i, (bname, (fmin_b, fmax_b)) in enumerate(band_items):
        desc = BAND_DESCRIPTIONS[bname]
        with cols[i]:
            st.markdown(f"""
            <div style="background: rgba(19, 27, 46, 0.85); border-top: 4px solid {colors[i]}; border-radius: 8px; padding: 1rem; height: 100%;">
                <h4 style="color: {colors[i]}; margin: 0;">{bname}</h4>
                <div style="font-size: 0.85rem; font-weight: 600; color: #ECEFF1; margin: 4px 0;">{desc['range']}</div>
                <p style="font-size: 0.8rem; color: #90A4AE; margin-bottom: 0.5rem;">{desc['states']}</p>
                <div style="font-size: 0.75rem; color: #78909C; line-height: 1.3;">{desc['note']}</div>
            </div>
            """, unsafe_allow_html=True)
            
    st.markdown("---")
    
    st.markdown("""
    ### 🎯 Why Time-Frequency Analysis Matters in BCI
    In Brain-Computer Interfaces, user intent is encoded not by static amplitudes, but by **rhythmic neural synchrony**:
    1. **Motor Imagery (Sensorimotor Rhythms):** Imagining limb movement evokes immediate *Event-Related Desynchronization (ERD)* in contralateral mu (8–13 Hz) and beta (13–30 Hz) bands over motor cortex (C3/C4).
    2. **Event-Related Potentials (ERP):** P300 target detection triggers coordinated theta-band phase resetting and burst synchronization.
    3. **Alpha-Blocking Switches:** Voluntary eyes-closed to eyes-open transitions create robust 10 Hz power modulation over visual cortex (Oz), usable as a binary control switch.
    4. **Cognitive Workload & Fatigue:** Frontal theta and parietal alpha oscillations track task engagement and drowsiness during human-machine interaction.
    """)


# -----------------------------------------------------------------------------
# PAGE 2: EEG DATA MANAGEMENT
# -----------------------------------------------------------------------------
elif "EEG Data" in selected_page:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">📊 EEG Data Management</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Load ready-to-use sample datasets or upload your own experimental EEG recordings (.edf, .fif, .vhdr, .set, .csv).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    source_type, uploaded_file, csv_params = render_data_source_selector()
    
    # Handle data loading
    if uploaded_file is not None:
        try:
            with st.spinner("Loading uploaded EEG file..."):
                temp_path = save_uploaded_file(uploaded_file)
                raw, info = load_eeg_file(temp_path, file_type=os.path.splitext(uploaded_file.name)[1].lower(), **csv_params)
                st.session_state.raw_data = raw
                st.session_state.raw_info = info
                st.session_state.dataset_name = uploaded_file.name
                st.session_state.is_synthetic = False
                st.success(f"Successfully loaded '{uploaded_file.name}' ({info['n_channels']} channels, {info['sfreq']} Hz)")
        except Exception as e:
            st.error(f"Error loading EEG file: {str(e)}")
            st.info("Falling back to built-in sample dataset.")
    elif source_type == 'motor_imagery':
        if st.session_state.dataset_name != "Motor Imagery Simulation (C3/C4)":
            with st.spinner("Generating Motor Imagery dataset..."):
                raw = generate_motor_imagery_data(duration=20.0, sfreq=256.0)
                st.session_state.raw_data = raw
                st.session_state.raw_info = extract_data_info(raw)
                st.session_state.dataset_name = "Motor Imagery Simulation (C3/C4)"
                st.session_state.is_synthetic = True
    elif source_type == 'alpha_blocking':
        if st.session_state.dataset_name != "Alpha Blocking Paradigm (Simulated)":
            with st.spinner("Generating Alpha Blocking dataset..."):
                raw = generate_sample_eeg(duration=30.0, sfreq=256.0)
                st.session_state.raw_data = raw
                st.session_state.raw_info = extract_data_info(raw)
                st.session_state.dataset_name = "Alpha Blocking Paradigm (Simulated)"
                st.session_state.is_synthetic = True

    # Display dataset metadata card
    render_dataset_info(st.session_state.raw_info, st.session_state.dataset_name, st.session_state.is_synthetic)
    
    st.markdown("### 📈 Raw EEG Signal Inspector")
    col1, col2 = st.columns([1, 3])
    with col1:
        preview_ch = st.selectbox("Select Channel to Preview:", st.session_state.raw_data.ch_names)
        st.markdown("""
        **Channel Navigation Tips:**
        - **Oz, O1, O2:** Occipital visual cortex (alpha rhythm)
        - **C3, Cz, C4:** Sensorimotor cortex (mu and beta motor imagery)
        - **Fz:** Frontal midline (theta rhythm / cognition)
        """)
    with col2:
        ch_data, times = get_channel_data(st.session_state.raw_data, preview_ch)
        fig_preview = create_single_eeg_plot(ch_data, times, preview_ch, annotations=st.session_state.raw_info.get('annotations'))
        st.plotly_chart(fig_preview, use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE 3: TIME-FREQUENCY EXPLORER (CORE ENGINE + LINKED PLOTS)
# -----------------------------------------------------------------------------
elif "Time-Frequency Explorer" in selected_page:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">🔬 Time-Frequency Explorer</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Adjust mathematical parameters in the sidebar to observe real-time recalculation
            of time-frequency representations across two synchronized, linked plots.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar parameter controls
    params = render_analysis_controls(st.session_state.raw_data)
    
    # Parameter Validation
    clean_params, val_errors = sanitize_parameters(params)
    if val_errors:
        for err in val_errors:
            st.error(f"⚠️ Validation error: {err}")
        st.stop()
        
    st.session_state.last_params = clean_params
    
    # Extract channel data
    ch_name = clean_params['channel']
    raw = st.session_state.raw_data
    sfreq = raw.info['sfreq']
    
    # Crop to selected time window if requested
    tmin, tmax = clean_params['time_range']
    data_signal, times_signal = get_channel_data(raw, ch_name)
    
    # Perform Actual Time-Frequency Computation
    with st.spinner(f"Computing {clean_params['method'].capitalize()} Time-Frequency decomposition on channel {ch_name}..."):
        try:
            # Prepare arguments for compute_tfr
            method = clean_params['method']
            tf_kwargs = {
                'fmin': clean_params['fmin'],
                'fmax': clean_params['fmax'],
                'n_freqs': clean_params['n_freqs'],
            }
            if method == 'morlet':
                tf_kwargs['n_cycles'] = clean_params.get('n_cycles', 7.0)
            elif method == 'multitaper':
                tf_kwargs['time_bandwidth'] = clean_params.get('time_bandwidth', 4.0)
            elif method == 'stft':
                tf_kwargs['window_length'] = clean_params.get('window_length', 256)
                tf_kwargs['overlap'] = clean_params.get('overlap', 128)
                tf_kwargs['window'] = clean_params.get('window_function', 'hann')
                
            power, freqs, tfr_times = compute_tfr(data_signal, sfreq, method=method, **tf_kwargs)
            
            # Apply baseline correction if selected
            if clean_params.get('baseline_mode') and clean_params.get('baseline_range'):
                power_display = apply_baseline_correction(
                    power, tfr_times, 
                    baseline=clean_params['baseline_range'], 
                    mode=clean_params['baseline_mode']
                )
            else:
                power_display = power
                
            # Store in session state for exports
            st.session_state.computed_tfr = {
                'power': power_display,
                'raw_power': power,
                'freqs': freqs,
                'times': tfr_times,
                'params': clean_params,
                'signal_data': data_signal,
                'signal_times': times_signal,
            }
            
        except Exception as e:
            st.error(f"Computation failed: {str(e)}")
            st.stop()

    # --- TWO LINKED LIVE-UPDATING PLOTS ---
    st.markdown("### 📊 Synchronized Neural Visualizations")
    st.caption("Linked view: Pan or zoom on the waveform or spectrogram; the shared temporal axis stays linked.")
    
    linked_fig = create_linked_plots(
        eeg_data=data_signal,
        eeg_times=times_signal,
        power=power_display,
        freqs=freqs,
        tfr_times=tfr_times,
        channel_name=ch_name,
        method_name=clean_params['method'].capitalize(),
        time_range=clean_params['time_range'],
        annotations=st.session_state.raw_info.get('annotations'),
        baseline_mode=clean_params.get('baseline_mode')
    )
    st.plotly_chart(linked_fig, use_container_width=True)
    
    # --- BONUS: Band Power Evolution Plot ---
    with st.expander("📈 Frequency Band Power Trajectories Over Time", expanded=True):
        st.markdown("Temporal evolution of power aggregated across standard EEG clinical bands:")
        band_powers = compute_all_band_powers(power, freqs)
        if band_powers:
            band_fig = create_band_power_plot(band_powers, tfr_times)
            st.plotly_chart(band_fig, use_container_width=True)
        else:
            st.info("Selected frequency limits do not overlap with standard EEG band ranges.")

    # Educational notes for current spectrogram
    st.markdown("""
    <div style="background: rgba(19, 27, 46, 0.7); border-left: 4px solid #00BCD4; padding: 1rem; border-radius: 6px; margin-top: 1rem;">
        <h5 style="color: #00BCD4; margin: 0 0 0.5rem 0;">💡 How to Interpret This Display</h5>
        <ul style="color: #B0BEC5; font-size: 0.9rem; margin: 0; padding-left: 1.2rem;">
            <li><strong>Top Plot:</strong> Time-domain potential fluctuations in microvolts (µV). The highlighted dashed window indicates your selected region of interest.</li>
            <li><strong>Bottom Plot:</strong> Time-Frequency energy surface. Warmer colors (red/orange) represent synchronous oscillatory bursts; cooler shades (blue) represent desynchronization or background noise.</li>
            <li><strong>Method in Use:</strong> <code>{method}</code>. Notice how parameter tweaks immediately recalculate the numerical energy matrix.</li>
        </ul>
    </div>
    """.format(method=clean_params['method'].upper()), unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 4: LEARN THE CONCEPTS (EXPLAIN PANEL)
# -----------------------------------------------------------------------------
elif "Learn the Concepts" in selected_page:
    current_p = st.session_state.last_params if st.session_state.last_params else None
    render_explain_panel(current_params=current_p)


# -----------------------------------------------------------------------------
# PAGE 5: EXPERIMENT LAB
# -----------------------------------------------------------------------------
elif "Experiment Lab" in selected_page:
    render_experiment_lab()


# -----------------------------------------------------------------------------
# PAGE 6: KNOWLEDGE CHECK (QUIZ)
# -----------------------------------------------------------------------------
elif "Knowledge Check" in selected_page:
    render_quiz()


# -----------------------------------------------------------------------------
# PAGE 7: EXPORT RESULTS
# -----------------------------------------------------------------------------
elif "Export Results" in selected_page:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">💾 Export Results & Reproducible Code</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            Download your active parameter configuration, numerical spectral matrices,
            and standalone Python scripts for reproducible BCI research.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.cached_tfr is None:
        st.warning("⚠️ No time-frequency computation found in session cache. Visit the **Time-Frequency Explorer** tab first to run an analysis.")
    else:
        cached = st.session_state.cached_tfr
        params = cached['params']
        power = cached['power']
        freqs = cached['freqs']
        times = cached['times']
        
        col1, col2 = st.columns(2)
        
        # 1. JSON Parameters Export
        with col1:
            st.markdown("### 📋 Configuration Metadata (JSON)")
            json_str = export_parameters_json(params)
            st.json(json.loads(json_str))
            
            st.download_button(
                label="⬇️ Download Parameters (.json)",
                data=json_str,
                file_name=f"neurolab_config_{params['method']}_{datetime.date.today()}.json",
                mime="application/json",
                use_container_width=True
            )
            
        # 2. Python Code Export
        with col2:
            st.markdown("### 🐍 Reproducible Python Script (.py)")
            py_code = generate_python_script(params)
            st.code(py_code, language="python")
            
            st.download_button(
                label="⬇️ Download Executable Python Script (.py)",
                data=py_code,
                file_name=f"run_neurolab_{params['method']}.py",
                mime="text/x-python",
                use_container_width=True
            )
            
        st.markdown("---")
        
        # 3. CSV Matrix Export
        st.markdown("### 📊 Spectral Power Matrix (CSV)")
        st.markdown(f"Matrix shape: **{power.shape[0]} frequency bins × {power.shape[1]} temporal time points**")
        
        csv_data = export_power_matrix_csv(power, freqs, times)
        st.download_button(
            label="⬇️ Download Computed Power Matrix (.csv)",
            data=csv_data,
            file_name=f"neurolab_power_matrix_{params['channel']}_{params['method']}.csv",
            mime="text/csv",
            use_container_width=True
        )


# -----------------------------------------------------------------------------
# PAGE 8: ABOUT
# -----------------------------------------------------------------------------
elif "About" in selected_page:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0d1b2a, #1b263b); padding: 1.5rem; border-radius: 12px; border: 1px solid #00BCD4; margin-bottom: 1.5rem;">
        <h2 style="color: #00BCD4; margin: 0;">ℹ️ About NeuroLab</h2>
        <p style="color: #90CAF9; margin-top: 0.5rem; margin-bottom: 0;">
            University Brain-Computer Interface Course Project — Module 5: Time-Frequency Analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🏛️ Academic Context & Module Role
    This interactive educational application forms **Module 5 (Time-Frequency Analysis)** in the shared curriculum pipeline:
    
    `1. Data Loading` → `2. Filtering` → `3. Artifact Handling` → `4. Epoching & ERP` → **`5. TIME-FREQUENCY ANALYSIS (NeuroLab)`** → `6. Spatial Analysis` → `7. Feature Extraction` → `8. Classification` → `9. Paradigm Explorer`
    
    ### 🛠️ Technology Stack
    - **UI & Web Application:** Streamlit, Custom Dark Neuroscience CSS
    - **Signal Processing & BCI:** MNE-Python (v1.6+), SciPy (v1.10+), NumPy (v1.24+), Pandas
    - **Interactive Visualizations:** Plotly Graph Objects & Plotly Subplots
    - **Quality Assurance & Verification:** Pytest automated testing suite
    
    ### 📜 Scientific Integrity & Limitations
    - **Educational Purpose:** Designed strictly for academic teaching and research demonstration. Not intended for clinical diagnostic, surgical, or therapeutic use.
    - **Data Privacy:** All processing executes locally on the student's workstation. No neural data is transmitted to remote servers.
    - **Attribution:** Synthetic benchmarks model physiological ground truth from Hans Berger (1929) and Pfurtscheller & Lopes da Silva (1999).
    """)

