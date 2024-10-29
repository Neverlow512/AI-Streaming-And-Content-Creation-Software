# Emily Stream - Technical Configuration Guide

## Critical Performance Settings

### LLM Configuration
Location: `content_generator.py`
```python
# Model Selection
command = ["ollama", "run", "hf.co/ArliAI/Mistral-Small-22B-ArliAI-RPMax-v1.1-GGUF:latest", prompt]
```
- Can be changed to any Ollama-compatible model
- Smaller models = faster generation, less coherent
- Larger models = slower generation, more coherent
- Recommended models:
  - Fast: mistral-7b-instruct
  - Balanced: mistral-7b-instruct-v0.2
  - Quality: mistral-22b-rp

### Context Window Management
Location: `content_generator.py`
```python
# Context Window Size
context_text = '\n'.join(self.context[-3:])  # Currently keeps last 3 segments
```
- Increase number (-3) for longer memory but more token usage
- Decrease for faster processing but less coherent conversation
- Memory usage scales linearly with context size
- Recommended ranges:
  - Minimum: -2 segments
  - Balanced: -3 to -5 segments
  - Maximum: -10 segments (may cause issues with some models)

### Queue Settings
```python
# Content Generation Queue
self.text_queue = Queue(maxsize=2)  # In content_generator.py

# Audio Processing Queue
self.audio_queue = queue.Queue(maxsize=2)  # In stream_manager.py
```
- Larger queue size = smoother playback but more memory usage
- Recommended ranges:
  - Low memory: maxsize=1
  - Balanced: maxsize=2-3
  - High performance: maxsize=4-5

## GPU Acceleration

### TTS GPU Settings
Location: `stream_manager.py`
```python
self.tts_model = TTS("tts_models/en/vctk/vits", progress_bar=False, gpu=False)
```
- Set `gpu=True` if you have CUDA-compatible GPU
- Requirements for GPU:
  - NVIDIA GPU with CUDA support
  - Appropriate CUDA toolkit installed
  - PyTorch with CUDA support

### Performance Impact
- CPU-only:
  - Processing time: ~1-2s per segment
  - Memory usage: 2-4GB
- GPU-enabled:
  - Processing time: ~0.3-0.5s per segment
  - VRAM usage: 2-6GB depending on model

## Audio Processing

### Sample Rate Settings
Location: `stream_manager.py`
```python
self.sample_rate = 22050  # Default TTS sample rate
```
- Higher = better quality but more processing
- Lower = faster processing but lower quality
- Recommended values:
  - Low quality: 16000
  - Balanced: 22050
  - High quality: 44100

### Audio Chunking
```python
# In stream_manager.py, play_audio method
if len(audio_data.shape) > 1:
    audio_data = np.mean(audio_data, axis=1)  # Mono conversion
```
- Affects how audio is processed and played
- Smaller chunks = lower latency but more CPU
- Larger chunks = higher latency but smoother playback

## System Optimization Tips

### Memory Management
1. Monitor RAM usage:
   - Normal: 2-4GB
   - High: 4-8GB
   - If exceeding 8GB, consider:
     - Reducing context window
     - Lowering queue sizes
     - Using smaller models

### CPU Usage
1. Thread Priority:
   - Audio thread: High priority
   - Content generation: Normal priority
   - Can be adjusted in OS settings

2. Process Priority:
   - Run with elevated priority for better performance
   - Windows: Run as administrator
   - Linux: Nice value adjustment

### Disk Usage
1. Log Management:
   - Logs are not automatically rotated
   - Manually clear logs periodically
   - Consider implementing log rotation

## Recommended Configurations

### Low-End System
```python
# Content Generator
context_text = '\n'.join(self.context[-2:])
self.text_queue = Queue(maxsize=1)

# Stream Manager
self.audio_queue = queue.Queue(maxsize=1)
self.sample_rate = 16000
gpu = False
```

### Mid-Range System (Recommended)
```python
# Content Generator
context_text = '\n'.join(self.context[-3:])
self.text_queue = Queue(maxsize=2)

# Stream Manager
self.audio_queue = queue.Queue(maxsize=2)
self.sample_rate = 22050
gpu = False  # True if NVIDIA GPU available
```

### High-End System
```python
# Content Generator
context_text = '\n'.join(self.context[-5:])
self.text_queue = Queue(maxsize=3)

# Stream Manager
self.audio_queue = queue.Queue(maxsize=3)
self.sample_rate = 44100
gpu = True
```

## Performance Monitoring
- Monitor system resources:
  ```python
  import psutil  # Add to requirements.txt
  
  # Check CPU usage
  cpu_percent = psutil.cpu_percent()
  
  # Check memory usage
  memory_info = psutil.Process().memory_info()
  ```

## Troubleshooting Performance Issues

### High Latency
1. Check queue sizes
2. Reduce context window
3. Lower sample rate
4. Monitor system resources

### Memory Leaks
1. Clear context periodically
2. Implement queue size limits
3. Monitor memory growth
4. Implement garbage collection calls

### GPU Issues
1. Check CUDA installation
2. Monitor VRAM usage
3. Consider fallback to CPU
4. Update GPU drivers