"""
NeuroLab BCI Time-Frequency Analysis - Core Module
===================================================

Educational toolkit for EEG time-frequency analysis and BCI demonstrations.
"""

from core.validation import (
    validate_frequency_range,
    validate_wavelet_cycles,
    validate_stft_params,
    validate_time_range,
    validate_baseline,
    validate_channel,
    sanitize_parameters,
)

from core.sample_data import (
    generate_sample_eeg,
    get_sample_data_info,
    generate_motor_imagery_data,
)

from core.data_loader import (
    load_eeg_file,
    extract_data_info,
    save_uploaded_file,
)

from core.preprocessing import (
    apply_bandpass_filter,
    get_channel_data,
    create_epochs_array,
)

from core.time_frequency import (
    compute_morlet_tfr,
    compute_multitaper_tfr,
    compute_stft,
    apply_baseline_correction,
    compute_tfr,
)

from core.band_power import (
    FREQUENCY_BANDS,
    BAND_COLORS,
    BAND_DESCRIPTIONS,
    compute_band_power,
    compute_all_band_powers,
    compute_band_power_ratio,
)

from core.export_utils import (
    export_parameters_json,
    generate_python_script,
    export_power_matrix_csv,
    export_analysis_results,
)

__all__ = [
    "validate_frequency_range",
    "validate_wavelet_cycles",
    "validate_stft_params",
    "validate_time_range",
    "validate_baseline",
    "validate_channel",
    "sanitize_parameters",
    "generate_sample_eeg",
    "get_sample_data_info",
    "generate_motor_imagery_data",
    "load_eeg_file",
    "extract_data_info",
    "save_uploaded_file",
    "apply_bandpass_filter",
    "get_channel_data",
    "create_epochs_array",
    "compute_morlet_tfr",
    "compute_multitaper_tfr",
    "compute_stft",
    "apply_baseline_correction",
    "compute_tfr",
    "FREQUENCY_BANDS",
    "BAND_COLORS",
    "BAND_DESCRIPTIONS",
    "compute_band_power",
    "compute_all_band_powers",
    "compute_band_power_ratio",
    "export_parameters_json",
    "generate_python_script",
    "export_power_matrix_csv",
    "export_analysis_results",
]
