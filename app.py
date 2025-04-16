import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import time
from google.api_core.exceptions import DeadlineExceeded, InternalServerError

# Set Streamlit page configuration first
st.set_page_config(page_title="YouTube to Notes", layout="centered")

# Load environment variables
load_dotenv()

# Configure Gemini API with the API Key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# List available models and print them (to check supported models)
models = genai.list_models()
st.write("Available Models:", models)  # Display available models for debugging

# Define the prompt to be used with Gemini
prompt = """
You are a YouTube video summarizer. You will be given a transcript and should summarize it in clear bullet points, staying under 250 words. Here's the transcript:
"""

# Function to extract transcript from YouTube
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("v=")[1]
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])
        transcript = " ".join([i["text"] for i in transcript_list])
        return transcript
    except Exception as e:
        st.error(f"❌ Error extracting transcript: {str(e)}")
        return None

# Function to generate content using Gemini with retry mechanism
def generate_gemini_content(transcript_text, prompt):
    # List available models
    models = genai.list_models()
    st.write("Available Models:", models)  # Display available models for debugging
    
    # Use a correct model based on the listed models
    model = genai.GenerativeModel("your-correct-model-name")  # Replace with a valid model name
    
    retries = 3
    delay = 5  # Initial delay between retries (in seconds)
    
    while retries > 0:
        try:
            response = model.generate_content(prompt + transcript_text)
            return response.text
        except (DeadlineExceeded, InternalServerError) as e:
            st.warning(f"❌ API Timeout/Error: {str(e)}. Retrying in {delay} seconds...")
            time.sleep(delay)
            retries -= 1
            delay *= 2  # Exponential backoff
        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            break  # Exit loop if any other error occurs
    
    st.error("❌ Failed to generate summary after multiple attempts.")
    return None

# Streamlit UI
st.title("🎬 YouTube Transcript to Notes")

# Input field for the YouTube video link
youtube_link = st.text_input("🔗 Enter YouTube video link:")

# Display thumbnail of YouTube video
if youtube_link:
    try:
        video_id = youtube_link.split("v=")[1]
        st.image(f"https://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except:
        st.warning("⚠️ Could not extract video thumbnail.")

# Button to generate notes
if st.button("📝 Generate Summary"):
    if not youtube_link:
        st.warning("Please enter a YouTube link first.")
    else:
        with st.spinner("Fetching transcript and summarizing..."):
            # Extract transcript details
            transcript_text = extract_transcript_details(youtube_link)
            if transcript_text:
                # Generate summary using Gemini
                summary = generate_gemini_content(transcript_text, prompt)
                if summary:
                    st.markdown("## 🧾 Summary:")
                    st.write(summary)
