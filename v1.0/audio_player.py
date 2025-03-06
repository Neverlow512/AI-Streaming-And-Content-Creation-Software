# audio_player.py

import sounddevice as sd
import numpy as np

def audio_player_process(audio_queue, stop_event, selected_audio_device):
    # Set the default output device to the selected device
    sd.default.device[1] = selected_audio_device  # Set the default output device
    devices = sd.query_devices()
    print(f"\nAudio Player Process: Using Output Device: {devices[selected_audio_device]['name']}")

    while not stop_event.is_set() or not audio_queue.empty():
        try:
            # Get audio data from the queue with a timeout
            wav = audio_queue.get(timeout=1)
            play_audio(wav)
        except Exception:
            # Timeout or empty queue
            if stop_event.is_set():
                break  # Exit if stop event is set and queue is empty

def play_audio(audio_data):
    try:
        # Adjust this to match your audio settings
        sample_rate = 22050
        sd.play(audio_data, sample_rate)
        sd.wait()
    except Exception as e:
        print(f"Error playing audio: {e}")
