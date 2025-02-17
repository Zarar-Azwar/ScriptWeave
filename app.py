from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import time
import csv
import backoff
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from utils.utility import *

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Constants
MAX_RETRIES = 3
BASE_DELAY = 5
MAX_SPEAKERS = 4

# Models
class Speaker(BaseModel):
    name: str
    role: str
    background: str
    style: str

class BlogRequest(BaseModel):
    urls: List[str]
    speakers: List[Speaker]
    duration_minutes: int

class GenerationResponse(BaseModel):
    title: str
    url: str
    content: str
    error: Optional[str] = None

# Create necessary directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)




@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate")
async def generate_scripts(request: BlogRequest):
    try:
        # Initialize LLM
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        
        # Initialize conversation chain
        conversation = ConversationChain(
            llm=llm,
            memory=ConversationBufferMemory(),
            verbose=True
        )

        results = []
        
        for url in request.urls:
            try:
                # Load blog content
                blog_data = load_blog_content(url)
                if not blog_data:
                    results.append(GenerationResponse(
                        title="Error",
                        url=url,
                        content="",
                        error="Failed to load blog content"
                    ))
                    continue

                # Generate script
                script = generate_script_from_blog(llm, blog_data, [s.dict() for s in request.speakers],request.duration_minutes)
                
                results.append(GenerationResponse(
                    title=blog_data['title'],
                    url=url,
                    content=script
                ))
                
            except Exception as e:
                results.append(GenerationResponse(
                    title="Error",
                    url=url,
                    content="",
                    error=str(e)
                ))

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))