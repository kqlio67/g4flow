# G4Flow

<div align="center">
  <h3>A powerful, open-source AI chat assistant built with Streamlit and G4F</h3>
</div>

G4Flow is a versatile chat application that provides an intuitive interface for interacting with various AI models — text conversations, image generation, image variations, audio (TTS), video generation, and document analysis. It leverages the [G4F (GPT4Free) framework](https://github.com/xtekky/gpt4free) to offer access to multiple AI models through a clean, user-friendly interface.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### 💬 Chat Capabilities
- **Grouped Model Selection**: Models organized by provider (OpenAI, Google, Meta, DeepSeek, Mistral, and more) for easy navigation across 100+ models
- **System Message Templates**: Customize AI behavior with predefined templates (Default, Creative, Academic, Programming, Friendly, Fitness) or create custom ones
- **Image Analysis**: Upload images for the AI to analyze and discuss using vision models
- **Web Search Integration**: Search the web using DuckDuckGo with source citations displayed as clickable references
- **Response Streaming**: View AI responses as they are generated in real-time
- **Native Reasoning Display**: Shows the reasoning process for DeepSeek-R1 and similar models with thinking duration, using g4f's native `Reasoning` API with regex fallback
- **Conversation History Toggle**: Enable/disable conversation history while maintaining system instructions
- **JSON Mode**: Force structured JSON output from models for programming use cases
- **Max Tokens & Stop Sequences**: Fine-tune response length and stop conditions
- **Token Usage Tracking**: Per-message and cumulative session token counts (prompt, completion, reasoning)
- **Document Upload & Analysis**: Upload TXT, PDF, DOCX, CSV, JSON, Markdown, and code files to analyze in chat

### 🖼️ Image Generation
- **Multiple Image Models**: 390+ image models including DALL-E 3, Midjourney, Flux, Stable Diffusion, and more
- **Prompt Improvement**: Automatically enhance image prompts for better results and translate non-English prompts to English
- **Image History**: View previously generated images in the chat history

### 🎨 Image Variation
- **Upload & Vary**: Upload an existing image and generate variations of it using any supported image model

### 🎵 Audio (TTS)
- **Text-to-Speech**: Convert text to audio using multiple voices (alloy, echo, fable, onyx, nova, shimmer)
- **Transcript Display**: View transcripts alongside generated audio when available

### 🎬 Video Generation
- **AI Video**: Generate videos from text prompts using 27+ video models
- **Auto-Download**: Optionally save generated videos locally

### 🔌 Custom Provider
- **Connect Your Own LLM**: Use Ollama, LM Studio, or any OpenAI-compatible API by entering a base URL and optional API key

### 💾 Media Management
- **Save Generated Files**: Toggle saving of generated images, audio, and videos to `generated_media/` folder
- **Chat Export**: Export full chat history as JSON with embedded images and token usage data

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/kqlio67/g4flow.git
   cd g4flow
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit application:
   ```bash
   streamlit run app.py
   ```

5. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501).

## 📋 Repository Structure

```
g4flow/
├── app.py                  # Main Streamlit application code
├── requirements.txt        # Project dependencies
├── generated_media/        # Auto-generated media files (images, audio, video)
├── .gitignore             # Git ignore file
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Guidelines for contributors
└── README.md             # Project documentation
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `g4f` | AI model client (chat, images, video, audio) |
| `g4f[search]` | Web search via DuckDuckGo |
| `pypdf2` | PDF document reading |
| `pdfplumber` | PDF document reading (fallback) |
| `python-docx` | DOCX document reading |
| `docx2txt` | DOCX document reading (fallback) |

## 🔧 Advanced Configuration

- **System Messages**: Add new templates in the `SYSTEM_MESSAGES` dictionary in `app.py`
- **Custom Provider**: Enter an OpenAI-compatible API URL in the Advanced Settings sidebar section
- **Max Tokens / Stop Sequences**: Configure under Advanced Settings in the sidebar
- **JSON Mode**: Enable in chat settings to force structured JSON output
- **Styling**: Edit the CSS in `apply_custom_styling()` in `app.py`

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## 📄 License

Licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 👥 Contributors

<a href="https://github.com/kqlio67/g4flow/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kqlio67/g4flow" />
</a>

## 🙏 Acknowledgments

- Built with the [G4F framework](https://github.com/xtekky/gpt4free)
- Powered by [Streamlit](https://streamlit.io/)
- Thanks to all the contributors who have helped improve this project

## ⚠️ Disclaimer

This project is for educational purposes only. Please ensure you comply with the terms of service for all AI providers and APIs used through the G4F framework.

---

<div align="center">
  <p>If you find this project useful, please consider giving it a star ⭐</p>
  <p>Made with ❤️ by <a href="https://github.com/kqlio67">kqlio67</a></p>
</div>
