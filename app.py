import streamlit as st
import asyncio
import io
import re
import time
import html
import base64
from PIL import Image
from g4f.client import AsyncClient
import g4f.models
from g4f.models import Model, ImageModel, AudioModel, VisionModel, ModelUtils

# Constants
# Models to hide from the Select Model dropdown
HIDDEN_MODELS = ["o1-mini", "GigaChat:latest", "meta-ai", "llama-2-7b", "llama-3-8b", "llama-3-70b", "llama-3", "llama-3.2-1b", "llama-3.2-11b", "mixtral-8x7b","phi-3.5-mini", "gemini-2.0", "gemini-exp", "gemini-2.0-flash-thinking", "gemini-2.0-pro", "claude-3-sonnet", "claude-3-opus", "claude-3.5-sonnet", "claude-3.7-sonnet-thinking", "reka-core", "qwen-1.5-7b", "qwen-2-vl-7b", "qwen-2.5-72b", "qwq-32b", "pi", "grok-3", "grok-3-r1", "MiniMax", "sonar", "sonar-pro", "sonar-reasoning", "sonar-reasoning-pro", "r1-1776"]

# Get image models dynamically from g4f.models, excluding hidden models
IMAGE_MODELS = [model.name for model in ModelUtils.convert.values() if isinstance(model, ImageModel) and model.name not in HIDDEN_MODELS]
SYSTEM_MESSAGES = {
    "Default": "You are a helpful assistant.",
    "Creative": "You are a creative assistant with a vivid imagination. Think outside the box and provide innovative solutions.",
    "Academic": "You are an academic assistant with expertise in research. Provide thorough, well-reasoned responses with academic precision.",
    "Programming": "You are a programming expert. Provide clean, efficient, and well-documented code with explanations.",
    "Friendly": "You are a friendly conversational assistant. Respond in a warm, casual tone like talking to a friend.",
    "Fitness": "You are a fitness and health assistant. Provide evidence-based advice on workouts, nutrition, wellness, and overall fitness goals. Focus on safe, balanced approaches to health improvement without promoting extreme diets or potentially harmful exercise routines.",
    "Custom": "custom"  # Special flag for custom message
}

# Apply custom styling
def apply_custom_styling():
    """Apply custom CSS styling to improve the app appearance"""
    st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem 1rem 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        margin-bottom: 1rem !important;
    }
    .stChatMessage [data-testid="stChatMessageContent"] {
        padding-bottom: 0 !important;
    }
    /* Improved overall styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Better chat input styling */
    .stChatInputContainer {
        padding-top: 1rem;
        padding-bottom: 1rem;
        background-color: rgba(240, 242, 246, 0.5);
        border-radius: 10px;
    }
    /* Add space at bottom of main panel for mobile experience */
    .main {
        padding-bottom: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize all session state variables if they don't exist"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_message" not in st.session_state:
        st.session_state.system_message = SYSTEM_MESSAGES["Default"]
    if "system_message_template" not in st.session_state:
        st.session_state.system_message_template = "Default"
    if "custom_system_message" not in st.session_state:
        st.session_state.custom_system_message = ""
    if "image_model" not in st.session_state:
        st.session_state.image_model = IMAGE_MODELS[0] if IMAGE_MODELS else ""
    if "improve_prompt" not in st.session_state:
        st.session_state.improve_prompt = True  # Default: enabled
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = True  # Default: enabled

# Utility functions
def get_text_and_vision_models():
    """Get text and vision models from g4f.models, excluding hidden models"""
    models = []
    
    # Add default model first
    models.append(g4f.models.default)
    
    # Iterate through all models in ModelUtils.convert
    for model_name, model in ModelUtils.convert.items():
        if model_name and model.best_provider:  # Only include models with a name and provider
            # Include text models and vision models, but exclude image and audio models
            if not isinstance(model, (ImageModel, AudioModel)):
                # Exclude models in the HIDDEN_MODELS list
                if model.name not in HIDDEN_MODELS:
                    models.append(model)
    
    # Sort models by name (except default which should be first)
    other_models = models[1:]
    other_models.sort(key=lambda x: x.name.lower())
    models = [models[0]] + other_models
    
    return models

def extract_thinking(text):
    """Extract thinking content and final response from text"""
    thinking_pattern = r'<think>(.*?)</think>'
    thinking_content = re.findall(thinking_pattern, text, re.DOTALL)
    
    # Remove thinking tags from the final response
    final_response = re.sub(thinking_pattern, '', text, flags=re.DOTALL)
    
    return thinking_content, final_response.strip()

def typing_indicator():
    """Display a custom typing indicator animation"""
    return st.markdown("""
    <div class="typing-indicator">
        <div class="typing-indicator-dot"></div>
        <div class="typing-indicator-dot"></div>
        <div class="typing-indicator-dot"></div>
    </div>
    <style>
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
    </style>
    """, unsafe_allow_html=True)

# Image generation functions
async def improve_prompt_with_claude(prompt):
    """Improve the image generation prompt using Claude"""
    client = AsyncClient()
    
    system_message = """You are an expert at creating high-quality image generation prompts. 
    Your task is to improve the given prompt to create better images. 
    If the prompt is not in English, translate it to English.
    Your response should ONLY contain the improved prompt text without any explanations or additional text.
    Focus on adding details that will make the image more vivid, clear, and visually appealing."""
    
    try:
        response = await client.chat.completions.create(
            model=g4f.models.claude_3_7_sonnet,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Original prompt: {prompt}\n\nImproved prompt (in English):"}
            ]
        )
        
        improved_prompt = response.choices[0].message.content.strip()
        return improved_prompt
    except Exception as e:
        st.warning(f"Could not improve prompt: {str(e)}. Using original prompt.")
        return prompt

async def generate_image(prompt, model_name):
    """Generate an image using G4F API"""
    client = AsyncClient()
    
    try:
        response = await client.images.generate(
            prompt=prompt,
            model=model_name,
            response_format="b64_json"  # Request base64 encoded image
        )
        
        if response.data and response.data[0].b64_json:
            # Return the base64 encoded image
            return response.data[0].b64_json
        else:
            return None
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Chat response generation
async def generate_response(messages, model, web_search, image, streaming, show_thinking):
    """Generate AI response with support for streaming, thinking, and image input"""
    client = AsyncClient()
            
    kwargs = {
        "model": model,
        "messages": messages,
        "web_search": web_search
    }
    if image is not None:
        kwargs["image"] = image

    thinking_duration = 0
    
    # Show typing indicator before receiving response
    indicator_placeholder = st.empty()
    
    # If streaming is enabled, we'll update this placeholder dynamically
    if streaming:
        with indicator_placeholder:
            typing_indicator()

    if streaming:
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
                # Clear typing indicator once we start receiving content
                indicator_placeholder.empty()
                
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                
                # Check for thinking tags in the current chunk
                if "<think>" in content:
                    in_thinking = True
                    thinking_start_time = time.time() if thinking_start_time == 0 else thinking_start_time
                    
                    if show_thinking and not expander:
                        expander = thinking_placeholder.expander("🤔 Is thinking...", expanded=True)
                
                if in_thinking:
                    thinking_content += content
                    
                    # Check if thinking ended in this chunk
                    if "</think>" in content:
                        in_thinking = False
                        thinking_duration = time.time() - thinking_start_time
                        
                        if show_thinking and expander:
                            # Extract just the thinking content
                            _, parts = thinking_content.split("<think>", 1)
                            thinking_text, _ = parts.split("</think>", 1)
                            
                            with expander:
                                st.markdown(thinking_text)
                            
                            # Update expander label
                            status = f"Thought for {thinking_duration:.2f}s"
                            expander.label = status
                        
                        # Reset thinking content
                        thinking_content = ""
                
                # Always extract clean content for display
                _, clean_text = extract_thinking(full_response)
                
                # Show animated cursor at the end
                cursor_styles = ["▌", "▐"]  # Alternating cursor styles
                cursor = cursor_styles[int(time.time() * 4) % len(cursor_styles)]  # Blinking effect
                
                # Update visible text
                message_placeholder.markdown(clean_text + cursor)
                
                await asyncio.sleep(0.02)  # Adjust for typing speed
        
        # Final update without cursor
        _, clean_text = extract_thinking(full_response)
        message_placeholder.markdown(clean_text)
        return full_response, thinking_duration
    else:
        # Show typing indicator for non-streaming responses
        with indicator_placeholder:
            typing_indicator()
            
        # For non-streaming response
        thinking_start_time = time.time()
        response = await client.chat.completions.create(**kwargs)
        
        # Clear typing indicator
        indicator_placeholder.empty()
        
        content = response.choices[0].message.content
        thinking_sections, cleaned_response = extract_thinking(content)
        
        # Calculate thinking duration if there are thinking sections
        if thinking_sections:
            thinking_duration = time.time() - thinking_start_time
            
            # Show thinking in expander with duration if display is enabled
            if show_thinking:
                status = f"Thought for {thinking_duration:.2f}s"
                with st.expander(status, expanded=False):
                    st.markdown(thinking_sections[-1])
        
        # Show the response
        st.markdown(cleaned_response)
        
        return content, thinking_duration  # Return full response and thinking duration

# UI Components
def render_header():
    """Render the app header"""
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: #4F8BF9;">G4Flow</h1>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with all settings"""
    with st.sidebar:
        # System message template selection with standard help
        selected_template = st.selectbox(
            "System Message",
            list(SYSTEM_MESSAGES.keys()),
            index=list(SYSTEM_MESSAGES.keys()).index(st.session_state.system_message_template),
            help="Define AI personality and behavior"
        )
        
        # Update template selection in session state
        st.session_state.system_message_template = selected_template
        
        # Show custom message input if "Custom" is selected
        if selected_template == "Custom":
            custom_message = st.text_area(
                "Custom message",
                value=st.session_state.custom_system_message if st.session_state.custom_system_message else "You are a helpful assistant that...",
                help="Write your own system instructions for the AI"
            )
            st.session_state.custom_system_message = custom_message
            st.session_state.system_message = custom_message
        else:
            # Use the selected template
            st.session_state.system_message = SYSTEM_MESSAGES[selected_template]
        
        # Image upload with standard help
        image_upload = st.file_uploader(
            "Upload Image",
            type=["jpg", "jpeg", "png"],
            help="Upload images to analyze or discuss with the AI"
        )
        
        # Get text and vision models
        models = get_text_and_vision_models()
        
        # Model selection with standard help
        if image_upload is not None:
            model = g4f.models.default_vision
            st.info("Using vision model for image input")
        else:
            if not models:
                st.warning("No models available.")
                # Fallback to default model
                model = g4f.models.default
            else:
                # Model selection
                model = st.selectbox(
                    "Select Model",
                    models,
                    format_func=lambda x: "Default" if x == g4f.models.default else x.name,
                    help="Choose which AI model to use for generating responses"
                )
        
        # Feature toggles
        web_search = st.checkbox(
            "Web Search",
            value=False,
            help="Search the web using DuckDuckGo"
        )
        streaming = st.checkbox(
            "Streaming",
            value=True,
            help="Show AI response as it's being generated"
        )
        thinking = st.checkbox(
            "Reasoning",
            value=False,
            help="Shows the step-by-step reasoning process for DeepSeek-R1 based models"
        )
        
        conversation_history = st.checkbox(
            "Conversation History",
            value=st.session_state.conversation_history,
            help="When enabled, the model remembers previous messages. When disabled, each message is treated as a new conversation while still maintaining system instructions."
        )
        st.session_state.conversation_history = conversation_history
        
        image_generation = st.checkbox(
            "Image Generation",
            value=False,
            help="When enabled, all prompts will generate images without requiring"
        )
        
        # Image model selection (only visible when image generation is enabled)
        if image_generation:
            if not IMAGE_MODELS:
                st.warning("No image models available.")
                image_model = ""
            else:
                # Find the index of the current model, or default to 0
                current_index = 0
                if st.session_state.image_model in IMAGE_MODELS:
                    current_index = IMAGE_MODELS.index(st.session_state.image_model)
                
                image_model = st.selectbox(
                    "Image Model",
                    IMAGE_MODELS,
                    index=current_index,
                    help="Select the model to use for image generation"
                )
            st.session_state.image_model = image_model
            
            # Add checkbox for prompt improvement
            improve_prompt = st.checkbox(
                "Improve Prompts",
                value=st.session_state.improve_prompt,
                help="Use to improve image prompts and translate non-English prompts to English"
            )
            st.session_state.improve_prompt = improve_prompt
        
        st.divider()
        
        # Clear chat button moved to bottom
        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Add CSS for the footer to position it at the bottom of the sidebar
        st.markdown("""
        <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 17.5rem;  /* Match sidebar width */
            text-align: center;
            padding: 10px;
            background-color: #f0f2f6;
            border-top: 1px solid #ddd;
            font-size: 0.8em;
            color: #666;
            z-index: 999;
        }
        </style>
        
        <div class="footer">
            G4Flow | Built with <a href="https://github.com/xtekky/gpt4free" target="_blank">G4F framework</a> | Streamlit | v1.0.0
        </div>
        """, unsafe_allow_html=True)
        
        return model, web_search, streaming, thinking, image_generation, image_upload

def display_chat_history():
    """Display all messages from the chat history"""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Display thinking in expander if available and display is enabled
            if "thinking" in message and st.session_state.get("thinking", False):
                thinking_label = f"Thought for {message.get('thinking_duration', 0):.2f}s"
                with st.expander(thinking_label, expanded=False):
                    st.markdown(message["thinking"])
            
            # Display the content
            st.markdown(message["content"])
            
            # If the message contains an image, display it
            if "image_base64" in message:
                try:
                    image_bytes = base64.b64decode(message["image_base64"])
                    st.image(image_bytes)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")

async def handle_image_generation(prompt):
    """Handle the image generation workflow"""
    image_prompt = prompt.strip()
    final_prompt = image_prompt
    improved_prompt_message = ""
    
    # Check if we have a valid image model
    if not st.session_state.image_model:
        with st.chat_message("assistant"):
            st.error("No image model available. Please check if image models are properly loaded.")
        
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "No image model available. Please check if image models are properly loaded.",
            "is_generated_image": False
        })
        return
    
    # Show spinner while processing
    with st.spinner("Processing image request..."):
        # Improve prompt if enabled
        if st.session_state.improve_prompt:
            with st.status("Improving prompt...", expanded=False) as status:
                final_prompt = await improve_prompt_with_claude(image_prompt)
                status.update(label="Prompt improved!", state="complete", expanded=False)
            
            # Add message about prompt improvement if the prompt was changed
            if final_prompt != image_prompt:
                improved_prompt_message = f"Improved prompt: \"{final_prompt}\"\n\n"
        
        # Generate image with the final prompt
        with st.status("Generating image...", expanded=False) as status:
            base64_image = await generate_image(final_prompt, st.session_state.image_model)
            status.update(label="Image generated!", state="complete", expanded=False)
        
        if base64_image:
            # Add image to chat
            try:
                image_bytes = base64.b64decode(base64_image)
                
                # Add message to chat with the image
                with st.chat_message("assistant"):
                    message_content = f'Generated image using {st.session_state.image_model}'
                    if improved_prompt_message:
                        message_content += f'\n\nOriginal prompt: "{image_prompt}"\n{improved_prompt_message}'
                    else:
                        message_content += f' for prompt: "{image_prompt}"'
                    
                    st.markdown(message_content)
                    st.image(image_bytes)
                
                # Store in history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": message_content,
                    "image_base64": base64_image,
                    "is_generated_image": True  # Flag for identifying generated images
                })
                
            except Exception as e:
                st.error(f"Error processing image: {str(e)}")
        else:
            with st.chat_message("assistant"):
                st.error("Failed to generate image. Please try again with a different prompt or model.")
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Failed to generate image. Please try again with a different prompt or model.",
                "is_generated_image": False
            })

async def handle_chat(prompt, model, web_search, image_upload, streaming, thinking):
    """Handle the chat workflow"""
    # Prepare image
    image = None
    if image_upload is not None:
        image = io.BytesIO(image_upload.read())

    # Prepare messages for API (system message + chat history if enabled)
    messages_for_api = []
    if st.session_state.system_message.strip():
        messages_for_api.append({"role": "system", "content": st.session_state.system_message})
    
    if st.session_state.conversation_history:
        # Include full conversation history
        messages_for_api.extend(
            [{"role": m["role"], "content": m["content"]} 
             for m in st.session_state.messages]
        )
    else:
        # Only include the current user message (last message)
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            messages_for_api.append({
                "role": "user", 
                "content": st.session_state.messages[-1]["content"]
            })

    # Generate and display assistant response
    with st.chat_message("assistant"):
        full_response, thinking_duration = await generate_response(
            messages_for_api,
            model,
            web_search,
            image,
            streaming,
            thinking
        )
    
    # Extract thinking and cleaned response
    thinking_sections, cleaned_response = extract_thinking(full_response)
    
    # Add assistant response to chat history with thinking if available
    response_data = {"role": "assistant", "content": cleaned_response}
    if thinking_sections:
        response_data["thinking"] = thinking_sections[-1]
        response_data["thinking_duration"] = thinking_duration
    
    st.session_state.messages.append(response_data)

# Main app function
def main():
    # Initialize session state
    initialize_session_state()
    
    # Apply custom styling
    apply_custom_styling()
    
    # Render header
    render_header()
    
    # Render sidebar and get settings
    model, web_search, streaming, thinking, image_generation, image_upload = render_sidebar()
    
    # Display chat history
    display_chat_history()
    
    # Chat interface
    prompt = st.chat_input("Ask me anything...")
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message in current session
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Handle image generation or chat based on mode
        if image_generation:
            asyncio.run(handle_image_generation(prompt))
        else:
            asyncio.run(handle_chat(prompt, model, web_search, image_upload, streaming, thinking))
        
        # Rerun to update UI
        st.rerun()

if __name__ == "__main__":
    main()
