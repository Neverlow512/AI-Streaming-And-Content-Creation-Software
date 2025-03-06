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
    selected_emotion: str
    selected_hook_type: Optional[str]
    selected_topic: Optional[str]
    use_template_outros: bool
    use_template_hooks: bool
    llm_generated_topics: bool
    video_structure: str
    story_framework: str
    category: str
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

    # Get structure components
    video_structure = "\n".join(VIDEO_STRUCTURES[video_config.video_structure]['structure'])
    story_framework = "\n".join(STORY_FRAMEWORKS[video_config.story_framework]['structure'])

    # Generate hook example
    if character_config.use_template_hooks and video_config.hook_type:
        hook_templates = HOOK_TYPES[video_config.hook_type]['templates']
        placeholder_values = {
            'topic': video_config.topic,
            'number': '50',
            'total': '100',
            'amount': '$100',
            'percentage': '50%'
        }
        hook_example = random.choice(hook_templates).format(**placeholder_values)
    else:
        hook_example = "Generate a compelling hook relevant to the topic."

    # Get outro instructions
    if video_config.use_template_outro and video_config.outro_category:
        outro_text = f"End with this outro style: \"{video_config.outro_template}\""
    else:
        outro_text = OUTROS["LLM"]["instructions"]

    prompt = f"""
{base_profile}

Video Structure ({video_config.video_structure}):
{video_structure}

Story Framework ({video_config.story_framework}):
{story_framework}

Current Video Configuration:
- Topic: {video_config.topic}
- Category: {video_config.category}
- Hook Type: {video_config.hook_type or 'AI-generated'}
- Hook Example: "{hook_example}"
- Target Duration: {video_config.duration} seconds
- Emotional Style: {video_config.emotion}

Timing Guidelines:
- Hook and Intro: 5-7 seconds
- Main Content: Structure according to the selected video structure
- Outro: 3-5 seconds
Total should be close to {video_config.duration} seconds

Content Instructions:
1. Follow the "{video_config.video_structure}" structure precisely.
2. Adapt the "{video_config.story_framework}" framework to fit the structure.
3. Start with a hook similar to: "{hook_example}"
4. Maintain a {video_config.emotion} emotional tone throughout.
5. Focus content on the selected topic: {video_config.topic}
6. Keep each section within its time limit.
7. {outro_text}

Previous Content History:
{conversation_history}

Generate the next TikTok script, following the structure exactly:
"""
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

    # Remove any remaining special characters while preserving emojis
    text = re.sub(r'[^\w\s.,!?💡❤️🔥✨👋🎯💪🌟]', '', text)

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
    structure: str,
    speaking_rate: float = 150
) -> float:
    """
    Estimate the duration of TikTok content when spoken.
    speaking_rate: words per minute
    Returns: duration in seconds
    """
    words = len(text.split())
    base_duration = (words / speaking_rate) * 60

    # Add time for transitions and pauses based on structure
    structure_timings = VIDEO_STRUCTURES[structure]['typical_duration']
    target_duration = (structure_timings[0] + structure_timings[1]) / 2

    # Adjust speaking rate to better match target duration
    if base_duration > target_duration * 1.2:
        speaking_rate *= 1.2
    elif base_duration < target_duration * 0.8:
        speaking_rate *= 0.8

    return (words / speaking_rate) * 60

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
        clean_content,
        video_config.video_structure
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
