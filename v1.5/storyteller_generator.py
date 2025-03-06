# storyteller_generator.py

import time
import os
import numpy as np
from TTS.api import TTS
from threading import Thread
from queue import Queue as ThreadQueue
import logging
import soundfile as sf
import re

from storyteller_character import StorytellerCharacter
from emotions import EMOTIONS
from storyteller_character import get_tts_settings_for_emotion
logger = logging.getLogger(__name__)

def storyteller_generator_process(
    audio_queue,
    stop_event,
    storyteller_config,
    selected_speaker,
    selected_audio_device,
    progress_queue,
    pause_event
):
    """
    Process that generates storytelling content with specified configuration.
    """
    # Initialize variables
    stories_input_dir = storyteller_config.stories_input_dir
    stories_output_dir = storyteller_config.stories_output_dir
    selected_stories = storyteller_config.selected_stories
    num_rewrites = storyteller_config.num_rewrites
    rewriting_intensity = storyteller_config.rewriting_intensity
    length_setting = storyteller_config.length_setting
    selected_vibe = storyteller_config.selected_vibe

    # Initialize TTS model
    print(f"\nInitializing TTS model for storytelling...")
    logger.info("Initializing TTS model for storytelling...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully.")
    logger.info("TTS model loaded successfully.")

    # Create a thread-safe queue for story content
    content_queue = ThreadQueue(maxsize=5)

    def generate_story_content():
        """Thread function to generate story content"""
        for story_file in selected_stories:
            if stop_event.is_set():
                break

            # Read the story file
            story_path = os.path.join(stories_input_dir, story_file)
            with open(story_path, 'r', encoding='utf-8') as f:
                original_story = f.read()

            # Create output directory for the story
            story_output_dir = os.path.join(stories_output_dir, os.path.splitext(story_file)[0])
            os.makedirs(story_output_dir, exist_ok=True)

            for version in range(1, num_rewrites + 1):
                if stop_event.is_set():
                    break

                # Rewriting the story based on intensity
                storyteller = StorytellerCharacter(
                    original_story=original_story,
                    rewriting_intensity=rewriting_intensity,
                    length_setting=length_setting,
                    selected_vibe=selected_vibe
                )

                # Generate the rewritten story
                rewritten_story = storyteller.rewrite_story()

                # Save the rewritten story transcript
                transcript_path = os.path.join(story_output_dir, f"{os.path.splitext(story_file)[0]}_v{version}_transcript.txt")
                with open(transcript_path, 'w', encoding='utf-8') as f:
                    f.write(rewritten_story)

                # Put the rewritten story in the content queue
                content_queue.put((rewritten_story, story_output_dir, story_file, version))

    # Start content generation thread
    generator_thread = Thread(target=generate_story_content)
    generator_thread.daemon = True
    generator_thread.start()

    while not stop_event.is_set():
        # Pause if pause_event is set
        if pause_event.is_set():
            time.sleep(1)
            continue

        try:
            # Get content from queue
            try:
                rewritten_story, story_output_dir, story_file, version = content_queue.get(timeout=1)
            except Exception:
                continue  # No content available yet, loop again

            if stop_event.is_set():
                break

            # Extract emotion labels and sound effects
            emotions = re.findall(r'\[\*\*(.*?)\*\*\]', rewritten_story)
            sound_effects = re.findall(r'!!(.*?)!!', rewritten_story)

            # Remove emotion labels and sound effects from the text for TTS
            clean_text = re.sub(r'\[\*\*(.*?)\*\*\]', '', rewritten_story)
            clean_text = re.sub(r'!!(.*?)!!', '', clean_text)

            # Determine TTS settings based on emotions
            tts_settings = {}
            for emotion in emotions:
                # Map the emotion to TTS settings
                if emotion in EMOTIONS:
                    emotion_settings = get_tts_settings_for_emotion(emotion)
                    # Update tts_settings; prioritize more intense emotions if multiple
                    tts_settings.update(emotion_settings)

            # Adjust settings based on sound effects
            for effect in sound_effects:
                if effect.lower() in ['gasp', 'bang bang']:
                    # Example: Increase volume or alter pitch for sound effects
                    tts_settings['pitch'] = tts_settings.get('pitch', 1.0) + 0.2
                    tts_settings['volume'] = 1.5  # Assuming 'volume' is a valid parameter

            # Synthesize speech with emotion settings
            try:
                wav = tts_model.tts(
                    text=clean_text,
                    speaker=selected_speaker,
                    speed=tts_settings.get('speed', 1.0),
                    pitch=tts_settings.get('pitch', 1.0),
                    volume=tts_settings.get('volume', 1.0)
                )
            except Exception as e:
                logger.error(f"TTS synthesis error: {e}", exc_info=True)
                print(f"TTS synthesis error: {e}")
                continue

            # Process audio
            wav = np.array(wav, dtype=np.float32)
            if np.max(np.abs(wav)) > 0:
                wav = wav / np.max(np.abs(wav))  # Normalize audio

            # Save audio to file
            audio_filename = os.path.join(story_output_dir, f"{os.path.splitext(story_file)[0]}_v{version}.wav")
            sf.write(audio_filename, wav, samplerate=tts_model.synthesizer.output_sample_rate)
            print(f"Audio for '{story_file}' version {version} saved to {audio_filename}")
            logger.info(f"Audio for '{story_file}' version {version} saved to {audio_filename}")

            # Put audio in queue for playback
            audio_queue.put(wav)

            # Update progress
            progress_info = {
                'current_story': story_file,
                'version': version,
                'status': 'Completed'
            }
            progress_queue.put(progress_info)

        except Exception as e:
            if stop_event.is_set():
                break
            logger.error(f"Error in storytelling generation loop: {e}", exc_info=True)
            print(f"Error in storytelling generation loop: {e}")
            time.sleep(1)

    # Cleanup
    stop_event.set()
    generator_thread.join(timeout=1)

    print("\nStorytelling generation completed.")
    logger.info("Storytelling generation completed.")