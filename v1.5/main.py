# main.py

import multiprocessing
from multiprocessing import Queue, Event
import threading
import logging
import os
import sys
import sounddevice as sd

# Import existing modules
from monologue_generator import monologue_generator_process
from audio_player import audio_player_process
from progress_display import progress_display_process
from viral_character import ViralCharacterConfig
from viral_generator import viral_generator_process
from tiktok_config import (
    EMOTIONS as TIKTOK_EMOTIONS,
    HOOK_TYPES,
    OUTROS,
    CONTENT_CATEGORIES,
    STORY_FRAMEWORKS,
    VIDEO_STRUCTURES
)

# Import storyteller modules
from storyteller_generator import storyteller_generator_process
from storyteller_character import StorytellerCharacterConfig
from emotions import EMOTIONS

# Configure the root logger
logging.basicConfig(
    filename='ai_content_creator.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s [%(name)s]: %(message)s'
)

def user_input_thread(stop_event, pause_event):
    """Thread to handle user input for pause, resume, and stop."""
    while not stop_event.is_set():
        command = input("\nEnter 'p' to pause, 'r' to resume, 's' to stop: ").strip().lower()
        if command == 'p':
            print("Pausing...")
            pause_event.set()
        elif command == 'r':
            print("Resuming...")
            pause_event.clear()
        elif command == 's':
            print("Stopping...")
            stop_event.set()
            break
        else:
            print("Invalid command.")

def select_audio_output_device():
    """Function to select audio output device."""
    devices = sd.query_devices()
    print("\nAvailable Audio Output Devices:")
    output_devices = [i for i, d in enumerate(devices) if d['max_output_channels'] > 0]
    for i in output_devices:
        print(f"{i}: {devices[i]['name']}")

    while True:
        try:
            device_id = int(input("Select the number corresponding to your preferred audio output device: ").strip())
            if device_id in output_devices:
                selected_audio_device = device_id
                print(f"\nSelected Output Device: {devices[device_id]['name']}")
                return selected_audio_device
            else:
                print("Invalid device number.")
        except ValueError:
            print("Please enter a valid number.")

def get_tiktok_settings():
    """Collect all TikTok-specific settings from user"""
    settings = {}

    print("\n=== TikTok Mode Configuration ===\n")

    # Video Structure Selection
    print("\nAvailable Video Structures:")
    for idx, (structure, details) in enumerate(VIDEO_STRUCTURES.items(), 1):
        print(f"{idx}. {structure}")
        print(f"   Duration: {details['typical_duration'][0]}-{details['typical_duration'][1]}s")
        print(f"   Best for: {', '.join(details.get('best_for', []))}")

    while True:
        try:
            struct_idx = int(input("\nSelect video structure number: "))
            if 1 <= struct_idx <= len(VIDEO_STRUCTURES):
                settings['video_structure'] = list(VIDEO_STRUCTURES.keys())[struct_idx - 1]
                # Set recommended duration based on structure
                struct_duration = VIDEO_STRUCTURES[settings['video_structure']]['typical_duration']
                settings['video_duration'] = (struct_duration[0] + struct_duration[1]) / 2
                break
            print(f"Please enter a number between 1 and {len(VIDEO_STRUCTURES)}")
        except ValueError:
            print("Please enter a valid number.")

    # Story Framework Selection
    print("\nAvailable Story Frameworks:")
    for idx, (framework, details) in enumerate(STORY_FRAMEWORKS.items(), 1):
        print(f"{idx}. {framework}")
        if 'best_emotions' in details:
            print(f"   Best emotions: {', '.join(details['best_emotions'])}")

    while True:
        try:
            framework_idx = int(input("\nSelect story framework number: "))
            if 1 <= framework_idx <= len(STORY_FRAMEWORKS):
                settings['story_framework'] = list(STORY_FRAMEWORKS.keys())[framework_idx - 1]
                break
            print(f"Please enter a number between 1 and {len(STORY_FRAMEWORKS)}")
        except ValueError:
            print("Please enter a valid number.")

    # Number of videos
    while True:
        try:
            settings['num_videos'] = int(input("\nHow many TikTok videos would you like to create? "))
            if settings['num_videos'] > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

    # Emotion Selection
    print("\nAvailable Emotions by Category:")
    all_emotions = []
    for category, emotions in TIKTOK_EMOTIONS.items():
        print(f"\n{category}:")
        for emotion in emotions:
            all_emotions.append(emotion)
            print(f"{len(all_emotions)}. {emotion}")

    while True:
        try:
            emotion_idx = int(input("\nSelect emotion number: "))
            if 1 <= emotion_idx <= len(all_emotions):
                settings['emotion'] = all_emotions[emotion_idx - 1]
                break
            print(f"Please enter a number between 1 and {len(all_emotions)}")
        except ValueError:
            print("Please enter a valid number.")

    # Hook Type Selection
    print("\nHook Type Options:")
    print("1. Choose from template hooks")
    print("2. Let AI generate hooks")

    while True:
        try:
            hook_choice = int(input("\nSelect option (1 or 2): "))
            if hook_choice in [1, 2]:
                if hook_choice == 1:
                    print("\nAvailable Hook Types:")
                    for idx, (hook_type, details) in enumerate(HOOK_TYPES.items(), 1):
                        print(f"\n{idx}. {hook_type}:")
                        print(f"   Description: {details['description']}")
                        # Prepare placeholder values
                        placeholder_values = {
                            'topic': '{topic}',
                            'number': '50',
                            'total': '100',
                            'amount': '$100',
                            'percentage': '50%'
                        }
                        # Use the first template as an example
                        try:
                            example_template = details['templates'][0]
                            example = example_template.format(**placeholder_values)
                        except KeyError:
                            example = example_template.replace('{topic}', '{topic}')
                        print(f"   Example: {example}")
                        print(f"   Best for: {', '.join(details['best_for'])}")

                    while True:
                        try:
                            hook_idx = int(input("\nSelect hook type number: "))
                            if 1 <= hook_idx <= len(HOOK_TYPES):
                                settings['hook_type'] = list(HOOK_TYPES.keys())[hook_idx - 1]
                                settings['use_template_hooks'] = True
                                break
                            print(f"Please enter a number between 1 and {len(HOOK_TYPES)}")
                        except ValueError:
                            print("Please enter a valid number.")
                    break
                else:
                    settings['hook_type'] = None
                    settings['use_template_hooks'] = False
                    break
            print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number.")

    # Outro Selection
    print("\nOutro Options:")
    print("1. Use template outros")
    print("2. Generate custom outros using LLM")

    # Define placeholder values for formatting
    placeholder_values = {
        'topic': '{topic}',
        'number': '1',
        'total': '100',
        'amount': '$100',
        'percentage': '50%'
    }

    print("\nExample templates for each category:")
    for category, templates in OUTROS["Template"].items():
        if isinstance(templates, list):
            try:
                # For simple list templates, show the formatted template
                template = templates[0]
                if isinstance(template, str):
                    formatted_template = template.format(**placeholder_values)
                    print(f"- {category}: {formatted_template}")
            except (IndexError, AttributeError, KeyError):
                continue
        elif isinstance(templates, dict):
            # For nested dictionary templates
            for subcat, subtemplates in templates.items():
                try:
                    if isinstance(subtemplates, list) and subtemplates:
                        template = subtemplates[0]
                        if isinstance(template, str):
                            formatted_template = template.format(**placeholder_values)
                            print(f"- {category} ({subcat}): {formatted_template}")
                except (IndexError, AttributeError, KeyError):
                    continue

    while True:
        try:
            outro_choice = int(input("\nSelect outro option (1 or 2): "))
            if outro_choice in [1, 2]:
                settings['use_template_outros'] = outro_choice == 1
                if outro_choice == 1:
                    print("\nSelect outro category:")
                    categories = list(OUTROS["Template"].keys())
                    for idx, category in enumerate(categories, 1):
                        print(f"{idx}. {category}")
                    while True:
                        try:
                            cat_idx = int(input("Choose category number: "))
                            if 1 <= cat_idx <= len(categories):
                                selected_category = categories[cat_idx - 1]
                                settings['outro_category'] = selected_category
                                # Check if subcategories exist
                                subcategories = OUTROS["Template"][selected_category]
                                if isinstance(subcategories, dict):
                                    subcats = list(subcategories.keys())
                                    print("\nSelect subcategory:")
                                    for idx, subcat in enumerate(subcats, 1):
                                        print(f"{idx}. {subcat}")
                                    while True:
                                        try:
                                            subcat_idx = int(input("Choose subcategory number: "))
                                            if 1 <= subcat_idx <= len(subcats):
                                                settings['outro_subcategory'] = subcats[subcat_idx - 1]
                                                break
                                            print(f"Please enter a number between 1 and {len(subcats)}")
                                        except ValueError:
                                            print("Please enter a valid number.")
                                else:
                                    settings['outro_subcategory'] = None
                                break
                            print(f"Please enter a number between 1 and {len(categories)}")
                        except ValueError:
                            print("Please enter a valid number.")
                else:
                    settings['outro_category'] = None
                    settings['outro_subcategory'] = None
                break
            print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number.")

    # Topic Selection with Categories and Subcategories
    print("\nTopic Selection:")
    print("1. Choose from categories")
    print("2. Let AI generate topics")
    print("3. Enter custom topic")

    while True:
        try:
            topic_choice = int(input("Select option: "))
            if topic_choice in [1, 2, 3]:
                if topic_choice == 1:
                    print("\nAvailable Categories:")
                    for idx, category in enumerate(CONTENT_CATEGORIES.keys(), 1):
                        print(f"{idx}. {category}")

                    while True:
                        try:
                            cat_idx = int(input("\nSelect category number: "))
                            if 1 <= cat_idx <= len(CONTENT_CATEGORIES):
                                category = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
                                settings['category'] = category
                                # Get subcategories
                                subcategories = CONTENT_CATEGORIES[category]
                                print(f"\nAvailable Subcategories in {category}:")
                                subcat_names = list(subcategories.keys())
                                for idx, subcat_name in enumerate(subcat_names, 1):
                                    print(f"{idx}. {subcat_name}")
                                while True:
                                    try:
                                        subcat_idx = int(input("\nSelect subcategory number: "))
                                        if 1 <= subcat_idx <= len(subcat_names):
                                            subcat_name = subcat_names[subcat_idx - 1]
                                            topics = subcategories[subcat_name]
                                            print(f"\nAvailable Topics in {subcat_name}:")
                                            for tidx, topic in enumerate(topics, 1):
                                                print(f"{tidx}. {topic}")
                                            topic_idx = int(input("\nSelect topic number: "))
                                            if 1 <= topic_idx <= len(topics):
                                                settings['topic'] = topics[topic_idx - 1]
                                                break
                                            else:
                                                print("Invalid topic selection. Please try again.")
                                        else:
                                            print("Invalid subcategory selection. Please try again.")
                                    except ValueError:
                                        print("Please enter valid numbers.")
                                break
                            else:
                                print(f"Please enter a number between 1 and {len(CONTENT_CATEGORIES)}")
                        except ValueError:
                            print("Please enter a valid number.")
                    settings['llm_generated_topics'] = False
                    break
                elif topic_choice == 2:
                    settings['llm_generated_topics'] = True
                    settings['topic'] = None
                    # Let user select category for AI topic generation
                    print("\nSelect category for AI topic generation:")
                    for idx, category in enumerate(CONTENT_CATEGORIES.keys(), 1):
                        print(f"{idx}. {category}")
                    while True:
                        try:
                            cat_idx = int(input("\nSelect category number: "))
                            if 1 <= cat_idx <= len(CONTENT_CATEGORIES):
                                settings['category'] = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
                                break
                            print(f"Please enter a number between 1 and {len(CONTENT_CATEGORIES)}")
                        except ValueError:
                            print("Please enter a valid number.")
                    break
                else:
                    settings['topic'] = input("Enter your custom topic: ")
                    settings['llm_generated_topics'] = False
                    # Let user select closest category
                    print("\nSelect closest category for your topic:")
                    for idx, category in enumerate(CONTENT_CATEGORIES.keys(), 1):
                        print(f"{idx}. {category}")
                    while True:
                        try:
                            cat_idx = int(input("\nSelect category number: "))
                            if 1 <= cat_idx <= len(CONTENT_CATEGORIES):
                                settings['category'] = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
                                break
                            print(f"Please enter a number between 1 and {len(CONTENT_CATEGORIES)}")
                        except ValueError:
                            print("Please enter a valid number.")
                    break
            print("Please enter 1, 2, or 3")
        except ValueError:
            print("Please enter a valid number.")

    return settings

if __name__ == '__main__':
    # Collect user inputs via CLI prompts
    print("\n=== AI Content Creator Setup ===\n")

    # Mode Selection
    print("Available Modes:")
    print("1. Stream Mode (Continuous or timed streaming)")
    print("2. TikTok Mode (Multiple short videos)")
    print("3. Storytelling Mode")

    while True:
        try:
            mode_choice = int(input("\nSelect mode (1, 2, or 3): ").strip())
            if mode_choice in [1, 2, 3]:
                break
            print("Please enter 1, 2, or 3.")
        except ValueError:
            print("Please enter a valid number.")

    if mode_choice == 3:
        # Storytelling Mode
        print("\n=== Storytelling Mode Configuration ===\n")

        # Predefined input and output directories
        stories_input_dir = "stories_input"
        stories_output_dir = "stories_output"

        # Ensure input directory exists
        if not os.path.exists(stories_input_dir):
            os.makedirs(stories_input_dir)
            print(f"Created input directory: {stories_input_dir}")
            print("Please add your story text files to the input directory and rerun the program.")
            sys.exit()

        # List stories in the input directory
        story_files = [f for f in os.listdir(stories_input_dir) if os.path.isfile(os.path.join(stories_input_dir, f))]
        if not story_files:
            print(f"No story files found in {stories_input_dir}. Please add your story text files and rerun the program.")
            sys.exit()

        print("\nAvailable Stories:")
        for idx, story_file in enumerate(story_files, 1):
            print(f"{idx}. {story_file}")

        # Story Selection
        while True:
            selected_stories_input = input("\nEnter the numbers of the stories you want to select, separated by commas (e.g., 1,3,5): ").strip()
            try:
                selected_indices = [int(num.strip()) for num in selected_stories_input.split(',')]
                if all(1 <= idx <= len(story_files) for idx in selected_indices):
                    selected_stories = [story_files[idx - 1] for idx in selected_indices]
                    break
                else:
                    print("Invalid selection. Please enter valid story numbers.")
            except ValueError:
                print("Please enter valid numbers separated by commas.")

        # Number of rewrites per story
        while True:
            try:
                num_rewrites = int(input("\nEnter the number of times you want each story to be rewritten: ").strip())
                if num_rewrites > 0:
                    break
                else:
                    print("Please enter a positive number.")
            except ValueError:
                print("Please enter a valid number.")

        # Rewriting Intensity
        while True:
            try:
                rewriting_intensity = int(input("\nEnter the rewriting intensity from 1 (few changes) to 10 (complete rewrite): ").strip())
                if 1 <= rewriting_intensity <= 10:
                    break
                print("Please enter a number between 1 and 10.")
            except ValueError:
                print("Please enter a valid number.")

        # Length setting
        while True:
            try:
                length_setting = int(input("\nEnter the desired length from 1 (matches original length) to 5 (longer story): ").strip())
                if 1 <= length_setting <= 5:
                    break
                else:
                    print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")

        # Emotion/Vibe Selection
        print("\nEmotion/Vibe Options:")
        print("1. Select an overall vibe for the story")
        print("2. Let the AI detect the vibe from the story")

        while True:
            try:
                vibe_choice = int(input("\nSelect option (1 or 2): ").strip())
                if vibe_choice in [1, 2]:
                    break
                print("Please enter 1 or 2.")
            except ValueError:
                print("Please enter a valid number.")

        if vibe_choice == 1:
            # Display available vibes
            vibes = list(EMOTIONS.keys())
            print("\nAvailable Vibes:")
            for idx, vibe in enumerate(vibes, 1):
                print(f"{idx}. {vibe}")

            while True:
                try:
                    vibe_idx = int(input("\nSelect the number corresponding to your preferred vibe: ").strip())
                    if 1 <= vibe_idx <= len(vibes):
                        selected_vibe = vibes[vibe_idx - 1]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(vibes)}.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            selected_vibe = None  # AI will detect the vibe

        # Speaker selection (TTS model initialization)
        from TTS.api import TTS
        print("\nInitializing TTS model...")
        tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
        print("TTS model loaded successfully.")

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
        print("\nAudio Output Options:")
        print("0. Select audio output device")
        print("Available Audio Output Devices:")
        devices = sd.query_devices()
        output_devices = [i for i, d in enumerate(devices) if d['max_output_channels'] > 0]
        for i in output_devices:
            print(f"{i}: {devices[i]['name']}")

        while True:
            try:
                audio_output_choice = int(input("\nSelect the number corresponding to your preferred audio output device (or 0 to manually select): ").strip())
                if audio_output_choice == 0:
                    selected_audio_device = select_audio_output_device()
                    break
                elif audio_output_choice in output_devices:
                    selected_audio_device = audio_output_choice
                    print(f"\nSelected Output Device: {devices[selected_audio_device]['name']}")
                    break
                else:
                    print("Invalid selection. Please enter 0 or a valid device number.")
            except ValueError:
                print("Please enter a valid number.")

        # Create shared queues and events
        audio_queue = Queue(maxsize=10)
        progress_queue = Queue()
        stop_event = Event()
        pause_event = Event()

        # Start user input thread
        input_thread = threading.Thread(target=user_input_thread, args=(stop_event, pause_event))
        input_thread.daemon = True
        input_thread.start()

        # Create Storyteller configuration
        storyteller_config = StorytellerCharacterConfig(
            selected_stories=selected_stories,
            num_rewrites=num_rewrites,
            rewriting_intensity=rewriting_intensity,
            length_setting=length_setting,
            selected_vibe=selected_vibe,
            stories_input_dir=stories_input_dir,
            stories_output_dir=stories_output_dir
        )

        # Create and start the storyteller generator process
        generator_process = multiprocessing.Process(
            target=storyteller_generator_process,
            args=(
                audio_queue,
                stop_event,
                storyteller_config,
                selected_speaker,
                selected_audio_device,
                progress_queue,
                pause_event
            )
        )
        generator_process.start()

        # Create and start the audio player process
        player_process = multiprocessing.Process(
            target=audio_player_process,
            args=(audio_queue, stop_event, selected_audio_device)
        )
        player_process.start()

        # Wait for the generator and player processes to finish
        generator_process.join()
        player_process.join()

        print("\nStorytelling session completed successfully!")

    else:
        # Existing modes (Stream Mode and TikTok Mode)
        # Collect additional inputs and proceed accordingly

        # Duration handling based on mode
        if mode_choice == 1:  # Stream Mode
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
        else:  # TikTok Mode
            # TikTok mode will handle duration per video in get_tiktok_settings()
            desired_duration_seconds = 0  # Not used in TikTok mode

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
        characters = ['Emily', 'Nova', 'Viral']
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

        # Branch based on character selection
        if selected_character == "Viral":
            tiktok_settings = get_tiktok_settings()
            modifications = f"TikTok mode: {tiktok_settings['topic']}"
        else:
            if mode_choice == 2:
                print("Note: TikTok mode is only available with the Viral character. Switching to stream mode.")
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
        print("\nAudio Output Options:")
        print("0. Select audio output device")
        print("Available Audio Output Devices:")
        devices = sd.query_devices()
        output_devices = [i for i, d in enumerate(devices) if d['max_output_channels'] > 0]
        for i in output_devices:
            print(f"{i}: {devices[i]['name']}")

        while True:
            try:
                audio_output_choice = int(input("\nSelect the number corresponding to your preferred audio output device (or 0 to manually select): ").strip())
                if audio_output_choice == 0:
                    selected_audio_device = select_audio_output_device()
                    break
                elif audio_output_choice in output_devices:
                    selected_audio_device = audio_output_choice
                    print(f"\nSelected Output Device: {devices[selected_audio_device]['name']}")
                    break
                else:
                    print("Invalid selection. Please enter 0 or a valid device number.")
            except ValueError:
                print("Please enter a valid number.")

        # Create shared queues and events
        audio_queue = Queue(maxsize=10)
        progress_queue = Queue()
        stop_event = Event()
        pause_event = Event()

        # Start user input thread
        input_thread = threading.Thread(target=user_input_thread, args=(stop_event, pause_event))
        input_thread.daemon = True
        input_thread.start()

        # Create and start the appropriate generator process
        if selected_character == "Viral":
            # Create Viral configuration
            viral_config = ViralCharacterConfig(
                num_videos=tiktok_settings['num_videos'],
                video_duration=tiktok_settings['video_duration'],
                selected_emotion=tiktok_settings['emotion'],
                selected_hook_type=tiktok_settings['hook_type'],
                selected_topic=tiktok_settings['topic'],
                use_template_outros=tiktok_settings['use_template_outros'],
                use_template_hooks=tiktok_settings['use_template_hooks'],
                llm_generated_topics=tiktok_settings['llm_generated_topics'],
                video_structure=tiktok_settings['video_structure'],
                story_framework=tiktok_settings['story_framework'],
                category=tiktok_settings['category'],
                outro_category=tiktok_settings.get('outro_category'),
                outro_subcategory=tiktok_settings.get('outro_subcategory')  # New field
            )

            # Use viral_generator_process instead of monologue_generator_process
            generator_process = multiprocessing.Process(
                target=viral_generator_process,
                args=(
                    audio_queue,
                    stop_event,
                    desired_duration_seconds,
                    output_filename,
                    selected_speaker,
                    viral_config,
                    max_cpu_usage,
                    progress_queue,
                    pause_event  # Pass pause_event
                )
            )
        else:
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
                    progress_queue,
                    pause_event  # Pass pause_event if needed
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
