import re
from dataclasses import dataclass
from typing import Optional
import random
from emotions import EMOTIONS
from textblob import TextBlob

@dataclass
class StorytellerCharacterConfig:
    """Configuration for the Storyteller character's session"""
    selected_stories: list
    num_rewrites: int
    rewriting_intensity: int
    length_setting: int
    selected_vibe: Optional[str]
    stories_input_dir: str
    stories_output_dir: str

    def get_emotion_settings(self, text: str) -> dict:
        """Get emotion settings based on the selected vibe or detect from text"""
        if self.selected_vibe:
            # Use the selected vibe's emotion settings
            emotions = EMOTIONS[self.selected_vibe]
            emotion = random.choice(emotions)
        else:
            # Detect emotion from text
            emotion = detect_emotion(text)
            emotions = [emotion]
        # Get the TTS settings for the emotion
        emotion_settings = get_tts_settings_for_emotion(emotion)
        return emotion_settings

class StorytellerCharacter:
    def __init__(self, original_story: str, rewriting_intensity: int, length_setting: int, selected_vibe: Optional[str]):
        self.original_story = original_story
        self.rewriting_intensity = rewriting_intensity
        self.length_setting = length_setting
        self.selected_vibe = selected_vibe

    def rewrite_story(self) -> str:
        """Rewrites the story based on the rewriting intensity and selected vibe"""
        prompt = self.generate_story_prompt()
        rewritten_story = call_llm_api(prompt)
        clean_story = clean_text(rewritten_story)
        return clean_story

    def generate_story_prompt(self) -> str:
        """Generates a prompt for the LLM to rewrite the story"""
        base_prompt = f"""
You are a skilled storyteller. Your task is to rewrite the following story.

Original Story:
{self.original_story}

Instructions:
- Rewrite the story with a rewriting intensity of {self.rewriting_intensity} out of 10.
- Maintain the core concept and plot of the story.
- Use natural language and make the story engaging.
- Apply an overall vibe of '{self.selected_vibe}' if specified.
- Adjust the length of the story based on a length setting of {self.length_setting} out of 5.
    - 1: Approximately the same length as the original story.
    - 5: Significantly longer, adding more details and depth.
- Ensure logical consistency and avoid any contradictions in the story.
- Avoid repetition of sentences or phrases.
- **Do not include any analysis or commentary about the story.**
- **Do not tell the reader how to feel or describe the feeling that the story gives.**

Important Notes:
- Do not include any special formatting or markdown.
- Do not mention the instructions or the fact that you are rewriting the story.
- Ensure the story flows naturally and is suitable for narration.
- Maintain logical consistency in the story.
- Avoid repetition of content.
"""

        return base_prompt.strip()

def call_llm_api(prompt):
    # Implement your API call here
    # Placeholder implementation using a command
    import subprocess
    command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest", prompt]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling LLM API: {e.stderr}")
        return ""

import re

def clean_text(text):
    # Remove any unwanted console error messages if present
    text = re.sub(r'failed to get console mode for stdout: The handle is invalid\.\s*', '', text)
    text = re.sub(r'failed to get console mode for stderr: The handle is invalid\.\s*', '', text)

    # Preserve [**emotion**] and !!sound effects!!, but remove other markdown formatting like *, _, ~, and 
    text = re.sub(r'(?<!\[\*\*)[*_~]+(?!\*\*\])', '', text)  # Removes formatting outside [**emotion**]

    # Optional: If you want to keep !!sound effects!! as well, ensure it remains untouched
    # This regex ensures !!...!! remains, and other parts of the text with !! are not stripped
    text = re.sub(r'(?<!!!)([*_~]+)(?!!!)', '', text)  # Ensures !! remains unaffected

    # Remove multiple spaces and clean up newlines
    text = ' '.join(text.split())

    return text.strip()


def detect_emotion(text):
    """Detects the dominant emotion from the text"""
    # Simple sentiment analysis as a placeholder
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0.5:
        return 'Happy'
    elif sentiment < -0.5:
        return 'Sad'
    else:
        return 'Neutral'

def get_tts_settings_for_emotion(emotion):
    """Returns TTS settings for the given emotion"""
    # Retrieve the settings from the EMOTIONS dictionary
    for vibe, emotions in EMOTIONS.items():
        for emo in emotions:
            if emo['name'] == emotion:
                return emo['tts_settings']
    # Default settings
    return {'speed': 0.8, 'pitch': 0.9}
