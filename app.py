import streamlit as st
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

from dotenv import load_dotenv
load_dotenv() 

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

prompt="""As a YouTube video summarizer, your task is to analyze the provided transcript text.
Create a concise summary of the entire video content, 
highlighting key points and main ideas ensuring it remains within a 250-word limit.
Please summarize the following transcript:  """




    
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        
        # Try to get the transcript in multiple languages
        transcript = None
        languages = ['en', 'en-GB', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'tr', 'ja', 'ko', 'zh-cn']
        
        for lang in languages:
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                break
            except Exception:
                continue
        
        if transcript is None:
            # If no language-specific transcript is found, try getting all available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript(['en']).fetch()
        
        if transcript:
            return " ".join(item['text'] for item in transcript)
        else:
            raise Exception("No transcript found for any supported language.")

    except Exception as e:
        st.error(f"An error occurred while extracting the transcript: {str(e)}")
        return None

# ... rest of the code remains unchanged ...

## getting the summary based on Prompt from OpenAI GPT-3.5-turbo
def generate_content(transcript_text, prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube videos."},
                {"role": "user", "content": f"{prompt}\n\n{transcript_text}"}
            ],
            max_tokens=300,
            n=1,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while generating the summary: {str(e)}")
        return None
    


# st.title("Youtube Video Summarizer")
st.markdown("<h1 style='color: #FF4B4B;'>Youtube Video Summarizer</h1>", unsafe_allow_html=True)
st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1024px-YouTube_full-color_icon_%282017%29.svg.png", width=50)


st.markdown("""
This app allows you to generate detailed notes from YouTube videos. Simply paste a YouTube video link in the input box below, and click the 'Get Summary' button. The app will extract the video's transcript, process it using advanced AI, and provide you with a comprehensive summary.
""")
youtube_link = st.text_input("**Enter YouTube Video Link:**")


if youtube_link:
    video_id = youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Summary"):
    transcript_text=extract_transcript_details(youtube_link)

    if transcript_text:
        summary=generate_content(transcript_text,prompt)
        st.markdown("## Summary:")
        st.write(summary)