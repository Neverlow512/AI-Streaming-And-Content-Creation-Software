import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Handle console errors silently
if os.name == 'nt':  # Windows
    try:
        import msvcrt
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

import subprocess
import re
import time
import random
from TTS.api import TTS
import sys
import logging
import queue
import sounddevice as sd
import numpy as np
from colorama import init, Fore, Style

# Initialize colorama for colored console output
init(strip=False if os.name == 'nt' else None)

# Configure logging with relative path
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'emily_stream.log')
logging.basicConfig(
    filename=log_file,
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def call_llm_api(prompt):
    """
    Calls the Ollama LLM API with the given prompt and returns the response.
    """
    command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest", prompt]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error calling Ollama: {e.stderr}")
        return ""

def generate_emily_prompt(conversation_history, modifications, nearing_end=False):
    """
    Generates a prompt for Emily based on the conversation history and modifications.
    """
    ending_instructions = ""
    if nearing_end:
        ending_instructions = "(As we are nearing the end of the stream, start concluding your thoughts naturally.)"
    
    prompt = f"""
You are Emily, a 22-year-old woman diagnosed with psychopathy. You lack genuine empathy, feel no remorse, and have a grandiose sense of self-worth. You are intelligent, manipulative, and charming.

Speak directly to your Twitch audience about {modifications}. Share your thoughts in an entertaining and engaging manner. Use natural pauses (...) and varied sentence structures.

{ending_instructions}

Important Instructions:
- Speak naturally as if on a live stream
- NO actions or descriptions (no sighs, winks, etc.)
- NO special characters or formatting
- NO stage directions or emotions in brackets
- Just natural speech as it would be spoken

Behavioral traits:
- Lack of genuine empathy and remorse
- Grandiose sense of self-worth
- Manipulativeness and deceitfulness
- Superficial charm

Previous monologue:
{conversation_history}

Your next monologue (natural speech only):
"""
    return prompt.strip()

def list_available_speakers(tts_model):
    """
    Lists available speakers for the TTS model.
    """
    available_speakers = tts_model.speakers
    print("\nAvailable VCTK VITS Female Speakers:")
    for idx, speaker in enumerate(available_speakers, 1):
        print(f"{idx}. {speaker}")
    return available_speakers

def truncate_conversation(conversation, max_tokens=32000):
    """
    Truncates the conversation history to the last 'max_tokens' words.
    """
    tokens = conversation.split()
    if len(tokens) > max_tokens:
        tokens = tokens[-max_tokens:]
    return ' '.join(tokens)

def estimate_speech_duration(text, words_per_minute=130):
    """
    Estimates the duration of the speech in seconds based on words per minute.
    """
    word_count = len(text.split())
    return (word_count / words_per_minute) * 60

class AudioPlayer:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.current_stream = None
        
        # List available audio devices
        print(f"\n{Fore.CYAN}Available Audio Output Devices:{Style.RESET_ALL}")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if "Speaker (Animaze Virtual Audio)" in device['name']:
                print(f"{Fore.GREEN}{i}: {device['name']} {Style.RESET_ALL} <- Recommended")
            else:
                print(f"{i}: {device['name']}")
            
        while True:
            try:
                device_id = int(input(f"\n{Fore.YELLOW}Select the number for Animaze Speaker output: {Style.RESET_ALL}"))
                if 0 <= device_id < len(devices):
                    sd.default.device[1] = device_id
                    print(f"\n{Fore.GREEN}Selected: {devices[device_id]['name']}{Style.RESET_ALL}")
                    device_info = sd.query_devices(device_id)
                    self.channels = 1 if device_info['max_output_channels'] == 1 else 2
                    break
            except ValueError:
                print("Please enter a valid number.")

    def clear_queue(self):
        """Clear any remaining audio data from the queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def callback(self, outdata, frames, time, status):
        if status:
            logging.warning(f'Audio callback status: {status}')
        
        try:
            data = self.audio_queue.get_nowait()
            if len(data) < len(outdata):
                outdata[:len(data)] = data
                outdata[len(data):] = np.zeros((len(outdata) - len(data), self.channels))
                self.is_playing = False
                raise sd.CallbackStop()
            else:
                outdata[:] = data[:len(outdata)]
                self.audio_queue.put(data[len(outdata):])
        except queue.Empty:
            outdata.fill(0)
            self.is_playing = False
            raise sd.CallbackStop()

    def play_audio(self, audio_data):
        """
        Plays audio data in real-time using sounddevice with improved error handling
        """
        try:
            # Clear any previous audio data and state
            self.clear_queue()
            self.is_playing = True
            
            print(f"{Fore.CYAN}▶ Playing audio...{Style.RESET_ALL}")
            
            # Convert to mono if needed
            if self.channels == 1:
                if len(audio_data.shape) > 1:
                    audio_data = np.mean(audio_data, axis=1)
            else:
                # Ensure stereo
                if len(audio_data.shape) == 1:
                    audio_data = np.column_stack((audio_data, audio_data))

            # Start the stream
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self.callback,
                finished_callback=lambda: setattr(self, 'is_playing', False)
            ) as stream:
                self.current_stream = stream
                self.audio_queue.put(audio_data)
                
                # Wait for playback to complete
                while self.is_playing and not self.audio_queue.empty():
                    time.sleep(0.1)
            
            print(f"{Fore.GREEN}✓ Audio complete{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}Error playing audio: {e}{Style.RESET_ALL}")
            logging.error(f"Error playing audio: {e}")
            self.is_playing = False
        finally:
            self.clear_queue()
            self.current_stream = None

def clean_text(text):
    """
    Removes all action descriptions and special characters.
    """
    # Remove text between asterisks or brackets
    text = re.sub(r'\*[^*]*\*', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)
    # Remove common action words
    action_words = ['sighs', 'winks', 'smirks', 'rolls eyes', 'chuckles', 'smiles', 'leans', 'looks']
    for word in action_words:
        text = re.sub(r'\b' + word + r'\b', '', text, flags=re.IGNORECASE)
    # Remove any remaining special characters and clean up whitespace
    text = re.sub(r'[*\[\]()]', '', text)
    return ' '.join(text.split())

def synthesize_speech(text, tts_model, speaker_name, audio_player):
    """
    Synthesizes speech from text and plays it in real-time.
    """
    try:
        clean_text_result = clean_text(text)
        if not clean_text_result:
            print(f"{Fore.RED}Cleaned text is empty. Skipping synthesis.{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}Generating speech...{Style.RESET_ALL}")
        wav = tts_model.tts(
            text=clean_text_result,
            speaker=speaker_name,
            raise_warning=False
        )

        wav = np.array(wav, dtype=np.float32)
        wav = wav / np.max(np.abs(wav))

        audio_player.play_audio(wav)
        
    except Exception as e:
        print(f"{Fore.RED}Error during speech synthesis: {e}{Style.RESET_ALL}")
        logging.error(f"Error during speech synthesis: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"{Fore.CYAN}=== Emily Solo Twitch Stream Setup ==={Style.RESET_ALL}\n")
    
    while True:
        try:
            desired_duration_minutes = float(input("Enter the desired duration of the stream in minutes: ").strip())
            if desired_duration_minutes <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    try:
        print(f"\n{Fore.YELLOW}Initializing TTS model...{Style.RESET_ALL}")
        tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
        print(f"{Fore.GREEN}TTS model loaded successfully.{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}Error initializing TTS model: {e}{Style.RESET_ALL}")
        sys.exit(1)

    audio_player = AudioPlayer()
    
    available_speakers = list_available_speakers(tts_model)
    while True:
        try:
            speaker_choice = int(input("\nSelect the number corresponding to your preferred speaker: ").strip())
            if 1 <= speaker_choice <= len(available_speakers):
                selected_speaker = available_speakers[speaker_choice - 1]
                break
            else:
                print(f"Please enter a number between 1 and {len(available_speakers)}.")
        except ValueError:
            print("Please enter a valid number.")
    
    print("\nWould you like to add any additional modifications or instructions for Emily's monologue?")
    modifications = input("Enter your modifications or press Enter to skip: ").strip()
    
    conversation_history = []
    conversation_transcript = ""
    total_duration_seconds = 0
    desired_duration_seconds = desired_duration_minutes * 60
    
    print(f"\n{Fore.GREEN}Starting stream...{Style.RESET_ALL}\n")
    
    while total_duration_seconds < desired_duration_seconds:
        nearing_end = total_duration_seconds >= 0.9 * desired_duration_seconds
        
        conversation_history_text = '\n'.join(conversation_history)
        conversation_history_text = truncate_conversation(conversation_history_text)
        
        emily_prompt = generate_emily_prompt(conversation_history_text, modifications, nearing_end)
        emily_monologue = call_llm_api(emily_prompt)
        
        if not emily_monologue:
            print(f"{Fore.RED}Failed to generate monologue. Retrying...{Style.RESET_ALL}")
            continue

        emily_monologue_clean = clean_text(emily_monologue)
        
        if not emily_monologue_clean:
            print(f"{Fore.RED}Monologue is empty after cleaning. Retrying...{Style.RESET_ALL}")
            continue
        
        print(f"\n{Fore.CYAN}Emily:{Style.RESET_ALL} {emily_monologue_clean}\n")
        
        conversation_history.append(f"Emily: {emily_monologue_clean}")
        conversation_transcript += f"Emily: {emily_monologue_clean}\n"
        
        synthesize_speech(emily_monologue_clean, tts_model, selected_speaker, audio_player)
        
        duration = estimate_speech_duration(emily_monologue_clean)
        total_duration_seconds += duration
        
        pause_duration = random.uniform(1, 3)
        time.sleep(pause_duration)
        
        if total_duration_seconds >= desired_duration_seconds:
            break
    
    print(f"\n{Fore.CYAN}Saving transcript...{Style.RESET_ALL}")
    
    while True:
        output_filename = input("\nEnter the desired filename for the output transcript (without extension): ").strip()
        if output_filename:
            break
        else:
            print("Filename cannot be empty. Please enter a valid name.")
    
    output_file = os.path.join(script_dir, f"{output_filename}.txt")
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(conversation_transcript)
        print(f"\n{Fore.GREEN}Transcript saved to {output_file}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error saving transcript: {e}{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}Stream session completed successfully!{Style.RESET_ALL}")

if __name__ == "__main__":
    main()