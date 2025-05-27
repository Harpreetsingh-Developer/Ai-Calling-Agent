# AI Calling Agent

A sophisticated AI-powered calling agent system with text-to-speech capabilities for multiple languages.

## Features

- High-quality text-to-speech synthesis for multiple languages (English, Hindi, Marathi, Telugu)
- Multiple TTS engines (Google TTS, Indic-TTS via ModelScope)
- Web-based chat interface
- Automated calling features
- API endpoints for speech synthesis

## Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- MongoDB (for storing conversations and call logs)
- CUDA-compatible GPU (optional, for faster TTS synthesis)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AiCallingAgent.git
   cd AiCallingAgent
   ```

2. Run the setup script to prepare the environment:
   ```bash
   ./setup.py
   ```
   
   This script will:
   - Create necessary directories
   - Install required dependencies
   - Test the TTS functionality

   For additional options, run:
   ```bash
   ./setup.py --help
   ```

3. Configure the application by creating a `.env` file in the root directory:
   ```
   # MongoDB connection
   MONGODB_URL=mongodb://localhost:27017
   
   # Google Cloud credentials (required for Google TTS)
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json
   
   # Indic-TTS model directory (optional)
   INDIC_TTS_MODELS_DIR=/path/to/your/models
   ```

### Running the Application

To start the application:

```bash
./run.py
```

This will start the server at http://localhost:8000.

For development mode with auto-reload:

```bash
./run.py --reload
```

For additional options:

```bash
./run.py --help
```

## Testing

### Testing TTS functionality

To test the TTS (Text-to-Speech) functionality:

```bash
./tests/test_tts.py
```

This will generate test audio files in the `test_outputs` directory.

Options:
```bash
./tests/test_tts.py --languages en,hi --engines google,indic
```

## TTS Engine Selection

The application uses a unified TTS service that selects the best engine based on:

1. Language - Different engines perform better for different languages
2. Availability - Falls back if a preferred engine is not available
3. User preference - Can be manually selected in the UI

Default preferences:
- English: Google TTS
- Indian languages (Hindi, Marathi, Telugu): Indic-TTS (via ModelScope)

## Troubleshooting

### TTS Issues

- If Indic-TTS fails to initialize, the system will automatically fall back to Google TTS
- Check the logs at `logs/ai_calling_agent.log` and `logs/errors.log` for detailed error messages
- For model loading issues, ensure you have sufficient RAM (8GB+ recommended)

### Installation Issues

- If the `setup.py` script fails, try installing dependencies manually:
  ```bash
  pip install -r requirements.txt
  pip install modelscope  # For Indic-TTS support
  ```

- For CUDA-related errors, ensure you have compatible NVIDIA drivers installed

## Documentation

For detailed documentation on the Indic-TTS integration, see [docs/indic_tts_integration.md](docs/indic_tts_integration.md).

## License

[MIT License](LICENSE) 