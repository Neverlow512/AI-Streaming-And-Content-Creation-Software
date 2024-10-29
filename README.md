# AI Character Streaming Platform

## Project Overview
This project aims to create a comprehensive AI streaming platform that enables AI characters to interact with live audiences through Twitch or similar streaming platforms. The current implementation focuses on "Emily," a psychopath AI character, but the framework is designed to be extensible for multiple AI personalities and characters.

## Core Features

### Text-to-Speech Live Streaming
- Real-time text generation using local LLMs (currently using Ollama)
- High-quality voice synthesis using VCTK VITS model
- Virtual audio routing for streaming software compatibility
- Integration with Animaze for visual avatars
- Automatic handling of conversation flow and context

### Technical Architecture

#### Components
1. **Language Model Integration**
   - Local LLM support through Ollama
   - Custom character prompting system
   - Context management for coherent conversations

2. **Voice Synthesis**
   - VCTK VITS model for natural speech
   - Multiple voice options
   - Real-time audio processing

3. **Audio Routing**
   - Virtual Audio Cable (VAC) integration
   - Compatible with streaming software
   - Animaze avatar synchronization

4. **Stream Management**
   - Configurable stream duration
   - Automatic conversation pacing
   - Natural pauses and speech patterns
   - Transcript generation and logging

## Setup Requirements

### Software Dependencies
- Python 3.x
- Ollama
- TTS (Text-to-Speech)
- VB-Audio Virtual Cable
- Animaze
- OBS or preferred streaming software

### Python Packages
```bash
pip install TTS
pip install sounddevice
pip install numpy
pip install colorama
pip install playsound==1.2.2
```

### Audio Setup
1. Install VB-Audio Virtual Cable
2. Configure Virtual Audio Cable routing:
   - Script output → Virtual Cable Input
   - Virtual Cable Output → Animaze Input
   - Animaze Output → Streaming Software

## Character Development

### Current Character: Emily
- 22-year-old AI with psychopathic traits
- Unique personality and behavioral patterns
- Engaging storytelling capabilities
- Dynamic audience interaction

### Extensibility
The system is designed to support multiple characters with:
- Custom personality traits
- Unique voice configurations
- Specialized knowledge domains
- Individual interaction styles

## Future Development

### Planned Features
1. **Enhanced Interaction**
   - Real-time chat integration
   - Audience question handling
   - Dynamic content adaptation

2. **Character Management**
   - Multiple character support
   - Character switching during streams
   - Personality fine-tuning

3. **Technical Improvements**
   - Improved audio quality
   - Better emotion handling
   - More natural speech patterns
   - Advanced context awareness

4. **Stream Integration**
   - Better streaming platform integration
   - Multi-platform support
   - Enhanced visual features

## Contributing
This project is part of a larger initiative to create interactive AI characters for live streaming. Contributions in the following areas are welcome:
- Character development
- Audio processing
- LLM integration
- Streaming features
- Documentation

## Current Status
The project is in active development with a working prototype that demonstrates:
- Basic character interaction
- Voice synthesis
- Audio routing
- Stream management

## Goals
- Create engaging AI-driven content
- Develop natural interaction patterns
- Build a framework for multiple AI personalities
- Enable real-time audience interaction
- Maintain character consistency
- Provide entertainment value

## Technical Notes
- The system uses a modular approach for easy expansion
- Character prompts are customizable
- Audio routing can be configured for different setups
- Logging system for debugging and improvement

## License
[Specify your license here]

## Contact
[Your contact information]
