import os
import sys
import logging
import signal
from colorama import init, Fore, Style

# Handle console errors silently
if os.name == 'nt':  # Windows
    try:
        import msvcrt
        import ctypes
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except Exception:
        pass

# Initialize colorama
init(strip=False if os.name == 'nt' else None)

from content_generator import ContentGenerator
from stream_manager import StreamManager

class EmilyStream:
    def __init__(self):
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set up main logging
        self.log_file = os.path.join(self.script_dir, 'logs', 'main.log')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        self.logger = logging.getLogger('main')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # Initialize components
        self.content_generator = None
        self.stream_manager = None
        self.audio_thread = None
        
        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle graceful shutdown on signals"""
        print(f"\n{Fore.YELLOW}Shutting down gracefully...{Style.RESET_ALL}")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Clean up resources"""
        try:
            if self.stream_manager:
                self.stream_manager.stop_stream()
            self.logger.info("Cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def get_duration(self) -> float:
        """Get desired stream duration from user"""
        while True:
            try:
                duration = float(input("Enter the desired duration of the stream in minutes: ").strip())
                if duration <= 0:
                    print("Please enter a positive number.")
                    continue
                return duration
            except ValueError:
                print("Please enter a valid number.")

    def get_speaker_choice(self, available_speakers) -> str:
        """Get speaker choice from user"""
        while True:
            try:
                choice = int(input("\nSelect the number corresponding to your preferred speaker: ").strip())
                if 1 <= choice <= len(available_speakers):
                    return available_speakers[choice - 1]
                else:
                    print(f"Please enter a number between 1 and {len(available_speakers)}.")
            except ValueError:
                print("Please enter a valid number.")

    def save_transcript(self, transcript: str):
        """Save the transcript to a file"""
        print(f"\n{Fore.CYAN}Saving transcript...{Style.RESET_ALL}")
        
        while True:
            output_filename = input("\nEnter the desired filename for the output transcript (without extension): ").strip()
            if output_filename:
                break
            print("Filename cannot be empty. Please enter a valid name.")
        
        try:
            output_file = os.path.join(self.script_dir, 'transcripts', f"{output_filename}.txt")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(transcript)
            print(f"\n{Fore.GREEN}Transcript saved to {output_file}{Style.RESET_ALL}")
            
        except Exception as e:
            self.logger.error(f"Error saving transcript: {e}")
            print(f"{Fore.RED}Error saving transcript: {e}{Style.RESET_ALL}")

    def run(self):
        """Main execution flow"""
        try:
            print(f"{Fore.CYAN}=== Emily Solo Twitch Stream Setup ==={Style.RESET_ALL}\n")
            self.logger.info("Starting Emily Stream setup")

            # Initialize components
            self.content_generator = ContentGenerator(self.script_dir)
            self.stream_manager = StreamManager(self.script_dir, self.content_generator)
            
            # Initialize TTS
            if not self.stream_manager.initialize_tts():
                self.logger.error("Failed to initialize TTS")
                return
            
            # Setup audio device
            if self.stream_manager.setup_audio_device() is None:
                self.logger.error("Failed to setup audio device")
                return
            
            # Get stream parameters
            duration = self.get_duration()
            available_speakers = self.stream_manager.tts_model.speakers
            
            print("\nAvailable VCTK VITS Female Speakers:")
            for idx, speaker in enumerate(available_speakers, 1):
                print(f"{idx}. {speaker}")
            
            speaker_name = self.get_speaker_choice(available_speakers)
            
            # Get any modifications
            print("\nWould you like to add any additional modifications or instructions for Emily's monologue?")
            modifications = input("Enter your modifications or press Enter to skip: ").strip()
            
            # Start streaming
            print(f"\n{Fore.GREEN}Starting stream...{Style.RESET_ALL}\n")
            self.audio_thread = self.stream_manager.start_stream(duration, speaker_name, modifications)
            
            # Wait for completion
            try:
                self.audio_thread.join()
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Stream interrupted by user{Style.RESET_ALL}")
            finally:
                # Save transcript
                transcript = self.stream_manager.get_transcript()
                self.save_transcript(transcript)
                
                # Cleanup
                self.cleanup()
                print(f"\n{Fore.GREEN}Stream session completed successfully!{Style.RESET_ALL}")
                
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            print(f"\n{Fore.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")
            self.cleanup()

if __name__ == "__main__":
    stream = EmilyStream()
    stream.run()