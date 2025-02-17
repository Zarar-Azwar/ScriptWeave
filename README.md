# ScriptWeave

## Overview
This project is a FastAPI-based application that generates YouTube video scripts from any blog. It utilizes Google's Generative AI (Gemini-Pro) via LangChain to summarize blog content and generate scripts based on specified speakers and duration.

## Features
- Extracts and summarizes blog content from given URLs
- Generates video scripts with multiple speakers and different styles
- Uses LangChain's `ConversationChain` for intelligent text generation
- Supports dynamic script generation based on blog content
- Implements FastAPI for quick and efficient API handling

## Technologies Used
- **FastAPI**: Web framework for building APIs
- **LangChain**: AI model orchestration
- **Google Generative AI (Gemini-Pro)**: LLM model for text generation
- **Jinja2**: Template engine for rendering HTML responses
- **Pydantic**: Data validation and serialization
- **Dotenv**: Environment variable management

## Installation
### Prerequisites
- Python 3.8+
- Google API credentials for Generative AI

### Steps
1. Clone the repository:
   ```sh
   git clone https://github.com/Zarar-Azwar/ScriptWeave.git
   cd ScriptWeave
   ```
2. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Set up environment variables in a `.env` file:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```sh
   uvicorn main:app --reload
   ```

## API Endpoints
### Home Page
**GET /**
- Returns the HTML interface for the application

### Generate Scripts
**POST /generate**
- **Request Body:**
  ```json
  {
    "urls": ["https://example.com/blog"],
    "speakers": [
      {
        "name": "Speaker 1",
        "role": "Narrator",
        "background": "Expert in technology",
        "style": "Informative"
      }
    ],
    "duration_minutes": 5
  }
  ```
- **Response:**
  ```json
  [
    {
      "title": "Blog Title",
      "url": "https://example.com/blog",
      "content": "Generated script content here",
      "error": null
    }
  ]
  ```

## Directory Structure
```
project-directory/
|-- main.py
|-- utils/
|   |-- utility.py
|-- static/
|-- templates/
|-- .env
|-- requirements.txt
|-- README.md
```

## Future Enhancements
- Support for multiple blog sources in a single request
- Improved error handling and retry mechanisms
- Integration with a frontend UI for better user experience


