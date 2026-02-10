import os
import uuid
from typing import Dict
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Tools to talk to YouTube and process text
from langchain_community.document_loaders import YoutubeLoader
from langchain_community.document_loaders.youtube import TranscriptFormat
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# 1. SETUP
load_dotenv()

app = FastAPI(title="VidWhisper | Video Intelligence API")

# Simple dictionary to store the AI chain for the current session
memory_storage: Dict[str, any] = {}

# 2. DATA MODELS
class VideoLink(BaseModel):
    url: str

class UserQuestion(BaseModel):
    question: str

# 3. HELPER FUNCTIONS

def parse_time_to_seconds(raw_stamp):
    """Safely converts HH:MM:SS, MM:SS or raw numeric timestamps."""
    if isinstance(raw_stamp, (int, float)):
        return int(raw_stamp)
    
    if isinstance(raw_stamp, str) and ":" in raw_stamp:
        parts = raw_stamp.split(':')
        try:
            if len(parts) == 3: # HH:MM:SS
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
            elif len(parts) == 2: # MM:SS
                return int(parts[0]) * 60 + int(parts[1])
        except ValueError:
            return 0
    
    try:
        return int(float(raw_stamp))
    except (ValueError, TypeError):
        return 0

def format_timestamp(total_seconds: int) -> str:
    """
    Dynamically formats time. 
    Returns [H:MM:SS] if 1 hour or longer, otherwise [M:SS].
    """
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"[{hours}:{minutes:02d}:{seconds:02d}]"
    else:
        return f"[{minutes}:{seconds:02d}]"

def get_video_transcript(url: str):
    """Downloads the text of the video in chunks."""
    try:
        loader = YoutubeLoader.from_youtube_url(
            url,
            add_video_info=False, 
            transcript_format=TranscriptFormat.CHUNKS,
            chunk_size_seconds=30,
            language=["en", "hi"]
        )
        transcript_data = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
        return text_splitter.split_documents(transcript_data)
    except Exception as e:
        print(f"Error loading transcript: {e}")
        return None

def attach_timestamps_to_text(chunks):
    """Formats retrieved chunks with dynamic [H:MM:SS] or [M:SS] markers."""
    clean_context = []
    for item in chunks:
        raw_start = item.metadata.get('start_timestamp', 0)
        total_seconds = parse_time_to_seconds(raw_start)
        
        # Use our new dynamic formatter
        timestamp = format_timestamp(total_seconds)
        
        clean_context.append(f"At {timestamp} the video says: {item.page_content}")
    return "\n\n".join(clean_context)

def build_ai_logic(text_chunks):
    """Creates the RAG (Retrieval Augmented Generation) chain."""
    embeddings_tool = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    search_db = Chroma.from_documents(
        documents=text_chunks,
        embedding=embeddings_tool,
        collection_name=f"session_{uuid.uuid4().hex[:6]}"
    )
    
    ai_model = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)
    
    # SYSTEM INSTRUCTIONS UPDATED: Added instruction for H:MM:SS vs M:SS
    instructions = """
    You are a professional assistant for a YouTube Question-Answering system.
    
    RULES:
    1. Answer the question STRICTLY using only the provided CONTEXT FROM VIDEO.
    2. Your answer must be concise and professional.
    3. Include relevant timestamps at the end of sentences exactly as they appear in context.
       (Note: Some are [M:SS] and long videos are [H:MM:SS]).
    4. If the context does not contain the answer, you MUST strictly say: 
       "This content is not provided in this video."
    5. Do not use outside knowledge.

    CONTEXT FROM VIDEO:
    {context}
    
    USER QUESTION: {question}
    
    YOUR ANSWER:
    """
    prompt_style = PromptTemplate.from_template(instructions)
    
    return (
        {"context": search_db.as_retriever() | attach_timestamps_to_text, "question": RunnablePassthrough()}
        | prompt_style
        | ai_model
    )

# 4. API ROUTES

@app.post("/load_video")
def start_processing(video: VideoLink):
    chunks = get_video_transcript(video.url)
    if not chunks:
        raise HTTPException(status_code=500, detail="Could not retrieve video transcript.")
    
    memory_storage["active_session"] = build_ai_logic(chunks)
    return {"message": "Video processed successfully!"}

@app.post("/ask")
def chat_with_ai(user_data: UserQuestion):
    ai_brain = memory_storage.get("active_session")
    if not ai_brain:
        raise HTTPException(status_code=404, detail="Please load a video first!")
    
    try:
        result = ai_brain.invoke(user_data.question)
        return {"answer": result.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)