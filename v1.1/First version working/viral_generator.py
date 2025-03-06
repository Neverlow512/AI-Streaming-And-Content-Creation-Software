# viral_generator.py

import time
import random
import numpy as np
from TTS.api import TTS
from threading import Thread
import psutil
from viral_character import ViralCharacter, ViralVideo, ViralCharacterConfig
from tiktok_config import OUTROS, VIDEO_STRUCTURES, STORY_FRAMEWORKS
import logging
import traceback
import queue
from queue import Queue as ThreadQueue

# Initialize logging at the module level
logging.basicConfig(
    filename='viral_generator.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

def viral_generator_process(
    audio_queue,
    stop_event,
    desired_duration_seconds,
    output_filename,
    selected_speaker,
    viral_config: ViralCharacterConfig,
    max_cpu_usage,
    progress_queue,
    pause_event  # Add this parameter
):
    """
    Process that generates TikTok-style videos with specified configuration.
    """

    # Initialize variables
    conversation_history = []
    conversation_transcript = ""
    total_duration_seconds = 0
    videos_created = 0

    # Initialize TTS model
    print(f"\nInitializing TTS model for TikTok video generation...")
    tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
    print("TTS model loaded successfully.")

    # Create a thread-safe queue for video content
    content_queue = ThreadQueue(maxsize=5)  # Buffer for 5 videos

    def generate_video_content():
        """Thread function to generate video content"""
        nonlocal videos_created

        # Initialize the ViralCharacter with the llm_api function
        character = ViralCharacter(llm_api)

        while videos_created < viral_config.num_videos and not stop_event.is_set():
            # Pause if pause_event is set
            if pause_event.is_set():
                time.sleep(1)
                continue

            try:
                # Check CPU usage
                while psutil.cpu_percent(interval=0.1) > max_cpu_usage * 100:
                    time.sleep(0.1)

                # Get structure-specific timing
                structure_timing = VIDEO_STRUCTURES[viral_config.video_structure]['typical_duration']
                target_duration = (structure_timing[0] + structure_timing[1]) / 2

                # Handle outro template selection
                outro_template = None
                if viral_config.use_template_outros and viral_config.outro_category:
                    outro_section = OUTROS['Template'][viral_config.outro_category]
                    if viral_config.outro_subcategory:
                        # If subcategory exists, select from it
                        templates = outro_section[viral_config.outro_subcategory]
                        outro_template = random.choice(templates)
                    elif isinstance(outro_section, list):
                        # Directly select if it's a list
                        templates = outro_section
                        outro_template = random.choice(templates)
                    else:
                        # Randomly select from all subcategories
                        all_templates = []
                        for subtemplates in outro_section.values():
                            all_templates.extend(subtemplates)
                        outro_template = random.choice(all_templates)

                # Create video configuration with new fields
                current_video = ViralVideo(
                    topic=viral_config.selected_topic,
                    hook_type=viral_config.selected_hook_type,
                    duration=target_duration,  # Use structure-specific duration
                    emotion=viral_config.selected_emotion,
                    use_template_outro=viral_config.use_template_outros,
                    category=viral_config.category,
                    video_structure=viral_config.video_structure,
                    story_framework=viral_config.story_framework,
                    outro_category=viral_config.outro_category,
                    outro_template=outro_template
                )

                # Generate content using viral character
                content, duration = character.create_video(viral_config, current_video)

                # Put content in queue
                content_queue.put((content, duration))
                videos_created += 1

            except Exception as e:
                logging.error(f"Error generating video content: {e}")
                logging.error(traceback.format_exc())
                print(f"Error generating video content: {e}")
                time.sleep(1)  # Brief pause before retry

    # Define the llm_api function using the same format as in shared_functions.py
    def llm_api(prompt):
        import subprocess

        # Construct the command as per your working example
        command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest"]

        try:
            result = subprocess.run(
                command,
                input=prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                encoding='utf-8',
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_message = e.stderr.strip()
            logging.error(f"Error calling LLM API: {error_message}")
            logging.error(traceback.format_exc())
            print(f"Error calling LLM API: {error_message}")
            return ""

    # Start content generation thread
    generator_thread = Thread(target=generate_video_content)
    generator_thread.daemon = True
    generator_thread.start()

    while not stop_event.is_set():
        # Pause if pause_event is set
        if pause_event.is_set():
            time.sleep(1)
            continue

        try:
            # Check if we've created all requested videos
            if videos_created >= viral_config.num_videos and content_queue.empty():
                break

            # Get content from queue
            try:
                content, estimated_duration = content_queue.get(timeout=1)
            except queue.Empty:
                continue  # No content available yet, loop again

            # Update transcript with more detailed formatting
            conversation_transcript += f"\n=== Video {len(conversation_history) + 1} ===\n"
            conversation_transcript += f"Structure: {viral_config.video_structure}\n"
            conversation_transcript += f"Framework: {viral_config.story_framework}\n"
            conversation_transcript += f"Duration: {estimated_duration:.1f}s\n"
            conversation_transcript += f"Content:\n{content}\n"
            conversation_history.append(content)

            # Generate speech with structure-appropriate pacing
            structure_speed = 0.85  # Base speed
            if 'Tutorial' in viral_config.video_structure:
                structure_speed = 0.9  # Slightly faster for tutorials
            elif 'Story' in viral_config.video_structure:
                structure_speed = 0.8  # Slower for stories

            wav = tts_model.tts(
                text=content,
                speaker=selected_speaker,
                speed=structure_speed
            )

            # Process audio
            wav = np.array(wav, dtype=np.float32)
            wav = wav / np.max(np.abs(wav))

            # Calculate actual duration
            actual_duration = len(wav) / tts_model.synthesizer.output_sample_rate
            total_duration_seconds += actual_duration

            # Put audio in queue
            audio_queue.put(wav)

            # Update progress with enhanced information
            progress_info = {
                'total_duration_seconds': total_duration_seconds,
                'videos_completed': len(conversation_history),
                'total_videos': viral_config.num_videos,
                'current_structure': viral_config.video_structure,
                'current_framework': viral_config.story_framework,
                'estimated_remaining': (viral_config.num_videos - len(conversation_history)) * estimated_duration
            }
            progress_queue.put(progress_info)

            # Check if we've hit the desired duration (if specified)
            if desired_duration_seconds > 0 and total_duration_seconds >= desired_duration_seconds:
                stop_event.set()
                break

            # Dynamic pause between videos based on structure
            pause_time = 0.5
            if 'Story' in viral_config.video_structure:
                pause_time = 0.8  # Longer pause after stories
            elif 'Quick' in viral_config.video_structure:
                pause_time = 0.3  # Shorter pause for quick content
            time.sleep(pause_time)

        except Exception as e:
            if stop_event.is_set():
                break
            logging.error(f"Error in video generation loop: {e}")
            logging.error(traceback.format_exc())
            print(f"Error in video generation loop: {e}")
            time.sleep(1)

    # Save enhanced transcript
    try:
        with open(f"{output_filename}.txt", "w", encoding="utf-8") as f:
            f.write(f"=== TikTok Content Generation Report ===\n")
            f.write(f"Structure: {viral_config.video_structure}\n")
            f.write(f"Framework: {viral_config.story_framework}\n")
            f.write(f"Total Videos: {len(conversation_history)}\n")
            f.write(f"Total Duration: {total_duration_seconds:.2f} seconds\n\n")
            f.write(conversation_transcript)
    except Exception as e:
        logging.error(f"Error saving transcript: {e}")
        logging.error(traceback.format_exc())
        print(f"Error saving transcript: {e}")

    # Cleanup
    stop_event.set()
    generator_thread.join(timeout=1)

    print(f"\nTikTok video generation completed:")
    print(f"- Total videos created: {len(conversation_history)}")
    print(f"- Total duration: {total_duration_seconds:.2f} seconds")
    if len(conversation_history) > 0:
        print(f"- Average duration per video: {total_duration_seconds/len(conversation_history):.2f} seconds")
    else:
        print("- No videos were created.")
    print(f"- Transcript saved to: {output_filename}.txt")
