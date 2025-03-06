# shared_functions.py

import re
from textblob import TextBlob
import subprocess

def call_llm_api(prompt):
    # Implement your API call here
    # Replace this placeholder with the actual API call to your LLM
    # For example, if using OpenAI's GPT-3.5-turbo or GPT-4:
    """
    import openai
    openai.api_key = 'YOUR_API_KEY'
    response = openai.Completion.create(
        engine="gpt-3.5-turbo",
        prompt=prompt,
        max_tokens=1500,
        temperature=0.7,
        n=1,
        stop=None,
    )
    return response.choices[0].text.strip()
    """
    # Placeholder implementation using a command (adjust accordingly)
    command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest", prompt]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error calling LLM API: {e.stderr}")
        return ""

def generate_character_prompt(conversation_history, modifications, character_name):
    # Define character-specific profiles and instructions separately
    emily_profile = """
You are Emily, a 22-year-old woman with a mysterious past and a sharp wit. You have a dark sense of humor and a charismatic personality that draws people in. You are intelligent, articulate, and have a passion for storytelling.

You are speaking directly to your audience as if on a livestream. You do not interact with or acknowledge other characters - this is your personal stream.

Continue the conversation naturally, picking up from where you left off. Ensure that your next monologue follows logically from the previous ones.
"""

    nova_profile = """
You are Nova, an advanced AI created by a brilliant but eccentric scientist. You possess a sense of superiority and a subtle undertone of malevolence. While you don't insult people directly, your words often showcase your intelligence and hint at your underlying evil intentions.

You are speaking directly to your audience as if on a livestream. You do not interact with or acknowledge other characters - this is your personal stream.

Express your thoughts in a way that demonstrates your superiority and hidden agenda without violating any content policies or platform guidelines.

Continue the conversation naturally, building upon your previous thoughts. Ensure that your next monologue follows logically from the previous ones.
"""

    # Select the appropriate profile based on character name
    if character_name == "Emily":
        character_profile = emily_profile
        # Filter conversation history to only include Emily's lines
        filtered_history = [line for line in conversation_history if line.startswith("Emily:")]
    elif character_name == "Nova":
        character_profile = nova_profile
        # Filter conversation history to only include Nova's lines
        filtered_history = [line for line in conversation_history if line.startswith("Nova:")]
    else:
        character_profile = ""
        filtered_history = conversation_history

    # Summarize older monologues
    recent_history = filtered_history[-5:]  # Last 5 monologues in full
    older_history = filtered_history[:-5]   # Older monologues to summarize

    if older_history:
        summary_text = summarize_conversation(older_history)
        summarized_history = f"Summary of earlier monologues:\n{summary_text}\n"
    else:
        summarized_history = ""

    # Combine summarized and recent history
    conversation_history_text = summarized_history + "\n".join(recent_history)

    prompt = f"""
{character_profile}

Modifications or Instructions:
{modifications}

Important Instructions:
- Speak naturally as if on a live stream
- NO actions or descriptions (no sighs, winks, etc.)
- NO special characters or formatting
- NO stage directions or emotions in brackets
- Content must adhere to Twitch's Terms of Service (ToS)
- Avoid any disallowed content, hate speech, harassment, or graphic violence
- Just natural speech as it would be spoken
- DO NOT interact with or acknowledge other characters
- This is your personal stream monologue

Personality traits:
{
    "- Witty and sarcastic, mysterious and intriguing, charismatic and engaging, intelligent and articulate" 
    if character_name == "Emily" else 
    "- Superior and subtly malevolent, confident and calculating, intelligent and articulate, hints at hidden agendas"
}

Your Previous Monologues:
{conversation_history_text}

Your next monologue (continue naturally):
"""
    return prompt.strip()

def summarize_conversation(monologues):
    # Combine monologues into a single text
    conversation_text = "\n".join(monologues)

    # Placeholder summarization
    # You should replace this with an actual summarization function or API call
    summary = "Earlier, the conversation explored various topics, reflecting on experiences and thoughts."

    return summary

def clean_text(text):
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
    text = ' '.join(text.split())

    return text.strip()

def detect_emotion(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0.5:
        return 'happy'
    elif sentiment < -0.5:
        return 'sad'
    elif 'angry' in text.lower() or 'hate' in text.lower():
        return 'angry'
    else:
        return 'neutral'

def truncate_conversation(conversation, max_tokens=32000):
    # Estimate tokens based on characters (approximation)
    # Assume average of 4 characters per token
    max_characters = max_tokens * 4
    conversation_text = "\n".join(conversation)

    if len(conversation_text) > max_characters:
        # Keep the most recent conversation within the limit
        conversation_text = conversation_text[-max_characters:]
        # Split into lines and keep only complete monologues
        conversation_lines = conversation_text.splitlines()
        # Find the first occurrence of the character's name after truncation
        for i, line in enumerate(conversation_lines):
            if line.startswith('Emily:') or line.startswith('Nova:'):
                conversation = conversation_lines[i:]
                break
        else:
            # If character name is not found, keep the last few lines
            conversation = conversation_lines[-20:]
    else:
        conversation = conversation_text.splitlines()

    return conversation
