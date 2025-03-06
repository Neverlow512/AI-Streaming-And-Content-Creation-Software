# main.py

import multiprocessing
from multiprocessing import Queue, Event
from monologue_generator import monologue_generator_process
from audio_player import audio_player_process
from progress_display import progress_display_process
from viral_character import ViralCharacter, ViralVideo, ViralCharacterConfig
from viral_generator import viral_generator_process
from tiktok_config import (
    EMOTIONS, 
    HOOK_TYPES, 
    OUTROS, 
    CONTENT_CATEGORIES,
    STORY_FRAMEWORKS,
    VIDEO_STRUCTURES
)

def get_subcategory_choice(category: str, subcategories: dict) -> str:
    """Helper function to get subcategory choice"""
    print(f"\nAvailable {category} Subcategories:")
    for idx, (subcat_name, topics) in enumerate(subcategories.items(), 1):
        print(f"\n{idx}. {subcat_name}:")
        for tidx, topic in enumerate(topics, 1):
            print(f"   {tidx}. {topic}")
    
    while True:
        try:
            subcat_choice = input("\nSelect subcategory.topic (e.g., 1.2 for second topic in first subcategory): ")
            subcat_idx, topic_idx = map(int, subcat_choice.split('.'))
            if 1 <= subcat_idx <= len(subcategories) and 1 <= topic_idx <= len(list(subcategories.values())[subcat_idx-1]):
                subcat_name = list(subcategories.keys())[subcat_idx - 1]
                return subcategories[subcat_name][topic_idx - 1]
        except:
            print("Please enter a valid selection (e.g., 1.2)")

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
    for category, emotions in EMOTIONS.items():
        print(f"\n{category}:")
        for idx, emotion in enumerate(emotions, 1):
            print(f"{len(all_emotions) + idx}. {emotion}")
            all_emotions.append(emotion)
    
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
                        # Handle Statistics hook type differently
                        if hook_type == "Statistics":
                            example = details['templates'][0].format(number=50, topic='{topic}')
                        else:
                            example = details['templates'][0].format(topic='{topic}')
                        print(f"   Example: {example}")
                        print(f"   Best for: {', '.join(details['best_for'])}")
                    
                    hook_idx = int(input("\nSelect hook type number: "))
                    if 1 <= hook_idx <= len(HOOK_TYPES):
                        settings['hook_type'] = list(HOOK_TYPES.keys())[hook_idx - 1]
                        settings['use_template_hooks'] = True
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
    print("\nExample templates for each category:")
    for category, templates in OUTROS["Template"].items():
        if isinstance(templates, list):
            try:
                # For simple list templates, show the raw template
                template = templates[0]
                if isinstance(template, str):
                    print(f"- {category}: {template}")
            except (IndexError, AttributeError):
                continue
        elif isinstance(templates, dict):
            # For nested dictionary templates
            for subcat, subtemplates in templates.items():
                try:
                    if isinstance(subtemplates, list) and subtemplates:
                        template = subtemplates[0]
                        if isinstance(template, str):
                            print(f"- {category} ({subcat}): {template}")
                except (IndexError, AttributeError):
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
                    cat_idx = int(input("Choose category number: "))
                    if 1 <= cat_idx <= len(categories):
                        settings['outro_category'] = categories[cat_idx - 1]
                else:
                    settings['outro_category'] = None
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
                    for idx, (category, subcats) in enumerate(CONTENT_CATEGORIES.items(), 1):
                        print(f"{idx}. {category}")
                    
                    cat_idx = int(input("\nSelect category number: "))
                    category = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
                    settings['topic'] = get_subcategory_choice(category, CONTENT_CATEGORIES[category])
                    settings['category'] = category
                    settings['llm_generated_topics'] = False
                
                elif topic_choice == 2:
                    settings['llm_generated_topics'] = True
                    settings['topic'] = None
                    # Let user select category for AI generation
                    print("\nSelect category for AI topic generation:")
                    for idx, category in enumerate(CONTENT_CATEGORIES.keys(), 1):
                        print(f"{idx}. {category}")
                    cat_idx = int(input("\nSelect category number: "))
                    settings['category'] = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
                
                else:
                    settings['topic'] = input("Enter your custom topic: ")
                    settings['llm_generated_topics'] = False
                    # Let user select closest category
                    print("\nSelect closest category for your topic:")
                    for idx, category in enumerate(CONTENT_CATEGORIES.keys(), 1):
                        print(f"{idx}. {category}")
                    cat_idx = int(input("\nSelect category number: "))
                    settings['category'] = list(CONTENT_CATEGORIES.keys())[cat_idx - 1]
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
    
    while True:
        try:
            mode_choice = int(input("\nSelect mode (1 or 2): ").strip())
            if mode_choice in [1, 2]:
                break
            print("Please enter 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")

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
                selected_audio_device = device_id
                print(f"\nSelected Output Device: {devices[device_id]['name']}")
                break
            else:
                print("Invalid device number.")
        except ValueError:
            print("Please enter a valid number.")

    # Create shared queues and events
    audio_queue = Queue(maxsize=10)
    progress_queue = Queue()
    stop_event = Event()

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
            llm_generated_topics=tiktok_settings['llm_generated_topics'],
            video_structure=tiktok_settings['video_structure'],
            story_framework=tiktok_settings['story_framework'],
            category=tiktok_settings['category'],
            outro_category=tiktok_settings.get('outro_category')
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
                progress_queue
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