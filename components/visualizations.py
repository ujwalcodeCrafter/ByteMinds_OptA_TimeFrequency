"""
NeuroLab Interactive Visualizations.

Creates linked EEG signal and time-frequency spectrogram plots using Plotly.
"""
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


def create_linked_plots(eeg_data, eeg_times, power, freqs, tfr_times,
                        channel_name, method_name, time_range=None,
                        annotations=None, baseline_mode=None):
    """
    Create two linked interactive plots:
    1. Original EEG signal with time selection
    2. Time-frequency spectrogram
    
    Parameters
    ----------
    eeg_data : np.ndarray, shape (n_times,)
        EEG amplitude data (in Volts).
    eeg_times : np.ndarray
        Time points for EEG data.
    power : np.ndarray, shape (n_freqs, n_times)
        Power values from TF analysis.
    freqs : np.ndarray
        Frequency values.
    tfr_times : np.ndarray
        Time points for TF data.
    channel_name : str
    method_name : str
    time_range : tuple (tmin, tmax), optional
    annotations : list of dicts, optional
    baseline_mode : str, optional
    """
    
    # Convert EEG to microvolts for display
    eeg_uv = eeg_data * 1e6
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(
            f'EEG Signal — Channel {channel_name}',
            f'Time-Frequency Spectrogram — {method_name}'
        ),
        row_heights=[0.35, 0.65]
    )
    
    # --- Plot 1: EEG Signal ---
    fig.add_trace(
        go.Scatter(
            x=eeg_times,
            y=eeg_uv,
            mode='lines',
            line=dict(color='#00BCD4', width=1),
            name='EEG Signal',
            hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.2f} µV<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Add event markers if available
    if annotations:
        colors_map = {
            'eyes_closed': '#4CAF50',
            'eyes_open': '#FF9800',
            'rest': '#2196F3',
            'left_hand_mi': '#E91E63',
            'right_hand_mi': '#9C27B0',
        }
        for ann in annotations:
            onset = ann['onset']
            duration = ann['duration']
            desc = ann['description']
            color = colors_map.get(desc, '#78909C')
            
            fig.add_vrect(
                x0=onset, x1=onset + duration,
                fillcolor=color, opacity=0.1,
                layer='below', line_width=0,
                row=1, col=1
            )
            fig.add_annotation(
                x=onset + duration / 2,
                y=1.05,
                text=desc.replace('_', ' ').title(),
                showarrow=False,
                font=dict(size=10, color=color),
                xref='x', yref='y domain',
                row=1, col=1
            )
    
    # Highlight selected time range
    if time_range:
        fig.add_vrect(
            x0=time_range[0], x1=time_range[1],
            fillcolor='#00BCD4', opacity=0.05,
            layer='below', line=dict(color='#00BCD4', width=1, dash='dash'),
            row=1, col=1
        )
    
    # --- Plot 2: Spectrogram ---
    # Determine color label
    if baseline_mode == 'db':
        colorbar_title = 'Power (dB)'
    elif baseline_mode == 'percent':
        colorbar_title = 'Power (% change)'
    elif baseline_mode == 'zscore':
        colorbar_title = 'Power (z-score)'
    elif baseline_mode == 'ratio':
        colorbar_title = 'Power (ratio)'
    elif baseline_mode == 'mean':
        colorbar_title = 'Power (baselined)'
    else:
        colorbar_title = 'Power (V²/Hz)'
    
    fig.add_trace(
        go.Heatmap(
            x=tfr_times,
            y=freqs,
            z=power,
            colorscale='RdYlBu_r',
            colorbar=dict(
                title=dict(text=colorbar_title, side='right'),
                len=0.55,
                y=0.22,
            ),
            hovertemplate='Time: %{x:.3f}s<br>Freq: %{y:.1f} Hz<br>Power: %{z:.4e}<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Highlight time range on spectrogram
    if time_range:
        fig.add_vrect(
            x0=time_range[0], x1=time_range[1],
            fillcolor='rgba(0,0,0,0)', opacity=1,
            line=dict(color='#00BCD4', width=1.5, dash='dash'),
            row=2, col=1
        )
    
    # --- Layout ---
    fig.update_layout(
        height=700,
        template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)',
        plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5', family='Inter, sans-serif'),
        margin=dict(l=60, r=20, t=50, b=40),
        showlegend=False,
    )
    
    fig.update_xaxes(title_text='Time (s)', row=2, col=1, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(title_text='Amplitude (µV)', row=1, col=1, gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(title_text='Frequency (Hz)', row=2, col=1, gridcolor='rgba(255,255,255,0.05)')
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', row=1, col=1)
    
    return fig


def create_band_power_plot(band_powers, times, band_colors=None):
    """
    Create a frequency band power evolution plot.
    
    Parameters
    ----------
    band_powers : dict
        {band_name: np.ndarray of power values}
    times : np.ndarray
        Time points.
    band_colors : dict, optional
    """
    if band_colors is None:
        band_colors = {
            'Delta': '#FF6B6B',
            'Theta': '#FFA94D',
            'Alpha': '#51CF66',
            'Beta': '#339AF0',
            'Gamma': '#CC5DE8',
        }
    
    fig = go.Figure()
    
    for band_name, power_vals in band_powers.items():
        # Subsample times to match power_vals length
        if len(times) != len(power_vals):
            t = np.linspace(times[0], times[-1], len(power_vals))
        else:
            t = times
        
        color = band_colors.get(band_name, '#78909C')
        # Convert hex to rgba for fill
        if color.startswith('#') and len(color) == 7:
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            fill_col = f'rgba({r}, {g}, {b}, 0.15)'
        else:
            fill_col = color.replace(')', ', 0.15)').replace('rgb', 'rgba') if 'rgb' in color else None

        fig.add_trace(
            go.Scatter(
                x=t, y=power_vals,
                mode='lines',
                name=band_name,
                line=dict(color=color, width=2),
                fill='tozeroy',
                fillcolor=fill_col,
                opacity=0.8,
                hovertemplate=f'{band_name}<br>Time: %{{x:.3f}}s<br>Power: %{{y:.4e}}<extra></extra>'
            )
        )
    
    fig.update_layout(
        title='Frequency Band Power Over Time',
        xaxis_title='Time (s)',
        yaxis_title='Mean Band Power',
        height=350,
        template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)',
        plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
        margin=dict(l=60, r=20, t=60, b=40),
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    
    return fig


def create_single_eeg_plot(eeg_data, times, channel_name, annotations=None):
    """Create a standalone EEG signal plot."""
    eeg_uv = eeg_data * 1e6
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times, y=eeg_uv,
            mode='lines',
            line=dict(color='#00BCD4', width=1),
            hovertemplate='Time: %{x:.3f}s<br>Amplitude: %{y:.2f} µV<extra></extra>'
        )
    )
    
    if annotations:
        colors_map = {
            'eyes_closed': '#4CAF50', 'eyes_open': '#FF9800',
            'rest': '#2196F3', 'left_hand_mi': '#E91E63', 'right_hand_mi': '#9C27B0',
        }
        for ann in annotations:
            color = colors_map.get(ann['description'], '#78909C')
            fig.add_vrect(
                x0=ann['onset'], x1=ann['onset'] + ann['duration'],
                fillcolor=color, opacity=0.1, layer='below', line_width=0,
            )
            fig.add_annotation(
                x=ann['onset'] + ann['duration'] / 2, y=1.05,
                text=ann['description'].replace('_', ' ').title(),
                showarrow=False, font=dict(size=10, color=color),
                xref='x', yref='y domain',
            )
    
    fig.update_layout(
        title=f'EEG Signal — Channel {channel_name}',
        xaxis_title='Time (s)',
        yaxis_title='Amplitude (µV)',
        height=300,
        template='plotly_dark',
        paper_bgcolor='rgba(10, 15, 30, 0.8)',
        plot_bgcolor='rgba(10, 15, 30, 0.95)',
        font=dict(color='#B0BEC5'),
        margin=dict(l=60, r=20, t=50, b=40),
    )
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
    
    return fig
