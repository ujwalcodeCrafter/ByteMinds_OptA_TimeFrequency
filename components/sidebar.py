"""
Time-Frequency Sidebar Navigation and Controls.
"""
import streamlit as st


def render_sidebar():
    """Render the main sidebar with navigation and branding."""
    with st.sidebar:
        # Branding
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h1 style="color: #00BCD4; margin-bottom: 0; font-size: 1.8rem;">TIME-FREQUENCY</h1>
            <p style="color: #90CAF9; font-size: 0.85rem; margin-top: 0.2rem;">
                Interactive EEG Time-Frequency Explorer
            </p>
        </div>
        <hr style="border-color: #1e3a5f; margin: 0.5rem 0;">
        """, unsafe_allow_html=True)
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["Overview",
             "EEG Data",
             "Time-Frequency Explorer",
             "Learn the Concepts",
             "Knowledge Check",
             "Export Results",
             "About"],
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='border-color: #1e3a5f; margin: 0.5rem 0;'>", unsafe_allow_html=True)
        
        # Quick info
        st.markdown("""
        <div style="padding: 0.5rem; background: rgba(0,188,212,0.05); border-radius: 8px; border-left: 3px solid #00BCD4;">
            <p style="font-size: 0.75rem; color: #B0BEC5; margin: 0;">
                BCI Course Module<br>
                Time-Frequency Analysis
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    return page


def render_analysis_controls(raw_data):
    """Render the analysis parameter controls in sidebar with safety clamps and presets."""
    with st.sidebar:
        st.markdown("### Analysis Parameters")
        
        # Channel selection
        default_ch_idx = raw_data.ch_names.index('Oz') if 'Oz' in raw_data.ch_names else 0
        channel = st.selectbox(
            "EEG Channel",
            raw_data.ch_names,
            index=default_ch_idx,
            help="Select which EEG electrode to analyze"
        )
        
        # Method selection
        method = st.selectbox(
            "Analysis Method",
            ['Morlet Wavelet', 'Multitaper', 'STFT'],
            index=0,
            help="Choose the time-frequency decomposition method"
        )
        method_key = {'Morlet Wavelet': 'morlet', 'Multitaper': 'multitaper', 'STFT': 'stft'}[method]
        
        # Frequency range
        st.markdown("**Frequency Range (Hz)**")
        nyquist = float(raw_data.info['sfreq'] / 2.0)
        
        col1, col2 = st.columns(2)
        with col1:
            fmin = st.number_input(
                "Min Freq", min_value=0.5, max_value=max(1.0, nyquist - 2.0), 
                value=1.0, step=0.5, help="Minimum frequency to analyze"
            )
        with col2:
            min_fmax = min(nyquist, max(fmin + 0.5, 2.0))
            fmax = st.number_input(
                "Max Freq", min_value=min_fmax, max_value=nyquist,
                value=min(45.0, nyquist), step=1.0, 
                help=f"Maximum frequency (Nyquist: {nyquist:.0f} Hz)"
            )
        
        # Number of frequency points
        n_freqs = st.slider("Frequency Points", min_value=10, max_value=80, value=30,
                           help="Number of frequency values to compute")
        
        # Time range
        st.markdown("**Time Window (seconds)**")
        duration = float(raw_data.times[-1])
        time_range = st.slider(
            "Time Range", 
            min_value=0.0, max_value=duration,
            value=(0.0, duration),
            step=0.2,
            help="Select time interval to analyze"
        )
        
        # Method-specific parameters
        method_params = {}
        
        if method_key == 'morlet':
            st.markdown("**Morlet Wavelet Settings**")
            n_cycles = st.slider(
                "Number of Cycles", min_value=1.0, max_value=20.0, value=7.0, step=0.5,
                help="More cycles = better frequency resolution, worse temporal resolution"
            )
            method_params['n_cycles'] = float(n_cycles)
            
        elif method_key == 'multitaper':
            st.markdown("**Multitaper Settings**")
            time_bandwidth = st.slider(
                "Time-Bandwidth Product", min_value=1.5, max_value=8.0, value=4.0, step=0.5,
                help="Higher values = more spectral smoothing, lower variance"
            )
            method_params['time_bandwidth'] = float(time_bandwidth)
            
        elif method_key == 'stft':
            st.markdown("**STFT Settings**")
            sfreq = raw_data.info['sfreq']
            max_win = min(512, max(16, int(raw_data.n_times / 2)))
            window_length = st.slider(
                "Window Length (samples)", min_value=32, max_value=max_win, 
                value=min(256, max_win), step=16,
                help="Longer windows = better frequency resolution, worse temporal resolution"
            )
            max_overlap = max(0, window_length - 1)
            overlap = st.slider(
                "Overlap (samples)", min_value=0, max_value=max_overlap,
                value=min(window_length // 2, max_overlap), step=8,
                help="Number of overlapping samples between windows"
            )
            window_fn = st.selectbox(
                "Window Function",
                ['hann', 'hamming', 'blackman', 'bartlett', 'boxcar'],
                help="Shape of the analysis window"
            )
            method_params['window_length'] = int(window_length)
            method_params['overlap'] = int(overlap)
            method_params['window_function'] = window_fn
        
        # Baseline correction
        st.markdown("**Baseline Normalization**")
        baseline_mode = st.selectbox(
            "Baseline Mode",
            ['None', 'db', 'percent', 'mean', 'ratio', 'zscore'],
            index=1,
            help="How to normalize power relative to a baseline period"
        )
        
        baseline_range = None
        if baseline_mode != 'None':
            max_base = min(5.0, duration / 2.0)
            baseline_range = st.slider(
                "Baseline Period (s)",
                min_value=0.0, max_value=duration,
                value=(0.0, max_base if max_base > 0.5 else duration),
                step=0.2,
                help="Time interval used as reference baseline"
            )
        
        # Colormap visual preference
        st.markdown("**Spectrogram Palette**")
        colormap = st.selectbox(
            "Colormap",
            ['RdYlBu_r', 'Viridis', 'Plasma', 'Turbo', 'Magma'],
            index=0,
            help="Color palette for spectrogram heatmap"
        )
        
        params = {
            'channel': channel,
            'method': method_key,
            'fmin': float(fmin),
            'fmax': float(fmax),
            'n_freqs': int(n_freqs),
            'time_range': (float(time_range[0]), float(time_range[1])),
            'baseline_mode': baseline_mode if baseline_mode != 'None' else None,
            'baseline_range': (float(baseline_range[0]), float(baseline_range[1])) if baseline_range else None,
            'sfreq': float(raw_data.info['sfreq']),
            'colormap': colormap,
            **method_params
        }
        
        return params
