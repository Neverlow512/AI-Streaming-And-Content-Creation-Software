# AI Content Creator

## Project Overview
AI-powered content creation system utilizing parallel processing for continuous content generation and speech synthesis. Currently implements a psychopathic AI character (Emily) as proof of concept, designed to be extensible for multiple characters.

## Core Components
- **Content Generator**: LLM-based text generation using Ollama
- **Stream Manager**: Audio processing and playback management
- **Main Controller**: System coordination and user interface

## Current Implementation
```plaintext
Content Generation -> Text Buffer -> Audio Processing -> Playback
     (Ollama)         (Queue)         (TTS)          (Virtual Audio)
```

## Technical Stack
- Python 3.8+
- Ollama for LLM
- TTS for speech synthesis
- Virtual Audio Cable for routing
- Threading for parallel processing

## System Requirements
- High-performance CPU (tested on i9-13900k)
- Adequate RAM (16GB minimum, tested on 128GB DDR5)
- NVIDIA GPU recommended (tested on RTX 3080)
- Virtual Audio Cable installed

## Key Features
- Real-time content generation
- Text-to-speech synthesis
- Virtual audio routing
- Configurable character personalities
- Multi-threaded processing

## Current Focus
- Thread synchronization improvement
- Content buffering optimization
- Audio playback stability
- Error handling and recovery

## Development Status
Active development with focus on:
1. Stabilizing core functionality
2. Improving content flow
3. Enhancing audio processing
4. Preparing for character system expansion

This project is under active development through claude.ai conversations, with each iteration focusing on specific improvements and feature additions.