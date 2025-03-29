# G4Flow

<div align="center">
  <h3>A powerful, open-source AI chat assistant repository built with Streamlit and G4F</h3>
</div>

G4Flow is a versatile chat application repository that provides code for building an intuitive interface for interacting with various AI models for both text conversations and image generation. This repository leverages the [G4F (GPT4Free) framework](https://github.com/xtekky/gpt4free) to offer access to multiple AI models through a clean, user-friendly interface.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## ✨ Features

### 💬 Chat Capabilities
- **Extensive Model Selection**: Access a wide range of AI models loaded directly from the g4f framework:
  - **OpenAI**: GPT-4, GPT-4o, o1, o3-mini
  - **DeepSeek**: deepseek-r1, deepseek-v3
  - **Anthropic**: Claude 3 models (Haiku, Sonnet)
  - **Google**: Gemini models (1.5 Flash, 1.5 Pro, 2.0 Flash)
  - **Meta**: Llama 3 models (8B, 70B, 405B)
  - **Other Models**: Mixtral, Phi-4, and more
  - **Evil Mode**: Experimental uncensored model without content filtering (use with caution)
  - For a complete list of supported models, see the [official g4f documentation](https://github.com/xtekky/gpt4free/blob/main/docs/providers-and-models.md#text-generation-models)
- **System Message Templates**: Customize AI behavior with predefined templates:
  - Default, Creative, Academic, Programming, Friendly, Fitness
  - Option to create custom templates for personalized instructions
- **Image Analysis**: Upload images for the AI to analyze and discuss
- **Web Search Integration**: Enable web search capabilities using DuckDuckGo
- **Response Streaming**: View AI responses as they are generated in real-time
- **Reasoning Display**: Shows the step-by-step reasoning process for DeepSeek-R1 based models with detailed thinking process and duration
- **Conversation History Toggle**: Option to enable/disable conversation history while maintaining system instructions

### 🎨 Image Generation
- **Multiple Image Models**: Generate images using various AI models loaded from the g4f framework:
  - DALL-E 3
  - Midjourney
  - Flux (standard, dev, and schnell variants)
  - For a complete list of supported image models, see the [official g4f documentation](https://github.com/xtekky/gpt4free/blob/main/docs/providers-and-models.md#image-generation-models)
- **Prompt Improvement**: Automatically enhance image prompts for better results and translate non-English prompts to English
- **Simple Interface**: Describe the image you want to generate in natural language
- **Image History**: View previously generated images in the chat history
- **Toggle Option**: Enable/disable image generation as needed

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
├── requirements.txt        # Repository dependencies
├── .gitignore             # Git ignore file
├── LICENSE                # MIT License
├── CONTRIBUTING.md        # Guidelines for contributors
└── README.md             # Repository documentation
```

## 🔧 Advanced Configuration

For advanced users, you can customize the application by:

1. Adding new system message templates in the `SYSTEM_MESSAGES` dictionary in `app.py`
2. Modifying the list of available models in the sidebar selectbox
3. Adjusting the styling by editing the CSS in the st.markdown sections

## 🤝 Contributing

Contributions to this repository are welcome! Please see our [Contributing Guidelines](CONTRIBUTING.md) for more details on how to get involved.

## 📄 License

This repository is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with the [G4F framework](https://github.com/xtekky/gpt4free)
- Powered by [Streamlit](https://streamlit.io/)
- Thanks to all the contributors who have helped improve this repository

## 🔒 Hidden Models

The repository includes support for several models that are hidden from the default interface due to stability issues, limited provider support, or other technical reasons:

```
HIDDEN_MODELS = ["o1-mini", "GigaChat:latest", "meta-ai", "llama-2-7b", "llama-3-8b", "llama-3-70b", "llama-3", "llama-3.2-1b", "llama-3.2-11b", "mixtral-8x7b","phi-3.5-mini", "gemini-2.0", "gemini-exp", "gemini-2.0-flash-thinking", "gemini-2.0-pro", "claude-3-sonnet", "claude-3-opus", "claude-3.5-sonnet", "claude-3.7-sonnet-thinking", "reka-core", "qwen-1.5-7b", "qwen-2-vl-7b", "qwen-2.5-72b", "qwq-32b", "pi", "grok-3", "grok-3-r1", "MiniMax", "sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "r1-1776"]
```

These models may be unstable, work poorly, or have limited provider support. Advanced users can modify the application code to enable these models if needed.

## ⚠️ Disclaimer

This repository is for educational purposes only. Please ensure you comply with the terms of service for all AI providers and APIs used through the G4F framework.

---

<div align="center">
  <p>If you find this repository useful, please consider giving it a star ⭐</p>
  <p>Made with ❤️ by <a href="https://github.com/kqlio67">kqlio67</a></p>
</div>
