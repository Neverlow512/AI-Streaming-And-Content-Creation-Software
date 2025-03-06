# main.py

import multiprocessing
from multiprocessing import Queue, Event
from monologue_generator import monologue_generator_process
from audio_player import audio_player_process
from progress_display import progress_display_process

if __name__ == '__main__':
    # Collect user inputs via CLI prompts
    print("\n=== AI Streamer Setup ===\n")

    # Desired duration
    while True:
        duration_input = input("Enter the desired duration of the stream in minutes (leave blank or enter 0 for continuous streaming): ").strip()
        if duration_input == '' or duration_input == '0':
            desired_duration_seconds = 0  # Continuous streaming
            break
        else:
            try:
                desired_duration_minutes = float(duration_input)
                if desired_duration_minutes <= 0:
                    print("Please enter a positive number or leave blank for continuous streaming.")
                    continue
                desired_duration_seconds = desired_duration_minutes * 60
                break
            except ValueError:
                print("Please enter a valid number.")

    # Maximum CPU usage
    while True:
        cpu_usage_input = input("Enter the maximum CPU usage percentage you're willing to allocate (e.g., 50.0 for 50%): ").strip()
        try:
            max_cpu_usage = float(cpu_usage_input)
            if 0 < max_cpu_usage <= 100:
                max_cpu_usage /= 100.0  # Convert percentage to decimal
                break
            else:
                print("Please enter a number between 1 and 100.")
        except ValueError:
            print("Please enter a valid number.")

    # Character selection
    print("\nAvailable Characters:")
    characters = ['Emily', 'Nova']
    for idx, character in enumerate(characters, 1):
        print(f"{idx}. {character}")
    while True:
        try:
            character_choice = int(input("Select the number corresponding to your preferred character: ").strip())
            if 1 <= character_choice <= len(characters):
                selected_character = characters[character_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(characters)}.")
        except ValueError:
            print("Please enter a valid number.")

    modifications = input(f"Enter any modifications or instructions for {selected_character}'s monologue (or press Enter to skip): ").strip()
    if not modifications:
        modifications = "general topics"

    output_filename = input("Enter the desired filename for the output transcript (without extension): ").strip()
    if not output_filename:
        output_filename = f"{selected_character}_conversation_transcript"

    # Initialize TTS model in the main process to get available speakers
    from TTS.api import TTS
    print("\nInitializing TTS model...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully.")

    # Speaker selection
    if tts_model.is_multi_speaker:
        available_speakers = tts_model.speakers
        print("\nAvailable Speakers:")
        for idx, speaker in enumerate(available_speakers, 1):
            print(f"{idx}. {speaker}")
        while True:
            try:
                speaker_choice = int(input("Select the number corresponding to your preferred speaker: ").strip())
                if 1 <= speaker_choice <= len(available_speakers):
                    selected_speaker = available_speakers[speaker_choice - 1]
                    break
                else:
                    print(f"Please enter a number between 1 and {len(available_speakers)}.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        selected_speaker = None

    # Audio Output Device Selection
    import sounddevice as sd
    devices = sd.query_devices()
    print("\nAvailable Audio Output Devices:")
    output_devices = [i for i, d in enumerate(devices) if d['max_output_channels'] > 0]
    for i in output_devices:
        print(f"{i}: {devices[i]['name']}")

    # Prompt user to select the audio output device
    while True:
        try:
            device_id = int(input("Select the number corresponding to your preferred audio output device: ").strip())
            if device_id in output_devices:
                selected_audio_device = device_id  # Store the selected device ID
                print(f"\nSelected Output Device: {devices[device_id]['name']}")
                break
            else:
                print("Invalid device number.")
        except ValueError:
            print("Please enter a valid number.")

    # Create shared queues and events
    audio_queue = Queue(maxsize=10)  # Adjust maxsize as needed
    progress_queue = Queue()
    stop_event = Event()

    # Create and start the monologue generator process
    generator_process = multiprocessing.Process(
        target=monologue_generator_process,
        args=(
            audio_queue,
            stop_event,
            desired_duration_seconds,
            modifications,
            output_filename,
            selected_speaker,
            selected_character,
            max_cpu_usage,
            progress_queue
        )
    )
    generator_process.start()

    # Create and start the audio player process
    player_process = multiprocessing.Process(
        target=audio_player_process,
        args=(audio_queue, stop_event, selected_audio_device)
    )
    player_process.start()

    # Create and start the progress display process
    progress_process = multiprocessing.Process(
        target=progress_display_process,
        args=(desired_duration_seconds, progress_queue)
    )
    progress_process.start()

    # Wait for the generator and player processes to finish
    generator_process.join()
    player_process.join()

    # Signal the progress display process to stop
    progress_queue.put(None)
    progress_process.join()

    print("\nStreaming session completed successfully!")
