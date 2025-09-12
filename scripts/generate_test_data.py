#!/usr/bin/env python
"""Generate a simulated EEG dataset for testing purposes."""

import os
import argparse
import numpy as np
import mne

def generate_simulated_eeg(duration=10, sfreq=256, n_channels=32, 
                          save_path="simulated_eeg.set", add_events=True,
                          add_artifacts=True):
    """Generate a simulated EEG dataset and save it as a .set file.
    
    Parameters
    ----------
    duration : float
        Duration of the simulated data in seconds
    sfreq : float
        Sampling frequency in Hz
    n_channels : int
        Number of EEG channels to simulate
    save_path : str
        Path where to save the .set file
    add_events : bool
        Whether to add simulated events
    add_artifacts : bool
        Whether to add simulated artifacts
    
    Returns
    -------
    raw : mne.io.Raw
        The generated Raw object
    """
    # Create channel names (Fp1, Fp2, F3, F4, etc.)
    ch_names = []
    
    # Add standard 10-20 channels
    standard_names = [
        'Fp1', 'Fp2', 'F7', 'F3', 'Fz', 'F4', 'F8', 
        'T3', 'C3', 'Cz', 'C4', 'T4', 
        'T5', 'P3', 'Pz', 'P4', 'T6', 
        'O1', 'O2'
    ]
    
    ch_names.extend(standard_names[:min(len(standard_names), n_channels)])
    
    # Add additional channels if needed
    while len(ch_names) < n_channels:
        ch_names.append(f'EEG{len(ch_names)+1}')
    
    # Add a few non-EEG channels
    if n_channels > 24:
        ch_names[-2] = 'EOG1'  # Replace one channel with EOG
        ch_names[-1] = 'ECG'   # Replace one channel with ECG
    
    # Create the info structure
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types='eeg')
    
    # For EOG and ECG channels, set the correct type
    if n_channels > 24:
        info['chs'][-2]['kind'] = mne.io.constants.FIFF.FIFFV_EOG_CH
        info['chs'][-1]['kind'] = mne.io.constants.FIFF.FIFFV_ECG_CH
    
    # Generate random EEG data (typically between -100 and 100 µV)
    n_samples = int(duration * sfreq)
    data = np.random.randn(n_channels, n_samples) * 20  # Scaled to realistic amplitude
    
    # Add alpha oscillations (8-12 Hz) to occipital channels
    if 'O1' in ch_names:
        o1_idx = ch_names.index('O1')
        t = np.arange(n_samples) / sfreq
        alpha_wave = 30 * np.sin(2 * np.pi * 10 * t)  # 10 Hz alpha wave
        data[o1_idx, :] += alpha_wave
    
    if 'O2' in ch_names:
        o2_idx = ch_names.index('O2')
        t = np.arange(n_samples) / sfreq
        alpha_wave = 30 * np.sin(2 * np.pi * 10 * t)  # 10 Hz alpha wave
        data[o2_idx, :] += alpha_wave
    
    # Add simulated artifacts if requested
    if add_artifacts:
        # Add occasional eyeblinks (high amplitude at frontal channels)
        if 'Fp1' in ch_names and 'Fp2' in ch_names:
            fp1_idx = ch_names.index('Fp1')
            fp2_idx = ch_names.index('Fp2')
            
            # Generate a few eyeblinks
            for i in range(3):
                blink_start = np.random.randint(0, n_samples - int(0.5 * sfreq))
                blink_length = int(0.3 * sfreq)  # 300 ms blink
                
                # Create blink shape (sharp rise, slow fall)
                blink = np.zeros(n_samples)
                t = np.linspace(0, 3, blink_length)
                blink_shape = 100 * (t * np.exp(-t))  # Approximate blink shape
                blink[blink_start:blink_start+blink_length] = blink_shape
                
                # Add to frontal channels (inverted for EEG)
                data[fp1_idx, :] -= blink
                data[fp2_idx, :] -= blink
        
        # Add ECG artifact if we have that channel
        if 'ECG' in ch_names:
            ecg_idx = ch_names.index('ECG')
            t = np.arange(n_samples) / sfreq
            heart_rate = 60  # beats per minute
            heart_freq = heart_rate / 60  # beats per second
            
            # Create QRS complex-like shapes
            qrs = np.zeros(n_samples)
            for i in range(int(duration * heart_freq)):
                qrs_center = int((i + 0.5) * sfreq / heart_freq)  # Distribute evenly
                if qrs_center < n_samples - 15:
                    # Simplified QRS shape
                    qrs[qrs_center-5:qrs_center+15] += np.concatenate([
                        -10 * np.ones(5),  # Q wave
                        100 * np.ones(5),  # R wave
                        -20 * np.ones(10)  # S wave and T wave
                    ])
            
            data[ecg_idx, :] = qrs
    
    # Create the Raw object
    raw = mne.io.RawArray(data, info)
    
    # Add events if requested
    if add_events:
        # Create some events (e.g., stimulus events)
        n_events = 5
        event_times = np.linspace(1, duration - 1, n_events)
        event_samples = (event_times * sfreq).astype(int)
        
        # Create event array (sample, 0, event_type)
        events = np.column_stack([
            event_samples,
            np.zeros(n_events, dtype=int),
            np.ones(n_events, dtype=int) * 1  # All events of type 1 for simplicity
        ])
        
        # Create an annotations object and add it to the Raw object
        onsets = event_times
        durations = [0] * n_events
        descriptions = ['Stimulus'] * n_events
        annot = mne.Annotations(onsets, durations, descriptions)
        raw.set_annotations(annot)
    
    # Save as EEGLAB .set file
    os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
    raw.export(save_path, fmt='eeglab')
    
    print(f"Simulated EEG data saved to {save_path}")
    return raw

def main():
    parser = argparse.ArgumentParser(description='Generate simulated EEG data for testing')
    parser.add_argument('--duration', type=float, default=10, help='Duration in seconds')
    parser.add_argument('--sfreq', type=float, default=256, help='Sampling frequency in Hz')
    parser.add_argument('--channels', type=int, default=32, help='Number of channels')
    parser.add_argument('--output', type=str, default='data/simulated_eeg.set', 
                        help='Output file path')
    parser.add_argument('--no-events', action='store_false', dest='add_events',
                       help='Disable adding simulated events')
    parser.add_argument('--no-artifacts', action='store_false', dest='add_artifacts',
                       help='Disable adding simulated artifacts')
    
    args = parser.parse_args()
    
    raw = generate_simulated_eeg(
        duration=args.duration,
        sfreq=args.sfreq,
        n_channels=args.channels,
        save_path=args.output,
        add_events=args.add_events,
        add_artifacts=args.add_artifacts
    )
    
    # Print some information about the generated data
    print("\nSimulated EEG Dataset Information:")
    print(f"Duration: {args.duration} seconds")
    print(f"Sampling Frequency: {args.sfreq} Hz")
    print(f"Number of Channels: {args.channels}")
    print(f"Number of Samples: {len(raw.times)}")
    
    # Calculate file size
    file_size_mb = os.path.getsize(args.output) / (1024 * 1024)
    print(f"File Size: {file_size_mb:.2f} MB")
    
    # Suggest command to view the data
    print("\nTo view this data with autocleaneeg-view, run:")
    print(f"autocleaneeg-view {args.output} --view")
    print("Legacy command also available:")
    print(f"autoclean-view {args.output} --view")

if __name__ == "__main__":
    main()