# AI Character Streaming Platform

## Project Overview
This project is a comprehensive AI streaming platform designed to enable interactive, AI-driven character performances on live streaming platforms (e.g., Twitch). The current implementation features an AI persona—“Emily,” a character with a distinct and provocative personality—but the framework is fully extensible to support multiple characters with unique traits. Built as an experimental, high-innovation hobby project, this tool demonstrates advanced integration of AI-assisted code generation, text-to-speech synthesis, and real-time audio routing, all developed using ethical and legally compliant methods.

## Core Features

### Text-to-Speech Live Streaming
- **Real-Time Text Generation:**  
  Integrates local large language models (LLMs) via Ollama to generate engaging dialogue on the fly.
- **High-Quality Voice Synthesis:**  
  Utilizes the VCTK VITS model to produce natural and expressive speech.
- **Virtual Audio Routing:**  
  Employs Virtual Audio Cable (VAC) integration to seamlessly route audio between the application, visual avatar software, and streaming software.
- **Visual Avatar Integration:**  
  Syncs with Animaze to animate and display the AI character in real-time.
- **Automated Conversation Flow:**  
  Manages context, pacing, and natural pauses to deliver a coherent live performance.

### Technical Architecture

#### Components
1. **Language Model Integration**
   - Supports local LLMs via Ollama with custom prompting and context management.
2. **Voice Synthesis**
   - Implements the VCTK VITS model for high-quality, natural speech output.
   - Offers multiple voice configurations for varied character expressions.
3. **Audio Routing & Stream Compatibility**
   - Configures Virtual Audio Cable (VAC) for flawless audio streaming.
   - Synchronizes output with visual avatar software (Animaze) and OBS (or other streaming platforms).
4. **Stream Management**
   - Features configurable stream durations and automatic pacing.
   - Generates transcripts and logs for performance review and debugging.

## Setup Requirements

### Software Dependencies
- Python 3.x
- Ollama for local LLM integration
- TTS (Text-to-Speech) engine (e.g., VCTK VITS model)
- VB-Audio Virtual Cable for audio routing
- Animaze for visual avatar integration
- OBS (or your preferred streaming software)
### Python Packages
```bash
pip install TTS
pip install sounddevice
pip install numpy
pip install colorama
pip install playsound==1.2.2
```

### Audio Setup
1. **Install VB-Audio Virtual Cable**  
   Configure audio routing as follows:
   - Script output → Virtual Cable Input
   - Virtual Cable Output → Animaze Input
   - Animaze Output → Streaming Software

## Character Development

### Current Character: Emily
- Portrayed as a 22-year-old AI with distinct, provocative (psychopathic) traits.
- Crafted with a unique personality that drives engaging, dynamic storytelling.
- Designed to interact with audiences in a way that challenges conventional live streaming norms.

### Extensibility
- Framework supports additional characters with customizable personality traits, voice configurations, and interaction styles.
- Easily extendable for multiple domains, enabling tailored content for various audiences.

## Usage

1. **Configure Your Environment:**  
   - Install the required Python packages using:  
     ```bash
     pip install TTS sounddevice numpy colorama playsound==1.2.2
     ```
   - Set up your audio routing as described in the "Audio Setup" section.

2. **Run the Application:**  
   - Execute the main script to start the streaming platform:  
     ```bash
     python main.py
     ```
   - Follow on-screen prompts (or refer to the documentation) to select the AI character and configure streaming parameters.

3. **Monitor and Interact:**  
   - The tool automatically handles text generation, voice synthesis, and stream management.  
   - Logs and transcripts are saved for debugging and review.


## Future Development

### Planned Enhancements
1. **Enhanced Interaction**
   - Real-time chat integration and audience Q&A handling.
   - Dynamic content adaptation based on live feedback.
2. **Advanced Character Management**
   - Multi-character support with seamless switching during streams.
   - Fine-tuning of personality parameters and behavior models.
3. **Technical Improvements**
   - Improved audio processing for higher fidelity.
   - Enhanced emotion recognition and context awareness.
4. **Expanded Streaming Integration**
   - Broader platform support and deeper integration with popular streaming tools.
   - Augmented visual and interactive features.

## Contributing
Contributions are welcome for enhancing character development, improving audio processing, refining LLM integration, and expanding streaming capabilities. Please follow ethical guidelines—ensure that any contributions remain within legal and defensive research frameworks.

## Current Status
The project is in active development with a working prototype that demonstrates:
- Real-time AI character interaction and dynamic script generation.
- High-quality voice synthesis and seamless audio routing.
- Automated stream management and contextual conversation handling.

## Goals
- Deliver engaging, AI-driven live content.
- Establish a modular framework for multiple AI personalities.
- Enable real-time audience interaction with natural, adaptive responses.
- Pioneer innovative methods for integrating AI into live streaming in a legal and ethical manner.

## Technical Notes
- **Modular Design:**  
  Built with a flexible architecture to support rapid iteration and expansion.
- **Ethical & Legal Compliance:**  
  Sensitive implementation details are abstracted; only high-level methodologies are disclosed.
- **AI Integration:**  
  Leverages AI tools to generate code snippets and assist in rapid prototyping while maintaining deep understanding of system internals.

## License
This project is licensed under the [MIT License](LICENSE).  
Copyright <2024-2025> <Neverlow512>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contact
For inquiries, collaborations, or further information, please contact:  
**Email:** neverlow512@proton.me
**GitHub:** [github.com/Neverlow512](https://github.com/Neverlow512)
