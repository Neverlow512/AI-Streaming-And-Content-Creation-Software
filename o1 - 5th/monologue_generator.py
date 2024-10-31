# monologue_generator.py

import time
import random
import numpy as np
from TTS.api import TTS
from threading import Thread
from queue import Queue as ThreadQueue
from shared_functions import (
    call_llm_api,
    generate_character_prompt,
    clean_text,
    detect_emotion,
    truncate_conversation,
)
import psutil

def monologue_generator_process(
    audio_queue,
    stop_event,
    desired_duration_seconds,
    modifications,
    output_filename,
    selected_speaker,
    selected_character,
    max_cpu_usage,
    progress_queue
):
    # Initialize variables
    conversation_history = []
    conversation_transcript = ""
    total_duration_seconds = 0

    # Initialize TTS model
    print(f"Initializing TTS model in monologue generator process for {selected_character}...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully in monologue generator process.")

    # Create a thread-safe queue for monologues
    monologue_queue = ThreadQueue(maxsize=50)  # Increased size for more buffering

    # Start a background thread for monologue generation
    generator_thread = Thread(
        target=monologue_generation_thread,
        args=(
            monologue_queue,
            stop_event,
            conversation_history,
            modifications,
            tts_model,
            selected_speaker,
            selected_character,
            max_cpu_usage
        )
    )
    generator_thread.start()

    start_time = time.time()

    while not stop_event.is_set():
        # Check if desired duration is reached (if duration is set)
        if desired_duration_seconds > 0:
            if total_duration_seconds >= desired_duration_seconds:
                stop_event.set()
                break

        try:
            # Get the next monologue from the queue
            character_monologue_clean, wav, duration = monologue_queue.get(timeout=1)
            if character_monologue_clean is None:
                continue

            # Update conversation history
            conversation_history.append(f"{selected_character}: {character_monologue_clean}")
            conversation_transcript += f"{selected_character}: {character_monologue_clean}\n"

            total_duration_seconds += duration

            # Put audio data into the shared queue for audio playback
            audio_queue.put(wav)

            # Update progress
            progress = {
                'total_duration_seconds': total_duration_seconds,
                'desired_duration_seconds': desired_duration_seconds
            }
            progress_queue.put(progress)

            # Small pause before processing the next monologue
            # Reduced pause time to minimize gaps
            time.sleep(random.uniform(0.1, 0.3))

        except Exception as e:
            if stop_event.is_set():
                break

    # Wait for the generator thread to finish
    generator_thread.join()

    # Optionally, save the transcript to a file
    with open(f"{output_filename}.txt", "w", encoding="utf-8") as f:
        f.write(conversation_transcript)

def monologue_generation_thread(
    monologue_queue,
    stop_event,
    conversation_history,
    modifications,
    tts_model,
    selected_speaker,
    selected_character,
    max_cpu_usage
):
    while not stop_event.is_set():
        try:
            # Limit CPU usage
            while psutil.cpu_percent(interval=0.1) > max_cpu_usage * 100:
                time.sleep(0.1)

            # Generate monologue
            character_prompt = generate_character_prompt(conversation_history, modifications, selected_character)
            character_monologue = call_llm_api(character_prompt)

            if not character_monologue:
                continue  # Retry if generation failed

            character_monologue_clean = clean_text(character_monologue)
            if not character_monologue_clean:
                continue  # Retry if cleaning resulted in empty string

            # Detect emotion (optional)
            # emotion = detect_emotion(character_monologue_clean)

            # Synthesize speech
            wav = tts_model.tts(
                character_monologue_clean,
                speaker=selected_speaker,
                speed=0.85,
            )
            wav = np.array(wav, dtype=np.float32)
            wav = wav / np.max(np.abs(wav))

            # Estimate duration
            duration = len(wav) / tts_model.synthesizer.output_sample_rate

            # Update conversation history
            conversation_history.append(f"{selected_character}: {character_monologue_clean}")

            # Truncate conversation history to maintain context window
            conversation_history = truncate_conversation(conversation_history, max_tokens=3000)

            # Put the monologue and audio into the queue
            monologue_queue.put((character_monologue_clean, wav, duration))

        except Exception as e:
            print(f"Error generating monologue: {e}")
            continue
