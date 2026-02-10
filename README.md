# 🎥 **YouTube Video Question Answering System**

**Data Science / NLP Project**

---

## 📌 **Project Overview**
This project is a **YouTube Video Question Answering (QA) System** that allows users to ask questions about video content and receive accurate, context-aware answers. The system uses **Retrieval-Augmented Generation (RAG)** with **LangChain**, **HuggingFace embeddings**, **Chroma vector database**, and **Groq LLM**.

The goal is to extract meaningful information from video transcripts in a **multilingual setup** (**English, Hindi, Telugu, Tamil**) and provide precise answers.

---

## ❓ **Problem Statement**
Build a system that can:
- Understand the content of YouTube videos from transcripts
- Answer questions accurately using the transcript context
- Handle multiple languages based on user queries
- Avoid hallucination by strictly following the video content

---

## 📊 **Dataset / Input**
- **Source**: YouTube video transcripts
- **Format**: Text / JSON (transcripts loaded via LangChain YouTubeLoader)
- **Languages Supported**: English, Hindi, Telugu, Tamil

---

## 🧰 **Technologies Used**
- Python 3.10+
- LangChain
- HuggingFace Transformers
- Chroma Vector Database
- Groq LLM
- python-dotenv
- uuid

---

## 🔄 **Project Workflow**
1. **Load YouTube Transcript** – Extract video transcript using YouTubeLoader
2. **Split Documents** – Divide transcript into chunks for efficient semantic search
3. **Generate Embeddings** – Use HuggingFace sentence transformers to create embeddings
4. **Store in Vector DB** – Save embeddings in Chroma database
5. **Build RAG Chain** – Groq LLM retrieves relevant chunks and generates answers
6. **Answer Questions** – User queries answered based on transcript context

---

## 🤖 **Key Features**
- **Multilingual QA**: English, Hindi, Telugu, Tamil
- **Context-aware answers** (no hallucinations)
- **Retrieval-Augmented Generation (RAG)** architecture
- **Easily extendable** for other video sources or languages

---

## 🚀 **How to Run the Project**

1. **Clone the repository**
   git clone https://github.com/athiyataj9-archyoutube-qa-system.git  
   cd youtube-qa-system  

2. **Create a virtual environment**  
   python -m venv venv  

3. **Activate the virtual environment**

   Windows (PowerShell):  
   venv\Scripts\activate  

   Windows (CMD):  
   venv\Scripts\activate.bat  

   Mac / Linux:  
   source venv/bin/activate  

4. **Install dependencies**  
   pip install -r requirements.txt  

5. **Create a `.env` file and add your API key**  
   GROQ_API_KEY=your_groq_api_key_here  

   ⚠️ Do not commit the `.env` file to GitHub  

6. **Start the FastAPI server**  
   uvicorn main:app --reload  

7. **Open API documentation**  
   http://127.0.0.1:8000/docs

### 🔗Example Usage

Load Video:

POST /load_video
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}

Ask Question with Timestamp:

POST /ask
{
  "question": "What is discussed at 2:30?"
}

Response:

{
  "answer": "Explanation from video...",
  "watch_at": "https://www.youtube.com/watch?v=VIDEO_ID&t=150s"
}

## 🔮 **Future Enhancements**

- Add Streamlit frontend for a user-friendly interface
- Support multi-video question answering
- Deploy on Render / Railway / AWS
- Add highlighted transcript segments in answers
- Add advanced summarization for long videos

## 📜 **License**

🧑‍🎓 This project is intended **strictly for educational and learning purposes**.  
You are free to explore, modify, and experiment with the code to understand the concepts.

⚠️ **Important Note**  
Before running the project, make sure to:
- Create a `.env` file in the project root  
- Add your **GROQ_API_KEY** inside the file  

🚫 **Do not commit** the `.env` file to GitHub.  
Use `.env.example` for reference.
