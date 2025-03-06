# setup.py

import os

# Create necessary files
files = {
    "main.py": """
import multiprocessing
from monologue_generator import monologue_generator_process
from audio_player import audio_player_process
from multiprocessing import Queue, Event

if __name__ == '__main__':
    # Get user inputs in the main process
    desired_duration_minutes = float(input("Enter the desired duration of the stream in minutes: ").strip())
    desired_duration_seconds = desired_duration_minutes * 60

    modifications = input("Enter any modifications or instructions for Emily's monologue (or press Enter to skip): ").strip()
    if not modifications:
        modifications = "general topics"

    output_filename = input("Enter the desired filename for the output transcript (without extension): ").strip()
    if not output_filename:
        output_filename = "conversation_transcript"

    # Initialize TTS model in the main process to get available speakers
    from TTS.api import TTS
    print("Initializing TTS model...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully.")

    # Speaker selection
    if tts_model.is_multi_speaker:
        available_speakers = tts_model.speakers
        print("\\nAvailable Speakers:")
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

    # Create a shared queue
    audio_queue = Queue(maxsize=5)  # Adjust maxsize as needed

    # Create an Event to signal when the desired duration is reached
    stop_event = Event()

    # Create and start the monologue generator process
    generator_process = multiprocessing.Process(
        target=monologue_generator_process,
        args=(audio_queue, stop_event, desired_duration_seconds, modifications, output_filename, selected_speaker)
    )
    generator_process.start()

    # Create and start the audio player process
    player_process = multiprocessing.Process(
        target=audio_player_process,
        args=(audio_queue, stop_event)
    )
    player_process.start()

    # Wait for both processes to finish
    generator_process.join()
    player_process.join()
""",

    "monologue_generator.py": """
import time
import random
import numpy as np
from TTS.api import TTS
from textblob import TextBlob
import sys
import logging
from shared_functions import (
    call_llm_api,
    generate_emily_prompt,
    clean_text,
    detect_emotion,
    truncate_conversation,
    estimate_speech_duration,
)

def monologue_generator_process(audio_queue, stop_event, desired_duration_seconds, modifications, output_filename, selected_speaker):
    # Initialize variables
    conversation_history = []
    conversation_transcript = ""
    total_duration_seconds = 0

    # Initialize TTS model
    print("Initializing TTS model in monologue generator process...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully in monologue generator process.")

    start_time = time.time()

    while not stop_event.is_set():
        # Check if desired duration is reached
        elapsed_time = time.time() - start_time
        if elapsed_time >= desired_duration_seconds:
            stop_event.set()
            break

        # Generate monologue
        conversation_history_text = '\\n'.join(conversation_history)
        conversation_history_text = truncate_conversation(conversation_history_text)

        emily_prompt = generate_emily_prompt(conversation_history_text, modifications)
        emily_monologue = call_llm_api(emily_prompt)

        if not emily_monologue:
            continue  # Retry if generation failed

        emily_monologue_clean = clean_text(emily_monologue)
        if not emily_monologue_clean:
            continue  # Retry if cleaning resulted in empty string

        # Update conversation history
        conversation_history.append(f"Emily: {emily_monologue_clean}")
        conversation_transcript += f"Emily: {emily_monologue_clean}\\n"

        # Detect emotion
        emotion = detect_emotion(emily_monologue_clean)

        # Synthesize speech
        wav = tts_model.tts(
            emily_monologue_clean,
            speaker=selected_speaker,
            speed=1.0,
        )
        wav = np.array(wav, dtype=np.float32)
        wav = wav / np.max(np.abs(wav))

        # Estimate duration
        duration = len(wav) / tts_model.synthesizer.output_sample_rate
        total_duration_seconds += duration

        # Put audio data into the queue
        audio_queue.put(wav)

        # Small pause before generating the next monologue
        time.sleep(random.uniform(1, 2))

    # Optionally, save the transcript to a file
    with open(f"{output_filename}.txt", "w", encoding="utf-8") as f:
        f.write(conversation_transcript)
""",

    # The rest of the files remain the same...
}

# Write files to disk
for filename, content in files.items():
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content.strip())

print("Setup complete. The following files have been created:")
for filename in files.keys():
    print(f"- {filename}")

print("\\nNext steps:")
print("1. Install the required packages by running:")
print("   pip install -r requirements.txt")
print("2. Download NLTK data by running the following in Python:")
print("   import nltk")
print("   nltk.download('punkt')")
print("3. Run the application:")
print("   python main.py")
