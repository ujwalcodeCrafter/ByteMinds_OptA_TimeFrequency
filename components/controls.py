"""
Time-Frequency UI Controls and Data Source Management.
"""
import streamlit as st
import os
import tempfile

def render_data_source_selector():
    """Render data source selection UI. Returns source type and any upload."""
    st.markdown("### Select Data Source")
    
    source = st.radio(
        "Choose how to load EEG data:",
        ["Sample Dataset (Alpha Blocking)",
         "Sample Dataset (Motor Imagery)",
         "Upload Your Own EEG File"],
        help="Start with a sample dataset to explore, or upload your own EEG recording"
    )
    
    uploaded_file = None
    csv_params = {}
    
    if "Upload" in source:
        st.markdown("#### Upload EEG File")
        st.info("**Supported formats:** EDF (.edf), FIF (.fif), BrainVision (.vhdr), EEGLAB (.set), CSV (.csv)")
        
        uploaded_file = st.file_uploader(
            "Choose an EEG file",
            type=['edf', 'fif', 'vhdr', 'set', 'csv'],
            help="Upload your EEG recording file"
        )
        
        if uploaded_file and uploaded_file.name.endswith('.csv'):
            st.markdown("**CSV Settings:**")
            csv_params['sfreq'] = st.number_input(
                "Sampling Frequency (Hz)", min_value=1.0, max_value=10000.0,
                value=256.0, step=1.0
            )
            csv_params['time_col'] = st.text_input(
                "Time Column Name (leave empty if none)", value=""
            )
            ch_input = st.text_input(
                "Channel Names (comma-separated, leave empty to use all columns)", value=""
            )
            if ch_input:
                csv_params['ch_names'] = [c.strip() for c in ch_input.split(',')]
            if not csv_params['time_col']:
                csv_params['time_col'] = None
        
        if uploaded_file and uploaded_file.name.endswith('.vhdr'):
            st.warning("BrainVision format requires .vhdr, .vmrk, and .eeg files to be in the same directory. Upload the .vhdr file - the others should be accessible at the same path.")
    
    source_type = 'alpha_blocking' if 'Alpha' in source else ('motor_imagery' if 'Motor' in source else 'upload')
    return source_type, uploaded_file, csv_params


def render_dataset_info(info_dict, dataset_name="", is_synthetic=False):
    """Display dataset metadata in a clean card layout."""
    if is_synthetic:
        st.info("**This is a simulated dataset** generated for educational purposes. It contains synthesized EEG signals with known frequency components for demonstration.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Channels", info_dict['n_channels'])
    with col2:
        st.metric("Sampling Rate", f"{info_dict['sfreq']:.0f} Hz")
    with col3:
        st.metric("Samples", f"{info_dict['n_samples']:,}")
    with col4:
        st.metric("Duration", f"{info_dict['duration']:.1f} s")
    
    with st.expander("Channel Details"):
        st.write(f"**Channel Names:** {', '.join(info_dict['ch_names'])}")
        if info_dict.get('annotations'):
            st.markdown("**Events/Annotations:**")
            for ann in info_dict['annotations']:
                st.write(f"  • `{ann['description']}` at {ann['onset']:.1f}s (duration: {ann['duration']:.1f}s)")
