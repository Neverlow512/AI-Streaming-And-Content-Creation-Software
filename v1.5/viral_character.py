# viral_character.py

from dataclasses import dataclass
from typing import List, Optional
import random
import re
from textblob import TextBlob
from tiktok_config import (
    EMOTIONS,
    HOOK_TYPES,
    OUTROS,
    CONTENT_CATEGORIES,
    STORY_FRAMEWORKS,
    VIDEO_STRUCTURES
)

@dataclass
class ViralVideo:
    """Represents a single TikTok video configuration"""
    topic: str
    hook_type: Optional[str]
    duration: float
    emotion: str
    use_template_outro: bool
    category: str
    subcategory: Optional[str]
    video_structure: str
    story_framework: str
    outro_category: Optional[str]
    outro_template: Optional[str] = None
    custom_outro: Optional[str] = None

@dataclass
class ViralCharacterConfig:
    """Configuration for the Viral character's session"""
    num_videos: int
    video_duration: float
    selected_emotion: Optional[str]
    selected_hook_type: Optional[str]
    selected_topic: Optional[str]
    use_template_outros: bool
    use_template_hooks: bool
    llm_generated_topics: bool
    video_structure: str
    story_framework: str
    category: str
    subcategory: Optional[str] = None
    selected_category: Optional[str] = None
    outro_category: Optional[str] = None
    outro_subcategory: Optional[str] = None  # Added field

def generate_viral_prompt(
    conversation_history: str,
    video_config: ViralVideo,
    character_config: ViralCharacterConfig
) -> str:
    """
    Generates a prompt for the Viral character based on TikTok-specific configuration
    """
    base_profile = """
You are Viral, a charismatic and trend-savvy TikTok content creator. Your content is 
engaging, authentic, and crafted to resonate with your audience while maintaining your 
unique style and personality.
"""

    # Generate hook example
    hook_instruction = ''
    if character_config.use_template_hooks and video_config.hook_type:
        hook_templates = HOOK_TYPES[video_config.hook_type]['templates']
        placeholder_values = {
            'topic': video_config.topic or "{topic}",
            'number': '50',
            'total': '100',
            'amount': '$100',
            'percentage': '50%'
        }
        # Validate and format hook templates
        valid_templates = []
        for template in hook_templates:
            try:
                # Try to format the template with the placeholders
                hook_example = template.format(**placeholder_values)
                valid_templates.append(hook_example)
            except KeyError:
                # Skip templates that require placeholders we don't have
                continue
        if valid_templates:
            hook_example = random.choice(valid_templates)
            hook_instruction = f'- Start with a captivating hook similar to: "{hook_example}"\n'
        else:
            # If no valid templates, provide general instruction
            hook_instruction = f'- Start with a captivating hook related to the topic.\n'
    else:
        # General instruction for when not using template hooks
        hook_instruction = f'- Start with a captivating hook related to the topic.\n'

    # Get outro instructions
    if video_config.use_template_outro and video_config.outro_template:
        outro_style_line = f'- End with this outro style: "{video_config.outro_template}"\n'
    else:
        outro_style_line = f'- End with an engaging outro that encourages interaction.\n'

    # Validate and set the emotion
    if character_config.selected_emotion not in [emotion for emotions in EMOTIONS.values() for emotion in emotions]:
        best_emotions = STORY_FRAMEWORKS[video_config.story_framework].get('best_emotions', [])
        if best_emotions:
            video_config.emotion = random.choice(best_emotions)
        else:
            video_config.emotion = random.choice([emotion for emotions in EMOTIONS.values() for emotion in emotions])

    # Build the prompt
    prompt = (
        f"{base_profile}\n\n"
        f"Create a TikTok script that is approximately {video_config.duration} seconds long.\n\n"
        f"Topic: {video_config.topic}\n"
        f"Category: {video_config.category}\n"
        f"Emotion/Tone: {video_config.emotion}\n\n"
        f"Instructions:\n"
        f"{hook_instruction}"
        f"- Ensure that the content is focused on the topic: {video_config.topic}.\n"
        f"- The content should logically follow from the hook and expand on it.\n"
        f"- Deliver content that flows naturally without using any section headers, labels, or script cues like 'Voiceover'.\n"
        f"- Do not include any words like 'Voiceover', 'Scene', 'Act', or any stage directions.\n"
        f"- Maintain a {video_config.emotion.lower()} tone throughout the script.\n"
        f"- Ensure the content is engaging, informative, and suitable for TikTok's format.\n"
        f"- Include a clear conclusion or takeaway at the end.\n"
        f"{outro_style_line}"
        f"- Write in first person, as if you are speaking directly to the audience.\n"
        f"- Keep sentences short and punchy to match TikTok's fast-paced style.\n"
        f"- The script should be self-contained and make sense without any additional context.\n"
        f"- Avoid repeating the same content in multiple scripts. Each script should introduce new ideas or tips related to the topic.\n\n"
        f"Previous Content History (for context):\n"
        f"{conversation_history}\n\n"
        f"Now, generate the TikTok script."
    )
    return prompt.strip()

def clean_tiktok_text(text: str) -> str:
    """
    Clean and format TikTok script text.
    Removes unwanted formatting while preserving the natural TikTok speaking style.
    """
    # Remove any markdown formatting
    text = re.sub(r'[*_~`]', '', text)

    # Remove action descriptions
    text = re.sub(r'\([^)]*\)', '', text)
    text = re.sub(r'\[[^\]]*\]', '', text)

    # Remove multiple spaces and clean up newlines
    text = ' '.join(text.split())

    # Remove any remaining special characters while preserving emojis and apostrophes
    allowed_chars = r'[^a-zA-Z0-9\s.,!?\'💡❤️🔥✨👋🎯💪🌟]'
    text = re.sub(allowed_chars, '', text)

    return text.strip()

def detect_viral_emotion(text: str) -> str:
    """
    Detect the emotional tone of TikTok content.
    Enhanced to understand TikTok-specific language and style.
    """
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    # More nuanced emotion mapping based on both polarity and subjectivity
    if sentiment > 0.6:
        return 'Excited' if subjectivity > 0.5 else 'Professional'
    elif sentiment > 0.2:
        return 'Enthusiastic' if subjectivity > 0.5 else 'Informative'
    elif sentiment < -0.6:
        return 'Dramatic' if subjectivity > 0.5 else 'Critical'
    elif sentiment < -0.2:
        return 'Intriguing' if subjectivity > 0.5 else 'Analytical'
    else:
        return 'Casual' if subjectivity > 0.5 else 'Neutral'

def estimate_tiktok_duration(
    text: str,
    speaking_rate: float = 150
) -> float:
    """
    Estimate the duration of TikTok content when spoken.
    speaking_rate: words per minute
    Returns: duration in seconds
    """
    words = len(text.split())
    duration = (words / speaking_rate) * 60
    return duration

def create_viral_video(
    llm_api,
    video_config: ViralVideo,
    character_config: ViralCharacterConfig,
    conversation_history: List[str]
) -> tuple[str, float]:
    """
    Creates a single TikTok video script and returns it with its estimated duration.
    """
    # Generate the prompt
    prompt = generate_viral_prompt(
        '\n'.join(conversation_history),
        video_config,
        character_config
    )

    # Get content from LLM
    content = llm_api(prompt)

    if not content:
        content = "Failed to generate content. Please try again."

    # Clean the content
    clean_content = clean_tiktok_text(content)

    # Estimate duration
    duration = estimate_tiktok_duration(
        clean_content
    )

    return clean_content, duration

class ViralCharacter:
    def __init__(self, llm_api):
        self.llm_api = llm_api
        self.conversation_history = []
        self.videos_created = 0
        self.total_duration = 0

    def create_video(
        self,
        config: ViralCharacterConfig,
        video_config: ViralVideo
    ) -> tuple[str, float]:
        """
        Creates a single TikTok video based on the provided configurations.
        Returns the script and its duration.
        """
        content, duration = create_viral_video(
            self.llm_api,
            video_config,
            config,
            self.conversation_history
        )

        # Update history and counters
        self.conversation_history.append(f"Video {self.videos_created + 1}:\n{content}")
        self.videos_created += 1
        self.total_duration += duration

        return content, duration
