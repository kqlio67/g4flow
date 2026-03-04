import streamlit as st
import asyncio
import io
import os
import aiohttp
import re
import time
import base64
import json
import tempfile
from datetime import datetime
from pathlib import Path
from g4f.client import AsyncClient, create_custom_provider
from g4f.providers.any_provider import AnyProvider

# Constants - using AnyProvider for dynamic model discovery
MEDIA_DIR = "generated_media"
IMAGE_MODELS = AnyProvider.image_models if hasattr(AnyProvider, 'image_models') else []
AUDIO_MODELS = AnyProvider.audio_models if hasattr(AnyProvider, 'audio_models') else []
VIDEO_MODELS = AnyProvider.video_models if hasattr(AnyProvider, 'video_models') else []

# Voice options for TTS
VOICE_OPTIONS = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

# Supported document types for file upload & analysis
DOCUMENT_EXTENSIONS = ["txt", "md", "csv", "json", "py", "js", "html", "css", "xml", "yaml", "log", "sql", "sh"]
DOCUMENT_EXTENSIONS_EXTRA = ["pdf", "docx"]  # Require optional deps

SYSTEM_MESSAGES = {
    "Default": "You are a helpful assistant.",
    "Creative": "You are a creative assistant with a vivid imagination. Think outside the box and provide innovative solutions.",
    "Academic": "You are an academic assistant with expertise in research. Provide thorough, well-reasoned responses with academic precision.",
    "Programming": "You are a programming expert. Provide clean, efficient, and well-documented code with explanations.",
    "Friendly": "You are a friendly conversational assistant. Respond in a warm, casual tone like talking to a friend.",
    "Fitness": "You are a fitness and health assistant. Provide evidence-based advice on workouts, nutrition, wellness, and overall fitness goals.",
    "Custom": "custom"
}

QUICK_PROMPTS = {
    "📝 Summarize": "Summarize the following: ",
    "🔍 Explain": "Explain in simple terms: ",
    "💻 Code": "Write code for: ",
    "🌐 Translate": "Translate to English: ",
}


# ============== Styling ==============
def apply_custom_styling():
    """Apply custom CSS styling with dark theme support"""
    st.markdown("""
    <style>
    /* Chat message styling */
    .stChatMessage {
        padding: 1rem 1rem 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        padding-bottom: 0 !important;
    }
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chat input */
    .stChatInputContainer {
        padding-top: 1rem;
        padding-bottom: 1rem;
        background-color: rgba(240, 242, 246, 0.5);
        border-radius: 10px;
    }
    
    /* Mobile padding */
    .main {
        padding-bottom: 50px;
    }
    
    /* Footer - exact Streamlit sidebar width */
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 256px;
        text-align: center;
        padding: 10px;
        font-size: 0.8em;
        z-index: 999;
        background-color: #f0f2f6;
        border-top: 1px solid #ddd;
        color: #666;
        box-sizing: border-box;
    }
    
    .footer a {
        color: #4F8BF9;
        text-decoration: none;
    }
    
    .footer a:hover {
        text-decoration: underline;
    }
    
    /* Dark theme for footer */
    @media (prefers-color-scheme: dark) {
        .footer {
            background-color: #262730;
            border-top: 1px solid #444;
            color: #a0a0a0;
        }
    }
    
    /* Mobile footer */
    @media (max-width: 768px) {
        .footer {
            width: 100vw;
            font-size: 0.7em;
            padding: 5px;
        }
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .typing-indicator-dot {
        background-color: #555;
        border-radius: 50%;
        width: 8px;
        height: 8px;
        margin: 0 2px;
        animation: typing-indicator 1.5s infinite ease-in-out;
    }
    .typing-indicator-dot:nth-child(2) {
        animation-delay: 0.2s;
    }
    .typing-indicator-dot:nth-child(3) {
        animation-delay: 0.4s;
    }
    @keyframes typing-indicator {
        0% { opacity: 0.2; transform: scale(0.8); }
        20% { opacity: 1; transform: scale(1); }
        100% { opacity: 0.2; transform: scale(0.8); }
    }
    
    /* Token usage badge */
    .token-badge {
        display: inline-block;
        background: rgba(79, 139, 249, 0.1);
        color: #4F8BF9;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75em;
        margin-top: 4px;
    }
    
    /* Source links styling */
    .source-link {
        display: inline-block;
        background: rgba(79, 139, 249, 0.08);
        padding: 4px 10px;
        border-radius: 6px;
        margin: 2px 4px 2px 0;
        font-size: 0.85em;
    }
    </style>
    """, unsafe_allow_html=True)


# ============== Session State ==============
def initialize_session_state():
    """Initialize all session state variables"""
    defaults = {
        "messages": [],
        "system_message": SYSTEM_MESSAGES["Default"],
        "system_message_template": "Default",
        "custom_system_message": "",
        "image_model": IMAGE_MODELS[0] if IMAGE_MODELS else "",
        "improve_prompt": True,
        "conversation_history": True,
        "quick_prompt_prefix": "",
        "regenerate": False,
        "audio_voice": VOICE_OPTIONS[0] if VOICE_OPTIONS else "alloy",
        "video_model": VIDEO_MODELS[0] if VIDEO_MODELS else "",
        "save_generated_files": True,
        # New feature defaults
        "max_tokens": 0,  # 0 = unlimited
        "stop_sequences": "",
        "json_mode": False,
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "custom_provider_url": "",
        "custom_provider_key": "",
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ============== Utility Functions ==============
def get_grouped_text_models():
    """Get text/vision models from AnyProvider, grouped by category.
    Returns list of dicts: [{"group": "Label", "models": [...]}, ...]
    """
    try:
        grouped = AnyProvider.get_grouped_models()
        # Filter out image and video groups, keep only text/vision models
        media_models = set(
            list(AnyProvider.image_models) +
            list(AnyProvider.audio_models) +
            list(AnyProvider.video_models)
        )
        result = []
        for group in grouped:
            if group["group"] in ("Image Generation", "Video Generation"):
                continue
            filtered = [m for m in group["models"] if m not in media_models]
            if filtered:
                result.append({"group": group["group"], "models": filtered})
        return result
    except Exception:
        # Fallback to flat list
        return [{"group": "All Models", "models": get_text_and_vision_models_flat()}]


def get_text_and_vision_models_flat(ignored: list = None):
    """Fallback: get flat text/vision model list"""
    if ignored is None:
        ignored = []
    
    all_models = AnyProvider.get_models(ignored=ignored)
    
    text_models = [
        m for m in all_models 
        if m not in AnyProvider.image_models 
        and m not in AnyProvider.audio_models
        and m not in AnyProvider.video_models
    ]
    
    return ["default"] + sorted([m for m in text_models if m != "default"])


def extract_thinking(text):
    """Extract thinking content and final response from text"""
    thinking_pattern = r'<think>(.*?)</think>'
    thinking_content = re.findall(thinking_pattern, text, re.DOTALL)
    final_response = re.sub(thinking_pattern, '', text, flags=re.DOTALL)
    return thinking_content, final_response.strip()


def extract_sources_from_response(text):
    """Extract source citations [[N]](url) from response text"""
    pattern = r'\[\[(\d+)\]\]\((https?://[^\s\)]+)\)'
    matches = re.findall(pattern, text)
    if matches:
        return [{"index": int(idx), "url": url} for idx, url in matches]
    return []


def typing_indicator():
    """Display typing indicator animation"""
    st.markdown("""
    <div class="typing-indicator">
        <div class="typing-indicator-dot"></div>
        <div class="typing-indicator-dot"></div>
        <div class="typing-indicator-dot"></div>
    </div>
    """, unsafe_allow_html=True)


def display_token_usage(usage):
    """Display token usage info from response"""
    if usage is None:
        return
    prompt_tokens = getattr(usage, 'prompt_tokens', 0) or 0
    completion_tokens = getattr(usage, 'completion_tokens', 0) or 0
    total = getattr(usage, 'total_tokens', 0) or (prompt_tokens + completion_tokens)
    
    if total > 0:
        # Update session totals
        st.session_state.total_prompt_tokens += prompt_tokens
        st.session_state.total_completion_tokens += completion_tokens
        
        reasoning_tokens = 0
        if hasattr(usage, 'completion_tokens_details') and usage.completion_tokens_details:
            reasoning_tokens = getattr(usage.completion_tokens_details, 'reasoning_tokens', 0) or 0
        
        parts = [f"📊 {prompt_tokens}→{completion_tokens}"]
        if reasoning_tokens > 0:
            parts.append(f"🧠 {reasoning_tokens}")
        parts.append(f"Σ {total}")
        
        st.caption(" | ".join(parts))


def display_sources(text):
    """Display extracted web search sources below the response"""
    sources = extract_sources_from_response(text)
    if sources:
        with st.expander(f"📎 Sources ({len(sources)})", expanded=False):
            for src in sources:
                domain = src["url"].split("/")[2] if len(src["url"].split("/")) > 2 else src["url"]
                st.markdown(f'<span class="source-link">[{src["index"]}] [{domain}]({src["url"]})</span>', unsafe_allow_html=True)


def read_uploaded_document(uploaded_file):
    """Extract text content from uploaded document file"""
    filename = uploaded_file.name
    ext = os.path.splitext(filename)[1].lower()
    
    try:
        if ext == ".pdf":
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(uploaded_file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
                return text.strip()
            except ImportError:
                try:
                    import pdfplumber
                    with pdfplumber.open(uploaded_file) as pdf:
                        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    return text.strip()
                except ImportError:
                    st.warning("Install `pypdf2` or `pdfplumber` for PDF support: `pip install pypdf2`")
                    return None
        elif ext == ".docx":
            try:
                from docx import Document
                doc = Document(uploaded_file)
                text = "\n".join(para.text for para in doc.paragraphs)
                return text.strip()
            except ImportError:
                try:
                    import docx2txt
                    # Save to temp file for docx2txt
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    text = docx2txt.process(tmp_path)
                    os.remove(tmp_path)
                    return text.strip()
                except ImportError:
                    st.warning("Install `python-docx` for DOCX support: `pip install python-docx`")
                    return None
        else:
            # Plain text-based formats
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode("utf-8", errors="ignore")
            return content.strip()
    except Exception as e:
        st.error(f"Error reading file: {str(e)}")
        return None


def export_chat_data():
    """Prepare chat data for export with images included"""
    export_data = {
        "exported_at": datetime.now().isoformat(),
        "system_message": st.session_state.system_message,
        "total_messages": len(st.session_state.messages),
        "messages": []
    }
    
    for msg in st.session_state.messages:
        msg_data = {
            "role": msg["role"],
            "content": msg["content"]
        }
        if "thinking" in msg:
            msg_data["thinking"] = msg["thinking"]
            msg_data["thinking_duration"] = msg.get("thinking_duration", 0)
        if "image_base64" in msg:
            msg_data["image_base64"] = msg["image_base64"]
        if "token_usage" in msg:
            msg_data["token_usage"] = msg["token_usage"]
        export_data["messages"].append(msg_data)
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def get_client():
    """Create AsyncClient with optional custom provider"""
    custom_url = st.session_state.get("custom_provider_url", "").strip()
    custom_key = st.session_state.get("custom_provider_key", "").strip()
    
    if custom_url:
        try:
            provider = create_custom_provider(
                base_url=custom_url,
                api_key=custom_key if custom_key else None
            )
            return AsyncClient(provider=provider)
        except Exception as e:
            st.warning(f"Custom provider error: {str(e)}. Falling back to default.")
    
    return AsyncClient()


# ============== Image Generation ==============
async def improve_prompt(prompt):
    """Improve image generation prompt using the default chat model"""
    client = AsyncClient()
    
    system_message = """You are an expert at creating high-quality image generation prompts. 
    Your task is to improve the given prompt to create better images. 
    If the prompt is not in English, translate it to English.
    Your response should ONLY contain the improved prompt text without any explanations.
    Focus on adding details that will make the image more vivid and visually appealing."""
    
    try:
        response = await client.chat.completions.create(
            model="default",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Original prompt: {prompt}\n\nImproved prompt (in English):"}
            ]
        )
        improved = response.choices[0].message.content.strip()
        if not improved:
            raise ValueError("Empty response from model")
        return improved
    except Exception as e:
        st.error(f"❌ Prompt improvement failed: {str(e)}")
        return None


async def generate_image(prompt, model_name):
    """Generate an image using G4F API"""
    client = AsyncClient()
    
    try:
        response = await client.images.generate(
            prompt=prompt,
            model=model_name,
            response_format="b64_json"
        )
        
        if response.data and response.data[0].b64_json:
            return response.data[0].b64_json
        return None
    except Exception as e:
        st.error(f"❌ Error generating image: {str(e)}")
        return None


async def generate_image_variation(image_data, model_name):
    """Generate an image variation from an uploaded image"""
    client = AsyncClient()
    
    try:
        response = await client.images.create_variation(
            image=image_data,
            model=model_name,
            response_format="b64_json"
        )
        
        if response.data and response.data[0].b64_json:
            return response.data[0].b64_json
        return None
    except Exception as e:
        st.error(f"❌ Error generating image variation: {str(e)}")
        return None


async def generate_audio(text, voice="alloy"):
    """Generate audio (TTS) using G4F API"""
    client = AsyncClient()
    
    try:
        response = await client.chat.completions.create(
            model="openai-audio",
            messages=[{"role": "user", "content": text}],
            audio={"voice": voice, "format": "mp3"},
        )
        return response.choices[0].message
    except Exception as e:
        st.error(f"❌ Error generating audio: {str(e)}")
        return None


async def generate_video(prompt, model_name):
    """Generate video using G4F API"""
    client = AsyncClient()
    
    try:
        result = await client.media.generate(
            model=model_name,
            prompt=prompt,
            response_format="url"
        )
        
        if result.data and result.data[0].url:
            return result.data[0].url
        return None
    except Exception as e:
        st.error(f"❌ Error generating video: {str(e)}")
        return None


# ============== Chat Response ==============
async def generate_response(messages, model, web_search, image, streaming, show_thinking, max_tokens=None, stop=None, response_format=None):
    """Generate AI response with streaming, thinking, and error handling"""
    client = get_client()
    
    kwargs = {
        "model": model,
        "messages": messages,
        "web_search": web_search
    }
    if image is not None:
        kwargs["image"] = image
    if max_tokens and max_tokens > 0:
        kwargs["max_tokens"] = max_tokens
    if stop:
        kwargs["stop"] = stop
    if response_format:
        kwargs["response_format"] = response_format

    thinking_duration = 0
    usage_data = None
    indicator_placeholder = st.empty()

    try:
        if streaming:
            with indicator_placeholder:
                typing_indicator()

            stream = client.chat.completions.stream(**kwargs)
            full_response = ""
            thinking_content = ""
            in_thinking = False
            thinking_start_time = 0
            thinking_placeholder = st.empty()
            message_placeholder = st.empty()
            expander = None
            first_chunk_received = False
            
            async for chunk in stream:
                if not first_chunk_received:
                    first_chunk_received = True
                    indicator_placeholder.empty()
                
                # Check for native reasoning support
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    
                    # Native reasoning from g4f Reasoning class
                    if hasattr(delta, 'reasoning') and delta.reasoning:
                        reasoning_text = str(delta.reasoning)
                        if reasoning_text:
                            if not expander and show_thinking:
                                thinking_start_time = time.time() if thinking_start_time == 0 else thinking_start_time
                                expander = thinking_placeholder.expander("🤔 Is thinking...", expanded=True)
                            thinking_content += reasoning_text
                            if show_thinking and expander:
                                with expander:
                                    st.markdown(thinking_content)
                            continue
                    
                    if delta.content:
                        content = delta.content
                        
                        if not isinstance(content, str):
                            continue
                        
                        full_response += content
                        
                        # Fallback: manual <think> tag parsing
                        if "<think>" in content:
                            in_thinking = True
                            thinking_start_time = time.time() if thinking_start_time == 0 else thinking_start_time
                            
                            if show_thinking and not expander:
                                expander = thinking_placeholder.expander("🤔 Is thinking...", expanded=True)
                        
                        if in_thinking:
                            thinking_content += content
                            
                            if "</think>" in content:
                                in_thinking = False
                                thinking_duration = time.time() - thinking_start_time
                                
                                if show_thinking and expander:
                                    _, parts = thinking_content.split("<think>", 1)
                                    thinking_text, _ = parts.split("</think>", 1)
                                    
                                    with expander:
                                        st.markdown(thinking_text)
                                    
                                    expander.label = f"Thought for {thinking_duration:.2f}s"
                                
                                thinking_content = ""
                        
                        _, clean_text = extract_thinking(full_response)
                        cursor = ["▌", "▐"][int(time.time() * 4) % 2]
                        message_placeholder.markdown(clean_text + cursor)
                        
                        await asyncio.sleep(0.02)
                
                # Capture usage from final chunk
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage_data = chunk.usage
            
            if thinking_content and thinking_start_time and not thinking_duration:
                thinking_duration = time.time() - thinking_start_time
                if show_thinking and expander:
                    expander.label = f"Thought for {thinking_duration:.2f}s"
            
            _, clean_text = extract_thinking(full_response)
            message_placeholder.markdown(clean_text)
            
            # Display sources from web search
            if web_search:
                display_sources(clean_text)
            
            return full_response, thinking_duration, usage_data
        
        else:
            with indicator_placeholder:
                typing_indicator()
            
            thinking_start_time = time.time()
            response = await client.chat.completions.create(**kwargs)
            indicator_placeholder.empty()
            
            content = response.choices[0].message.content
            
            if not isinstance(content, str):
                content = str(content) if content else ""
            
            # Check for native reasoning field
            native_reasoning = getattr(response.choices[0].message, 'reasoning', None)
            
            thinking_sections, cleaned_response = extract_thinking(content)
            
            # Use native reasoning if available, fallback to regex
            if native_reasoning:
                thinking_duration = time.time() - thinking_start_time
                if show_thinking:
                    with st.expander(f"Thought for {thinking_duration:.2f}s", expanded=False):
                        st.markdown(str(native_reasoning))
            elif thinking_sections:
                thinking_duration = time.time() - thinking_start_time
                if show_thinking:
                    with st.expander(f"Thought for {thinking_duration:.2f}s", expanded=False):
                        st.markdown(thinking_sections[-1])
            
            # Render response (JSON mode formatting)
            if response_format and response_format.get("type") == "json_object":
                try:
                    parsed_json = json.loads(cleaned_response)
                    st.json(parsed_json)
                except (json.JSONDecodeError, TypeError):
                    st.markdown(cleaned_response)
            else:
                st.markdown(cleaned_response)
            
            # Display sources
            if web_search:
                display_sources(cleaned_response)
            
            # Capture usage
            usage_data = getattr(response, 'usage', None)
            
            return content, thinking_duration, usage_data

    except Exception as e:
        indicator_placeholder.empty()
        error_msg = f"❌ Error generating response: {str(e)}"
        st.error(error_msg)
        return error_msg, 0, None


# ============== Handlers ==============
async def handle_image_generation(prompt):
    """Handle image generation workflow"""
    image_prompt = prompt.strip()
    final_prompt = image_prompt
    improved_prompt_message = ""
    
    if not st.session_state.image_model:
        with st.chat_message("assistant"):
            st.error("❌ No image model available.")
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "No image model available.",
            "is_generated_image": False
        })
        return
    
    with st.spinner("Processing image request..."):
        if st.session_state.improve_prompt:
            with st.status("Improving prompt...", expanded=False) as status:
                final_prompt = await improve_prompt(image_prompt)
                if final_prompt is None:
                    status.update(label="❌ Prompt improvement failed", state="error")
                    with st.chat_message("assistant"):
                        st.error("❌ Prompt improvement failed. Disable 'Improve Prompts' to use your original prompt, or try again.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Prompt improvement failed. Disable 'Improve Prompts' to send your original prompt directly.",
                        "is_generated_image": False
                    })
                    return
                status.update(label="✅ Prompt improved!", state="complete")
            
            if final_prompt != image_prompt:
                improved_prompt_message = f"Improved prompt: \"{final_prompt}\"\n\n"
        
        with st.status("Generating image...", expanded=False) as status:
            base64_image = await generate_image(final_prompt, st.session_state.image_model)
            status.update(label="✅ Image generated!", state="complete")
        
        if base64_image:
            try:
                image_bytes = base64.b64decode(base64_image)
                
                if st.session_state.save_generated_files:
                    os.makedirs(MEDIA_DIR, exist_ok=True)
                    image_filename = os.path.join(MEDIA_DIR, f"image_{int(time.time())}.png")
                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)
                
                with st.chat_message("assistant"):
                    message_content = f'Generated image using {st.session_state.image_model}'
                    if improved_prompt_message:
                        message_content += f'\n\nOriginal prompt: "{image_prompt}"\n{improved_prompt_message}'
                    else:
                        message_content += f' for prompt: "{image_prompt}"'
                    
                    st.markdown(message_content)
                    st.image(image_bytes)
                
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": message_content,
                    "image_base64": base64_image,
                    "is_generated_image": True
                })
                
            except Exception as e:
                st.error(f"❌ Error processing image: {str(e)}")
        else:
            with st.chat_message("assistant"):
                st.error("❌ Failed to generate image. Please try again.")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Failed to generate image.",
                "is_generated_image": False
            })


async def handle_image_variation(source_image):
    """Handle image variation workflow"""
    if not st.session_state.image_model:
        with st.chat_message("assistant"):
            st.error("❌ No image model available.")
        return
    
    with st.spinner("Generating image variation..."):
        with st.status("Creating variation...", expanded=False) as status:
            image_data = io.BytesIO(source_image.read())
            base64_image = await generate_image_variation(image_data, st.session_state.image_model)
            status.update(label="✅ Variation generated!", state="complete")
        
        if base64_image:
            try:
                image_bytes = base64.b64decode(base64_image)
                
                if st.session_state.save_generated_files:
                    os.makedirs(MEDIA_DIR, exist_ok=True)
                    image_filename = os.path.join(MEDIA_DIR, f"variation_{int(time.time())}.png")
                    with open(image_filename, "wb") as f:
                        f.write(image_bytes)
                
                with st.chat_message("assistant"):
                    message_content = f'Generated image variation using {st.session_state.image_model}'
                    st.markdown(message_content)
                    st.image(image_bytes)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message_content,
                    "image_base64": base64_image,
                    "is_generated_image": True
                })
            except Exception as e:
                st.error(f"❌ Error processing variation: {str(e)}")
        else:
            with st.chat_message("assistant"):
                st.error("❌ Failed to generate image variation.")


async def handle_audio_generation(text, voice):
    """Handle audio generation workflow (TTS)"""
    if not text.strip():
        with st.chat_message("assistant"):
            st.error("❌ Please provide text to convert to speech.")
        return
    
    with st.spinner("Generating audio..."):
        with st.status("Converting text to speech...", expanded=False) as status:
            audio_response = await generate_audio(text, voice)
            status.update(label="✅ Audio generated!", state="complete")
        
        if audio_response:
            try:
                audio_bytes = None
                transcript = None
                
                # Try native AudioResponseModel first (g4f improved audio handling)
                if hasattr(audio_response, 'audio') and audio_response.audio:
                    audio_data = audio_response.audio
                    if hasattr(audio_data, 'data') and audio_data.data:
                        # base64 encoded audio data
                        audio_bytes = base64.b64decode(audio_data.data)
                    if hasattr(audio_data, 'transcript'):
                        transcript = audio_data.transcript
                
                # Fallback to save() method
                if audio_bytes is None:
                    if st.session_state.save_generated_files:
                        os.makedirs(MEDIA_DIR, exist_ok=True)
                        audio_filename = os.path.join(MEDIA_DIR, f"audio_{int(time.time())}.mp3")
                        if hasattr(audio_response, 'save'):
                            audio_response.save(audio_filename)
                            with open(audio_filename, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                    else:
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                            temp_path = tmp_file.name
                        if hasattr(audio_response, 'save'):
                            audio_response.save(temp_path)
                            with open(temp_path, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                            os.remove(temp_path)
                
                if audio_bytes:
                    # Save to disk if enabled and not already saved
                    if st.session_state.save_generated_files and not os.path.exists(os.path.join(MEDIA_DIR, f"audio_{int(time.time())}.mp3")):
                        os.makedirs(MEDIA_DIR, exist_ok=True)
                        audio_filename = os.path.join(MEDIA_DIR, f"audio_{int(time.time())}.mp3")
                        with open(audio_filename, "wb") as f:
                            f.write(audio_bytes)
                    
                    with st.chat_message("assistant"):
                        message_content = f'🎵 Generated audio with voice "{voice}"'
                        if transcript:
                            message_content += f'\n\n📝 Transcript: {transcript}'
                        st.markdown(message_content)
                        st.audio(audio_bytes, format="audio/mp3")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": message_content,
                        "audio_bytes": base64.b64encode(audio_bytes).decode(),
                        "is_generated_audio": True
                    })
                else:
                    st.error("❌ Audio response format not supported.")
                    
            except Exception as e:
                st.error(f"❌ Error processing audio: {str(e)}")
        else:
            with st.chat_message("assistant"):
                st.error("❌ Failed to generate audio. Please try again.")


async def handle_video_generation(prompt):
    """Handle video generation workflow"""
    video_prompt = prompt.strip()
    
    if not st.session_state.get('video_model'):
        with st.chat_message("assistant"):
            st.error("❌ No video model available.")
        return
    
    with st.spinner("Generating video..."):
        with st.status("Generating video...", expanded=False) as status:
            video_url = await generate_video(video_prompt, st.session_state.video_model)
            status.update(label="✅ Video generated!", state="complete")
        
        if video_url:
            try:
                if st.session_state.save_generated_files:
                    try:
                        os.makedirs(MEDIA_DIR, exist_ok=True)
                        video_filename = os.path.join(MEDIA_DIR, f"video_{int(time.time())}.mp4")
                        
                        async with aiohttp.ClientSession() as session:
                            async with session.get(video_url) as resp:
                                if resp.status == 200:
                                    video_data = await resp.read()
                                    with open(video_filename, "wb") as f:
                                        f.write(video_data)
                                else:
                                    st.warning(f"⚠️ Could not download video (Status {resp.status})")
                    except Exception as download_err:
                        st.warning(f"⚠️ Failed to save video locally: {str(download_err)}")

                with st.chat_message("assistant"):
                    message_content = f'Generated video using {st.session_state.video_model} for prompt: "{video_prompt}"'
                    st.markdown(message_content)
                    st.video(video_url)
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": message_content,
                    "video_url": video_url,
                    "is_generated_video": True
                })
                
            except Exception as e:
                st.error(f"❌ Error processing video: {str(e)}")
        else:
            with st.chat_message("assistant"):
                st.error("❌ Failed to generate video. Please try again.")


async def handle_chat(prompt, model, web_search, image_upload, streaming, thinking, document_text=None):
    """Handle chat workflow"""
    image = None
    if image_upload is not None:
        image = io.BytesIO(image_upload.read())

    messages_for_api = []
    if st.session_state.system_message.strip():
        messages_for_api.append({"role": "system", "content": st.session_state.system_message})
    
    if st.session_state.conversation_history:
        messages_for_api.extend([
            {"role": m["role"], "content": m["content"]} 
            for m in st.session_state.messages
        ])
    else:
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            messages_for_api.append({
                "role": "user", 
                "content": st.session_state.messages[-1]["content"]
            })

    # Prepend document context to the last user message if available
    if document_text and messages_for_api:
        last_msg = messages_for_api[-1]
        if last_msg["role"] == "user":
            last_msg["content"] = f"[Uploaded Document Content]\n{document_text}\n\n[User Question]\n{last_msg['content']}"

    # Build extra kwargs
    max_tokens = st.session_state.get("max_tokens", 0)
    stop_str = st.session_state.get("stop_sequences", "").strip()
    stop = [s.strip() for s in stop_str.split(",") if s.strip()] if stop_str else None
    response_format = {"type": "json_object"} if st.session_state.get("json_mode", False) else None

    with st.chat_message("assistant"):
        full_response, thinking_duration, usage = await generate_response(
            messages_for_api, model, web_search, image, streaming, thinking,
            max_tokens=max_tokens if max_tokens > 0 else None,
            stop=stop,
            response_format=response_format
        )
    
    thinking_sections, cleaned_response = extract_thinking(full_response)
    
    response_data = {"role": "assistant", "content": cleaned_response}
    if thinking_sections:
        response_data["thinking"] = thinking_sections[-1]
        response_data["thinking_duration"] = thinking_duration
    
    # Store token usage in message
    if usage:
        prompt_tokens = getattr(usage, 'prompt_tokens', 0) or 0
        completion_tokens = getattr(usage, 'completion_tokens', 0) or 0
        total_tokens = getattr(usage, 'total_tokens', 0) or 0
        if total_tokens > 0 or prompt_tokens > 0 or completion_tokens > 0:
            response_data["token_usage"] = {
                "prompt": prompt_tokens,
                "completion": completion_tokens,
                "total": total_tokens
            }
    
    st.session_state.messages.append(response_data)
    
    # Display token usage after response
    if usage:
        display_token_usage(usage)


async def handle_regenerate(model, web_search, streaming, thinking, image_generation):
    """Regenerate the last response (text or image)"""
    if len(st.session_state.messages) < 2:
        return
    
    if st.session_state.messages[-1]["role"] == "assistant":
        st.session_state.messages.pop()
    
    last_user_msg = None
    for msg in reversed(st.session_state.messages):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break
    
    if last_user_msg:
        if image_generation:
            await handle_image_generation(last_user_msg)
        else:
            await handle_chat(last_user_msg, model, web_search, None, streaming, thinking)


# ============== UI Components ==============
def render_header():
    """Render app header"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: #4F8BF9;">G4Flow</h1>
    </div>
    """, unsafe_allow_html=True)


def render_quick_prompts():
    """Render quick action buttons"""
    cols = st.columns(len(QUICK_PROMPTS))
    for i, (label, prompt_prefix) in enumerate(QUICK_PROMPTS.items()):
        with cols[i]:
            if st.button(label, use_container_width=True, key=f"quick_{i}"):
                st.session_state.quick_prompt_prefix = prompt_prefix


def render_sidebar():
    """Render sidebar with all settings"""
    with st.sidebar:
        # System message
        selected_template = st.selectbox(
            "System Message",
            list(SYSTEM_MESSAGES.keys()),
            index=list(SYSTEM_MESSAGES.keys()).index(st.session_state.system_message_template),
            help="Define AI personality and behavior"
        )
        
        st.session_state.system_message_template = selected_template
        
        if selected_template == "Custom":
            custom_message = st.text_area(
                "Custom message",
                value=st.session_state.custom_system_message or "You are a helpful assistant that...",
                help="Write your own system instructions"
            )
            st.session_state.custom_system_message = custom_message
            st.session_state.system_message = custom_message
        else:
            st.session_state.system_message = SYSTEM_MESSAGES[selected_template]
        
        st.divider()

        # Generation mode selection (mutually exclusive)
        generation_mode = st.radio(
            "🎨 Generation Mode",
            ["💬 Chat", "🖼️ Image", "🎨 Image Variation", "🎵 Audio (TTS)", "🎬 Video"],
            index=0,
            help="Select what to generate from your prompts"
        )
        
        # Initialize defaults
        image_upload = None
        document_upload = None
        model = "default"
        web_search = False
        streaming = True
        thinking = False
        image_generation = generation_mode == "🖼️ Image"
        image_variation = generation_mode == "🎨 Image Variation"
        audio_generation = generation_mode == "🎵 Audio (TTS)"
        video_generation = generation_mode == "🎬 Video"
        variation_source = None
        
        if generation_mode == "💬 Chat":
            # Image upload for vision models
            image_upload = st.file_uploader(
                "Upload Image",
                type=["jpg", "jpeg", "png"],
                help="Upload images to analyze or discuss"
            )
            
            # Document upload for analysis
            all_doc_types = DOCUMENT_EXTENSIONS + DOCUMENT_EXTENSIONS_EXTRA
            document_upload = st.file_uploader(
                "📄 Upload Document",
                type=all_doc_types,
                help="Upload documents (TXT, PDF, DOCX, CSV, etc.) to analyze in chat"
            )
            
            # Model selection with grouped categories
            grouped_models = get_grouped_text_models()
            
            if image_upload is not None:
                model = "default"
                st.info("Using vision model for image input")
            else:
                if not grouped_models:
                    st.warning("No models available.")
                    model = "default"
                else:
                    # Build flat list with group headers for selectbox
                    all_model_names = []
                    model_group_map = {}
                    for group in grouped_models:
                        for m in group["models"]:
                            all_model_names.append(m)
                            model_group_map[m] = group["group"]
                    
                    if not all_model_names:
                        all_model_names = ["default"]
                    
                    model = st.selectbox(
                        "Select Model",
                        all_model_names,
                        format_func=lambda x: f"{x} — {model_group_map.get(x, '')}" if x != "default" else "Default",
                        help="Choose AI model for responses (grouped by provider)"
                    )
            
            # Feature toggles
            web_search = st.checkbox("Web Search", value=False, help="Search the web using DuckDuckGo")
            streaming = st.checkbox("Streaming", value=True, help="Show response as it's generated")
            thinking = st.checkbox("Reasoning", value=False, help="Show reasoning process for DeepSeek-R1 models")
            
            conversation_history = st.checkbox(
                "Conversation History",
                value=st.session_state.conversation_history,
                help="Remember previous messages"
            )
            st.session_state.conversation_history = conversation_history
            
            # JSON mode toggle
            json_mode = st.checkbox(
                "🔧 JSON Mode",
                value=st.session_state.get("json_mode", False),
                help="Force structured JSON output from the model"
            )
            st.session_state.json_mode = json_mode
            
            # Advanced settings expander
            with st.expander("⚙️ Advanced Settings", expanded=False):
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=0,
                    max_value=128000,
                    value=st.session_state.get("max_tokens", 0),
                    step=256,
                    help="Maximum response length (0 = unlimited)"
                )
                st.session_state.max_tokens = max_tokens
                
                stop_sequences = st.text_input(
                    "Stop Sequences",
                    value=st.session_state.get("stop_sequences", ""),
                    help="Comma-separated stop sequences (e.g. 'END,STOP')"
                )
                st.session_state.stop_sequences = stop_sequences
                
                st.divider()
                st.markdown("**🔌 Custom Provider**")
                custom_url = st.text_input(
                    "API Base URL",
                    value=st.session_state.get("custom_provider_url", ""),
                    placeholder="https://api.example.com/v1",
                    help="Connect to Ollama, LM Studio, or any OpenAI-compatible API"
                )
                st.session_state.custom_provider_url = custom_url
                
                custom_key = st.text_input(
                    "API Key",
                    value=st.session_state.get("custom_provider_key", ""),
                    type="password",
                    help="API key for authentication (optional)"
                )
                st.session_state.custom_provider_key = custom_key
                
                if custom_url:
                    st.success(f"✅ Using custom provider")

        elif image_generation:
            if IMAGE_MODELS:
                current_index = IMAGE_MODELS.index(st.session_state.image_model) if st.session_state.image_model in IMAGE_MODELS else 0
                image_model = st.selectbox(
                    "Image Model",
                    IMAGE_MODELS,
                    index=current_index,
                    help="Select image generation model"
                )
                st.session_state.image_model = image_model
                
                improve_prompt = st.checkbox(
                    "Improve Prompts",
                    value=st.session_state.improve_prompt,
                    help="Enhance prompts and translate to English"
                )
                st.session_state.improve_prompt = improve_prompt
            else:
                st.warning("No image models available.")
        
        elif image_variation:
            if IMAGE_MODELS:
                current_index = IMAGE_MODELS.index(st.session_state.image_model) if st.session_state.image_model in IMAGE_MODELS else 0
                image_model = st.selectbox(
                    "Image Model",
                    IMAGE_MODELS,
                    index=current_index,
                    help="Select model for image variation"
                )
                st.session_state.image_model = image_model
                
                variation_source = st.file_uploader(
                    "Upload Source Image",
                    type=["jpg", "jpeg", "png", "webp"],
                    help="Upload an image to create variations of"
                )
            else:
                st.warning("No image models available.")
        
        elif audio_generation:
            if VOICE_OPTIONS:
                audio_voice = st.selectbox(
                    "Voice",
                    VOICE_OPTIONS,
                    index=VOICE_OPTIONS.index(st.session_state.audio_voice) if st.session_state.audio_voice in VOICE_OPTIONS else 0,
                    help="Select TTS voice"
                )
                st.session_state.audio_voice = audio_voice
            else:
                st.warning("No voice options available.")
        
        elif video_generation:
            if VIDEO_MODELS:
                current_video_index = VIDEO_MODELS.index(st.session_state.video_model) if st.session_state.video_model in VIDEO_MODELS else 0
                video_model = st.selectbox(
                    "Video Model",
                    VIDEO_MODELS,
                    index=current_video_index,
                    help="Select video generation model"
                )
                st.session_state.video_model = video_model
            else:
                st.warning("No video models available.")
        
        st.divider()
        
        # Save generated files option (Global)
        save_files = st.checkbox(
            "💾 Save Generated Files",
            value=st.session_state.save_generated_files,
            help="Save generated images, audio, and video to generated_media/ folder"
        )
        st.session_state.save_generated_files = save_files
        
        # Token usage summary
        total_p = st.session_state.get("total_prompt_tokens", 0)
        total_c = st.session_state.get("total_completion_tokens", 0)
        if total_p > 0 or total_c > 0:
            st.caption(f"📊 Session tokens: {total_p}→{total_c} (Σ {total_p + total_c})")
        
        st.divider()
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear", use_container_width=True, help="Clear chat history"):
                st.session_state.messages = []
                st.session_state.total_prompt_tokens = 0
                st.session_state.total_completion_tokens = 0
                st.rerun()
        
        with col2:
            if st.session_state.messages:
                chat_export = export_chat_data()
                st.download_button(
                    "📥 Export",
                    data=chat_export,
                    file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    help="Export chat history with images"
                )
            else:
                st.button("📥 Export", disabled=True, use_container_width=True)
        
        # Regenerate button
        if (st.session_state.messages and 
            len(st.session_state.messages) >= 2 and 
            st.session_state.messages[-1]["role"] == "assistant"):
            if st.button("🔄 Regenerate", use_container_width=True, help="Regenerate last response"):
                st.session_state.regenerate = True
                st.rerun()
        
        # Footer
        st.markdown("""
        <div class="footer">
            <a href="https://github.com/kqlio67/g4flow" target="_blank" rel="noopener noreferrer">G4Flow</a><br/>
            Built with <a href="https://github.com/xtekky/gpt4free" target="_blank" rel="noopener noreferrer">G4F framework</a> | Streamlit
        </div>
        """, unsafe_allow_html=True)
        
        return model, web_search, streaming, thinking, image_generation, image_variation, audio_generation, video_generation, image_upload, document_upload, variation_source


def display_chat_history():
    """Display all messages from chat history"""
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if "thinking" in msg and st.session_state.get("thinking", False):
                with st.expander(f"Thought for {msg.get('thinking_duration', 0):.2f}s", expanded=False):
                    st.markdown(msg["thinking"])
            
            st.markdown(msg["content"])
            
            if "image_base64" in msg:
                try:
                    image_bytes = base64.b64decode(msg["image_base64"])
                    st.image(image_bytes)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
            
            if "audio_bytes" in msg:
                try:
                    audio_bytes = base64.b64decode(msg["audio_bytes"])
                    st.audio(audio_bytes, format="audio/mp3")
                except Exception as e:
                    st.error(f"Error displaying audio: {str(e)}")
            
            if "video_url" in msg:
                try:
                    st.video(msg["video_url"])
                except Exception as e:
                    st.error(f"Error displaying video: {str(e)}")
            
            # Display saved token usage
            if "token_usage" in msg and msg["role"] == "assistant":
                tu = msg["token_usage"]
                st.caption(f"📊 {tu.get('prompt', 0)}→{tu.get('completion', 0)} | Σ {tu.get('total', 0)}")


# ============== Main ==============
def main():
    initialize_session_state()
    apply_custom_styling()
    
    render_header()
    
    result = render_sidebar()
    model, web_search, streaming, thinking = result[0], result[1], result[2], result[3]
    image_generation, image_variation = result[4], result[5]
    audio_generation, video_generation = result[6], result[7]
    image_upload, document_upload, variation_source = result[8], result[9], result[10]
    
    render_quick_prompts()
    
    display_chat_history()
    
    # Handle regenerate
    if st.session_state.get("regenerate", False):
        st.session_state.regenerate = False
        asyncio.run(handle_regenerate(model, web_search, streaming, thinking, image_generation))
        st.rerun()
    
    # Handle image variation (no text prompt needed)
    if image_variation and variation_source is not None:
        if st.button("🎨 Generate Variation", use_container_width=True):
            asyncio.run(handle_image_variation(variation_source))
            st.rerun()
    
    # Chat input
    default_value = st.session_state.quick_prompt_prefix
    st.session_state.quick_prompt_prefix = ""
    
    prompt = st.chat_input("Ask me anything...", key="chat_input")
    
    if default_value and prompt:
        prompt = default_value + prompt
    elif default_value and not prompt:
        st.info(f'💡 Type your text after: "{default_value}"')
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        if image_generation:
            asyncio.run(handle_image_generation(prompt))
        elif audio_generation:
            asyncio.run(handle_audio_generation(prompt, st.session_state.audio_voice))
        elif video_generation:
            asyncio.run(handle_video_generation(prompt))
        else:
            # Read document if uploaded
            doc_text = None
            if document_upload is not None:
                with st.spinner("Reading document..."):
                    doc_text = read_uploaded_document(document_upload)
                    if doc_text:
                        st.toast(f"📄 Document loaded: {len(doc_text)} chars", icon="📄")
            
            asyncio.run(handle_chat(prompt, model, web_search, image_upload, streaming, thinking, doc_text))
        
        st.rerun()


if __name__ == "__main__":
    main()
