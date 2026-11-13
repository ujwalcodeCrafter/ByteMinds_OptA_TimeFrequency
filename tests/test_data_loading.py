"""
Test Suite: EEG Data Loading and Sample Data Generation
======================================================
"""
import pytest
import numpy as np
import mne
import io
import pandas as pd

from core.sample_data import generate_sample_eeg, get_sample_data_info, generate_motor_imagery_data
from core.data_loader import extract_data_info, _load_csv


def test_generate_sample_eeg_structure():
    """Verify default synthetic EEG data loads with correct dimensions and properties."""
    raw = generate_sample_eeg(duration=10.0, sfreq=256.0, random_seed=42)
    
    # Assertions
    assert isinstance(raw, mne.io.RawArray), "Expected MNE RawArray instance"
    assert raw.info['sfreq'] == 256.0, f"Expected sfreq=256.0, got {raw.info['sfreq']}"
    assert raw.n_times == 2560, f"Expected 2560 samples for 10s @ 256Hz, got {raw.n_times}"
    assert len(raw.ch_names) == 10, f"Expected 10 channels, got {len(raw.ch_names)}"
    assert 'Oz' in raw.ch_names, "Channel Oz must be present for visual alpha"
    assert 'Cz' in raw.ch_names, "Channel Cz must be present"
    assert 'C3' in raw.ch_names, "Channel C3 must be present"
    assert 'C4' in raw.ch_names, "Channel C4 must be present"


def test_sample_data_metadata_and_annotations():
    """Verify sample metadata dictionary and event annotations."""
    info = get_sample_data_info()
    assert info['is_synthetic'] is True
    assert 'channels' in info
    assert 'sfreq' in info
    assert info['sfreq'] == 256.0

    raw = generate_sample_eeg(duration=30.0, sfreq=256.0)
    assert len(raw.annotations) == 3, "Expected 3 annotations for eyes_closed/eyes_open/eyes_closed"
    descriptions = [a['description'] for a in raw.annotations]
    assert 'eyes_closed' in descriptions
    assert 'eyes_open' in descriptions


def test_motor_imagery_dataset_generation():
    """Verify synthetic motor imagery dataset generation."""
    raw_mi = generate_motor_imagery_data(duration=15.0, sfreq=256.0, random_seed=123)
    assert isinstance(raw_mi, mne.io.RawArray)
    assert 'C3' in raw_mi.ch_names
    assert 'C4' in raw_mi.ch_names
    assert raw_mi.n_times == int(15.0 * 256.0)
    assert len(raw_mi.annotations) > 0


def test_extract_data_info():
    """Verify metadata extraction function."""
    raw = generate_sample_eeg(duration=5.0, sfreq=200.0)
    info_dict = extract_data_info(raw)
    
    assert info_dict['n_channels'] == 10
    assert info_dict['sfreq'] == 200.0
    assert info_dict['n_samples'] == 1000
    assert abs(info_dict['duration'] - 5.0) < 0.05
    assert isinstance(info_dict['ch_names'], list)


def test_csv_data_loader():
    """Verify loading EEG signals from CSV format."""
    # Create synthetic CSV buffer
    n_samples = 512
    sfreq = 256.0
    df = pd.DataFrame({
        'time': np.arange(n_samples) / sfreq,
        'Fz': np.random.randn(n_samples) * 10,
        'Cz': np.random.randn(n_samples) * 10,
        'Oz': np.random.randn(n_samples) * 10,
    })
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    raw = _load_csv(csv_buffer, sfreq=sfreq, time_col='time')
    assert isinstance(raw, mne.io.RawArray)
    assert raw.info['sfreq'] == 256.0
    assert raw.n_times == n_samples
    assert 'Fz' in raw.ch_names
    assert 'Cz' in raw.ch_names
    assert 'Oz' in raw.ch_names
    assert 'time' not in raw.ch_names
