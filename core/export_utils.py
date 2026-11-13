"""
Export utilities for NeuroLab.

Exports analysis parameters as JSON, generates reproducible Python scripts,
and exports computed data as CSV.
"""

import json
import numpy as np
import datetime


def export_parameters_json(params):
    """
    Export analysis parameters as a JSON string.
    
    Parameters
    ----------
    params : dict
        Analysis configuration parameters.
        
    Returns
    -------
    json_str : str
        JSON-formatted parameter string.
    """
    export_data = {
        'neurolab_export': {
            'version': '1.0.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'software': {
                'application': 'NeuroLab - Interactive EEG Time-Frequency Explorer',
                'libraries': {
                    'mne': '>=1.6',
                    'scipy': '>=1.10',
                    'numpy': '>=1.24',
                }
            }
        },
        'parameters': _make_serializable(params)
    }
    return json.dumps(export_data, indent=2)


def generate_python_script(params):
    """
    Generate a reproducible Python script based on current analysis parameters.
    
    The script includes all necessary imports, data loading, computation,
    and visualization steps with the exact parameters the user selected.
    
    Parameters
    ----------
    params : dict
        Must contain: method, channel, sfreq, fmin, fmax, and method-specific params.
        
    Returns
    -------
    script : str
    """
    method = params.get('method', 'morlet')
    channel = params.get('channel', 'Oz')
    sfreq = params.get('sfreq', 256.0)
    fmin = params.get('fmin', 1.0)
    fmax = params.get('fmax', 40.0)
    n_freqs = params.get('n_freqs', 30)
    baseline_mode = params.get('baseline_mode', 'None')
    baseline_tmin = params.get('baseline_tmin', 0.0)
    baseline_tmax = params.get('baseline_tmax', 1.0)
    tmin = params.get('tmin', None)
    tmax = params.get('tmax', None)
    dataset_name = params.get('dataset_name', 'your_eeg_data')
    
    script = f'''#!/usr/bin/env python3
"""
NeuroLab - Reproducible Time-Frequency Analysis Script
Generated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Dataset: {dataset_name}
Channel: {channel}
Method: {method.capitalize()}
Frequency range: {fmin}-{fmax} Hz
"""

import numpy as np
import matplotlib.pyplot as plt

# === Configuration ===
CHANNEL = "{channel}"
SFREQ = {sfreq}
FMIN = {fmin}
FMAX = {fmax}
N_FREQS = {n_freqs}

# === Load Data ===
# Option 1: Load from file (modify path as needed)
# import mne
# raw = mne.io.read_raw_edf("your_file.edf", preload=True)

# Option 2: Use NeuroLab sample data
import sys
sys.path.insert(0, ".")
from core.sample_data import generate_sample_eeg
raw = generate_sample_eeg()

# Extract channel data
ch_idx = raw.ch_names.index(CHANNEL)
data = raw.get_data()[ch_idx]
times = raw.times
'''

    # Crop if time range specified
    if tmin is not None or tmax is not None:
        tmin_str = tmin if tmin is not None else 0.0
        tmax_str = tmax if tmax is not None else 'None'
        script += f'''
# Crop to selected time range
raw_cropped = raw.copy().crop(tmin={tmin_str}, tmax={tmax_str})
ch_idx = raw_cropped.ch_names.index(CHANNEL)
data = raw_cropped.get_data()[ch_idx]
times = raw_cropped.times
'''

    # Method-specific computation
    if method == 'morlet':
        n_cycles = params.get('n_cycles', 7.0)
        script += f'''
# === Morlet Wavelet Time-Frequency Analysis ===
from mne.time_frequency import tfr_array_morlet

freqs = np.linspace(FMIN, FMAX, N_FREQS)
n_cycles = {n_cycles}

# Reshape for MNE: (n_epochs, n_channels, n_times)
data_3d = data.reshape(1, 1, -1)

# Compute TFR
tfr = tfr_array_morlet(data_3d, sfreq=SFREQ, freqs=freqs,
                       n_cycles=n_cycles, output='power', verbose=False)
power = tfr[0, 0]  # (n_freqs, n_times)
tfr_times = np.linspace(times[0], times[-1], power.shape[1])
'''
    elif method == 'multitaper':
        time_bandwidth = params.get('time_bandwidth', 4.0)
        script += f'''
# === Multitaper Time-Frequency Analysis ===
from mne.time_frequency import tfr_array_multitaper

freqs = np.linspace(FMIN, FMAX, N_FREQS)
n_cycles = freqs / 2.0
n_cycles = np.maximum(n_cycles, 1.0)
time_bandwidth = {time_bandwidth}

data_3d = data.reshape(1, 1, -1)

tfr = tfr_array_multitaper(data_3d, sfreq=SFREQ, freqs=freqs,
                            n_cycles=n_cycles, time_bandwidth=time_bandwidth,
                            output='power', verbose=False)
power = tfr[0, 0]
tfr_times = np.linspace(times[0], times[-1], power.shape[1])
'''
    elif method == 'stft':
        window_length = params.get('window_length', 256)
        overlap = params.get('overlap', 128)
        window_fn = params.get('window_function', 'hann')
        script += f'''
# === Short-Time Fourier Transform ===
from scipy.signal import stft

window_length = {window_length}
overlap = {overlap}

f, t, Zxx = stft(data, fs=SFREQ, window="{window_fn}",
                  nperseg=window_length, noverlap=overlap)
power = np.abs(Zxx) ** 2

# Apply frequency limits
freq_mask = (f >= FMIN) & (f <= FMAX)
power = power[freq_mask]
freqs = f[freq_mask]
tfr_times = t
'''

    # Baseline correction
    if baseline_mode and baseline_mode != 'None':
        script += f'''
# === Baseline Correction ({baseline_mode}) ===
baseline_mask = (tfr_times >= {baseline_tmin}) & (tfr_times <= {baseline_tmax})
if np.any(baseline_mask):
    baseline_power = power[:, baseline_mask].mean(axis=1, keepdims=True)
    baseline_power = np.maximum(baseline_power, np.finfo(float).eps)
'''
        if baseline_mode == 'mean':
            script += '    power = power - baseline_power\n'
        elif baseline_mode == 'ratio':
            script += '    power = power / baseline_power\n'
        elif baseline_mode == 'db':
            script += '    power = 10 * np.log10(power / baseline_power)\n'
        elif baseline_mode == 'percent':
            script += '    power = (power - baseline_power) / baseline_power * 100\n'

    # Visualization
    script += f'''
# === Visualization ===
fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Plot 1: Original EEG Signal
axes[0].plot(times, data * 1e6, color='#00BCD4', linewidth=0.5)
axes[0].set_ylabel('Amplitude (µV)')
axes[0].set_title(f'EEG Signal - Channel {{CHANNEL}}')
axes[0].grid(True, alpha=0.3)

# Plot 2: Time-Frequency Spectrogram
im = axes[1].pcolormesh(tfr_times, freqs if '{method}' != 'morlet' else np.linspace(FMIN, FMAX, N_FREQS),
                         power, cmap='RdYlBu_r', shading='auto')
axes[1].set_ylabel('Frequency (Hz)')
axes[1].set_xlabel('Time (s)')
axes[1].set_title('Time-Frequency Representation ({method.capitalize()})')
plt.colorbar(im, ax=axes[1], label='Power')

plt.tight_layout()
plt.savefig('neurolab_tfr_result.png', dpi=150, bbox_inches='tight')
plt.show()

print("Analysis complete! Figure saved as neurolab_tfr_result.png")
'''
    return script


def export_power_matrix_csv(power, freqs, times):
    """
    Export power matrix as CSV with frequency and time labels.
    
    Returns CSV string with frequencies as rows and times as columns.
    """
    import io
    import csv
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header: Time values
    header = ['Frequency (Hz)'] + [f'{t:.4f}' for t in times]
    writer.writerow(header)
    
    # Data rows
    for i, freq in enumerate(freqs):
        row = [f'{freq:.2f}'] + [f'{p:.6e}' for p in power[i]]
        writer.writerow(row)
    
    return output.getvalue()


def export_analysis_results(power, freqs, times, params):
    """
    Create a comprehensive results export package.
    
    Returns dict with keys: 'parameters_json', 'python_script', 'power_csv'
    """
    return {
        'parameters_json': export_parameters_json(params),
        'python_script': generate_python_script(params),
        'power_csv': export_power_matrix_csv(power, freqs, times),
    }


def _make_serializable(obj):
    """Convert numpy types to Python native types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_,)):
        return bool(obj)
    return obj
