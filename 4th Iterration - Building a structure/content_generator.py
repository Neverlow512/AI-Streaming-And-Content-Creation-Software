import os
import logging
import subprocess
import re
from queue import Queue
from threading import Thread, Event

class ContentGenerator:
    def __init__(self, script_dir):
        # Set up logging for content generator
        self.log_file = os.path.join(script_dir, 'logs', 'content.log')
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        self.logger = logging.getLogger('content_generator')
        self.logger.setLevel(logging.INFO)
        
        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(handler)
        
        # Initialize queues and events
        self.text_queue = Queue(maxsize=2)  # Buffer for 2 segments
        self.stop_event = Event()
        self.context = []
        self.modifications = ""
        self.total_duration = 0
        self.current_duration = 0

    def start(self, modifications="", total_duration_minutes=0):
        """Start the content generation thread"""
        self.modifications = modifications
        self.total_duration = total_duration_minutes * 60
        self.current_duration = 0
        self.stop_event.clear()
        
        # Start generation thread
        self.generator_thread = Thread(target=self._generate_content_loop)
        self.generator_thread.daemon = True
        self.generator_thread.start()
        
        self.logger.info(f"Content generator started. Duration: {total_duration_minutes} minutes")

    def stop(self):
        """Stop content generation gracefully"""
        self.logger.info("Stopping content generator...")
        self.stop_event.set()
        if hasattr(self, 'generator_thread'):
            self.generator_thread.join()
        self.logger.info("Content generator stopped")

    def get_next_segment(self):
        """Get the next text segment from the queue"""
        try:
            return self.text_queue.get(timeout=10)
        except Exception as e:
            self.logger.error(f"Error getting next segment: {e}")
            return None

    def _call_llm_api(self, prompt):
        """Call Ollama API with error handling and logging"""
        try:
            command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest", prompt]
            self.logger.debug(f"Calling LLM API with command: {command}")
            
            result = subprocess.run(command, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 encoding='utf-8', 
                                 check=True)
            
            if result.stdout.strip():
                self.logger.debug("LLM API call successful")
                return result.stdout.strip()
            else:
                self.logger.warning("LLM API returned empty response")
                return ""
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"LLM API error: {e.stderr}")
            return ""
        except Exception as e:
            self.logger.error(f"Unexpected error calling LLM API: {e}")
            return ""

    def _generate_prompt(self, nearing_end=False):
        """Generate Emily's prompt with context awareness"""
        ending_instructions = ""
        if nearing_end:
            ending_instructions = "(As we are nearing the end of the stream, start concluding your thoughts naturally.)"
        
        context_text = '\n'.join(self.context[-3:])  # Keep last 3 segments for context
        
        prompt = f"""
You are Emily, a 22-year-old woman diagnosed with psychopathy. You lack genuine empathy, feel no remorse, and have a grandiose sense of self-worth. You are intelligent, manipulative, and charming.

Speak directly to your Twitch audience about {self.modifications}. Share your thoughts in an entertaining and engaging manner. Use natural pauses (...) and varied sentence structures.

{ending_instructions}

Important Instructions:
- Continue the ongoing stream naturally, don't start fresh
- NO actions or descriptions (no sighs, winks, etc.)
- NO special characters or formatting
- NO stage directions or emotions in brackets
- Just natural speech as it would be spoken
- Don't end with conclusive statements unless specifically told to wrap up

Behavioral traits:
- Lack of genuine empathy and remorse
- Grandiose sense of self-worth
- Manipulativeness and deceitfulness
- Superficial charm

Previous context:
{context_text}

Continue the stream naturally:
"""
        return prompt.strip()

    def _clean_text(self, text):
        """Clean generated text of unwanted elements"""
        # Remove console error messages
        text = re.sub(r'failed to get console mode for stdout: The handle is invalid\.\s*', '', text)
        text = re.sub(r'failed to get console mode for stderr: The handle is invalid\.\s*', '', text)
        
        # Remove text between asterisks or brackets
        text = re.sub(r'\*[^*]*\*', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        
        # Remove common action words
        action_words = ['sighs', 'winks', 'smirks', 'rolls eyes', 'chuckles', 'smiles', 'leans', 'looks']
        for word in action_words:
            text = re.sub(r'\b' + word + r'\b', '', text, flags=re.IGNORECASE)
        
        # Remove any remaining special characters and clean up whitespace
        text = re.sub(r'[*\[\]()]', '', text)
        return ' '.join(text.split()).strip()

    def _generate_content_loop(self):
        """Main content generation loop"""
        while not self.stop_event.is_set():
            try:
                # Check if we're nearing the end
                nearing_end = self.current_duration >= 0.9 * self.total_duration
                
                # Generate and clean content
                prompt = self._generate_prompt(nearing_end)
                content = self._call_llm_api(prompt)
                cleaned_content = self._clean_text(content)
                
                if cleaned_content:
                    # Add to context and queue
                    self.context.append(f"Emily: {cleaned_content}")
                    self.text_queue.put(cleaned_content)
                    self.logger.debug(f"Generated and queued new content segment: {len(cleaned_content)} chars")
                else:
                    self.logger.warning("Generated empty content, retrying...")
                    continue
                
            except Exception as e:
                self.logger.error(f"Error in content generation loop: {e}")
                if not self.stop_event.is_set():
                    self.logger.info("Continuing despite error...")
                    continue

    def get_context(self):
        """Return current context for transcript purposes"""
        return '\n'.join(self.context)