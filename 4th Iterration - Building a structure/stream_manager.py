import os
import logging
import threading
import queue
import sounddevice as sd
import numpy as np
from TTS.api import TTS
import time
from typing import Optional
from colorama import Fore, Style

class StreamManager:
    def __init__(self, script_dir: str, content_generator):
        # Set up logging
        self.log_file = os.path.join(script_dir, 'logs', 'stream.log')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        self.logger = logging.getLogger('stream_manager')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)

        # Initialize components
        self.content_generator = content_generator
        self.audio_queue = queue.Queue(maxsize=2)
        self.stop_event = threading.Event()
        self.is_playing = False
        self.current_stream = None
        
        # TTS settings
        self.sample_rate = 22050
        self.tts_model = None
        self.speaker_name = None
        
        self.logger.info("Stream Manager initialized")

    def initialize_tts(self) -> bool:
        """Initialize the TTS model"""
        try:
            self.logger.info("Initializing TTS model...")
            print(f"{Fore.YELLOW}Initializing TTS model...{Style.RESET_ALL}")
            
            self.tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
            
            print(f"{Fore.GREEN}TTS model loaded successfully.{Style.RESET_ALL}\n")
            self.logger.info("TTS model initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS model: {e}")
            print(f"{Fore.RED}Error initializing TTS model: {e}{Style.RESET_ALL}")
            return False

    def setup_audio_device(self) -> Optional[int]:
        """Set up audio output device"""
        try:
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
                        self.logger.info(f"Audio device set up successfully: {devices[device_id]['name']}")
                        return device_id
                except ValueError:
                    print("Please enter a valid number.")
                    
        except Exception as e:
            self.logger.error(f"Error setting up audio device: {e}")
            return None

    def audio_callback(self, outdata, frames, time, status):
        """Callback for audio stream"""
        if status:
            self.logger.warning(f'Audio callback status: {status}')
        
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
        """Play audio data with error handling"""
        try:
            self.is_playing = True
            print(f"{Fore.CYAN}▶ Playing audio...{Style.RESET_ALL}")
            
            # Convert to mono/stereo as needed
            if self.channels == 1 and len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            elif self.channels == 2 and len(audio_data.shape) == 1:
                audio_data = np.column_stack((audio_data, audio_data))

            # Start playback
            with sd.OutputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=self.audio_callback,
                finished_callback=lambda: setattr(self, 'is_playing', False)
            ) as stream:
                self.current_stream = stream
                self.audio_queue.put(audio_data)
                
                while self.is_playing and not self.audio_queue.empty():
                    time.sleep(0.1)
                    if self.stop_event.is_set():
                        break
            
            print(f"{Fore.GREEN}✓ Audio complete{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"Error playing audio: {e}")
            print(f"{Fore.RED}Error playing audio: {e}{Style.RESET_ALL}")
            self.is_playing = False
        finally:
            self._clear_audio_queue()
            self.current_stream = None

    def _clear_audio_queue(self):
        """Clear audio queue"""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def process_audio_thread(self):
        """Process text to audio in separate thread"""
        while not self.stop_event.is_set():
            try:
                text = self.content_generator.get_next_segment()
                if text:
                    self.logger.debug("Processing text to speech")
                    wav = self.tts_model.tts(
                        text=text,
                        speaker=self.speaker_name,
                        raise_warning=False
                    )
                    
                    wav = np.array(wav, dtype=np.float32)
                    wav = wav / np.max(np.abs(wav))
                    
                    self.play_audio(wav)
                    time.sleep(0.5)  # Small pause between segments
                    
            except Exception as e:
                self.logger.error(f"Error in audio processing thread: {e}")
                if not self.stop_event.is_set():
                    time.sleep(1)  # Wait before retrying
                    continue

    def start_stream(self, duration_minutes: float, speaker_name: str, modifications: str = ""):
        """Start the streaming process"""
        self.speaker_name = speaker_name
        self.stop_event.clear()
        
        # Start content generator
        self.content_generator.start(modifications, duration_minutes)
        
        # Start audio processing thread
        audio_thread = threading.Thread(target=self.process_audio_thread)
        audio_thread.daemon = True
        audio_thread.start()
        
        self.logger.info(f"Stream started. Duration: {duration_minutes} minutes")
        return audio_thread

    def stop_stream(self):
        """Stop the stream gracefully"""
        self.logger.info("Stopping stream...")
        self.stop_event.set()
        self.content_generator.stop()
        self._clear_audio_queue()
        self.logger.info("Stream stopped")

    def get_transcript(self) -> str:
        """Get the complete transcript"""
        return self.content_generator.get_context()