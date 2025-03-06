# emotions.py

# emotions.py
EMOTIONS = {
      'Happy': [
          {'name': 'Cheerful', 'tts_settings': {'speed': 0.85, 'pitch': 1.1, 'volume': 1.0}},
          {'name': 'Joyful', 'tts_settings': {'speed': 0.9, 'pitch': 1.0, 'volume': 1.0}},
      ],
      'Sad': [
          {'name': 'Melancholic', 'tts_settings': {'speed': 0.9, 'pitch': 0.9, 'volume': 0.9}},
          {'name': 'Somber', 'tts_settings': {'speed': 0.8, 'pitch': 0.8, 'volume': 0.8}},
      ],
      'Dramatic': [
          {'name': 'Intense', 'tts_settings': {'speed': 0.8, 'pitch': 1.0, 'volume': 1.1}},
          {'name': 'Epic', 'tts_settings': {'speed': 0.83, 'pitch': 0.9, 'volume': 1.2}},  # Adjusted volume
      ],
      'Motivational': [
          {'name': 'Inspirational', 'tts_settings': {'speed': 1.0, 'pitch': 1.1, 'volume': 1.0}},
          {'name': 'Encouraging', 'tts_settings': {'speed': 1.05, 'pitch': 1.05, 'volume': 1.0}},
      ],
      'Horror': [
          {'name': 'Creepy', 'tts_settings': {'speed': 0.85, 'pitch': 0.95, 'volume': 1.0}},
          {'name': 'Spooky', 'tts_settings': {'speed': 0.8, 'pitch': 0.9, 'volume': 1.0}},
      ],
      # Added more emotions
      'Excited': [
          {'name': 'Thrilled', 'tts_settings': {'speed': 1.1, 'pitch': 1.0, 'volume': 1.0}},
          {'name': 'Energetic', 'tts_settings': {'speed': 1.0, 'pitch': 1.05, 'volume': 1.0}},
      ],
      'Neutral': [
          {'name': 'Calm', 'tts_settings': {'speed': 1.0, 'pitch': 1.0, 'volume': 1.0}},
          {'name': 'Balanced', 'tts_settings': {'speed': 1.0, 'pitch': 1.0, 'volume': 1.0}},
      ],
      # Add more emotions as needed
  }
