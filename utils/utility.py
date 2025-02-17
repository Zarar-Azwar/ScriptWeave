from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from datetime import datetime
import time
import csv
def initialize_llm():
    """Initialize the language model with error handling"""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        test_prompt = "Hello, this is a test."
        make_api_call(llm, test_prompt)
        return llm
    except Exception as e:
        print(f"\nError initializing the language model: {str(e)}")
        return None
def make_api_call(llm, prompt):
    """Make API call with exponential backoff retry logic"""
    try:
        response = llm.invoke(prompt)
        return response
    except Exception as e:
        if "quota" in str(e).lower() or "429" in str(e):
            print("\nAPI quota exceeded. Please try one of the following:")
            print("1. Check your Google API quota in the Google Cloud Console")
            print("2. Wait a few minutes before trying again")
            print("3. Use a different API key")
            raise Exception("API quota exceeded") from e
        raise
def load_blog_content(url):
    """Load and process blog content using LangChain's WebBaseLoader"""
    try:
        loader = WebBaseLoader(url)
        docs = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=2000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)

        return {
            'title': splits[0].metadata.get('title', 'Untitled'),
            'content': '\n'.join([doc.page_content for doc in splits])
        }
    except Exception as e:
        print(f"Error loading content from {url}: {str(e)}")
        return None

def summarize_content(llm, content, chunk_size=1000):
    """Summarize content in chunks"""
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=100
        )

        # Split the text into chunks
        chunks = text_splitter.split_text(content)

        # Create documents in the correct format for LangChain
        from langchain.schema import Document
        texts = [Document(page_content=chunk, metadata={}) for chunk in chunks]

        # Process summary in chunks with rate limiting
        summaries = []
        for i, text_chunk in enumerate(texts):
            try:
                print(f"\nProcessing chunk {i+1}/{len(texts)}...")
                summary_chain = load_summarize_chain(
                    llm,
                    chain_type="stuff",
                    verbose=False
                )
                chunk_summary = summary_chain.invoke([text_chunk])
                if isinstance(chunk_summary, dict):
                    chunk_summary = chunk_summary.get('output_text', '')
                summaries.append(chunk_summary)
                time.sleep(1)
            except Exception as e:
                print(f"Error processing chunk {i+1}: {str(e)}")
                continue

        if not summaries:
            raise Exception("Failed to generate any summary")

        return " ".join(summaries)
    except Exception as e:
        print(f"Error in summarization: {str(e)}")
        return None

def generate_script_from_blog(llm, blog_data, speakers,duration_minutes):
    """Generate a multi-speaker script from blog content with error handling"""
    try:
        # Generate summary
        summary = summarize_content(llm, blog_data['content'])
        if not summary:
            raise Exception("Failed to generate summary")

        # Create detailed speaker profiles
        speaker_profiles = "\n".join([
            f"{s['name']} ({s['role']}):\n"
            f"- Background: {s['background']}\n"
            f"- Style: {s['style']}"
            for s in speakers
        ])

        target_words = duration_minutes * 140  

        prompt = f"""
        Create a YouTube video script for {len(speakers)} speakers based on this blog post:
        Title: {blog_data['title']}

        Target Duration: {duration_minutes} minutes
        Target Word Count: approximately {target_words} words

        Speaker Profiles:
        {speaker_profiles}

        Blog Content Summary:
        {summary}

        Please create an engaging multi-speaker script that:
        1. Fits within the {duration_minutes}-minute target duration (approximately {target_words} words)
        2. Starts with the Main Host introducing the topic and other speakers
        3. Distributes content based on each speaker's expertise and role
        4. Matches each speaker's designated presentation style
        5. Creates natural dialogue and interactions between speakers
        6. Uses speakers' backgrounds to add relevant insights and examples
        7. Maintains clear speaker labels for each line
        8. Ends with contributions from all speakers and a collaborative conclusion
        9. Includes appropriate pacing and transitions between segments
        10. Balances speaking time among participants

        Format each line as: [Speaker Name]: Dialog
        Include timestamps in [MM:SS] format before major segments
        """


        response = make_api_call(llm, prompt)
        # Extract the string content from the response
        return response.content if hasattr(response, 'content') else str(response)

    except Exception as e:
        print(f"\nError generating script: {str(e)}")
        return None

def process_blog(llm, url, speakers):
    """Process a single blog URL"""
    print(f"\nProcessing: {url}")
    blog_data = load_blog_content(url)

    if not blog_data:
        return None

    script = generate_script_from_blog(llm, blog_data, speakers)
    if not script:
        return None

    print(f"\nGenerated Script for '{blog_data['title']}':\n")
    print(script)

    script_data = {
        'title': blog_data['title'],
        'url': url,
        'speakers': speakers,
        'content': script
    }

    while True:
        user_input = input("\nWould you like to: (1) Add more content (2) Generate conclusion (3) Move to next blog (4) Exit? ")

        if user_input in ['3', '4']:
            return script_data, user_input == '4'

        if user_input == '1':
            next_part_prompt = """
            Continue the multi-speaker script, maintaining:
            - Speaker roles and expertise
            - Individual presentation styles
            - Natural interactions and dialogue
            - Balanced participation
            """
            next_part = make_api_call(llm, next_part_prompt)
            next_part_content = next_part.content if hasattr(next_part, 'content') else str(next_part)
            print("\nAdditional Content:\n")
            print(next_part_content)
            script_data['content'] += '\n\n' + next_part_content

        elif user_input == '2':
            conclusion_prompt = """
            Generate a collaborative conclusion where:
            - Each speaker contributes based on their expertise
            - The Main Host summarizes key points
            - All speakers participate in the call-to-action
            - Maintain individual speaking styles
            """
            conclusion = make_api_call(llm, conclusion_prompt)
            conclusion_content = conclusion.content if hasattr(conclusion, 'content') else str(conclusion)
            print("\nConclusion:\n")
            print(conclusion_content)
            script_data['content'] += '\n\n' + conclusion_content



def save_to_csv(scripts):
    """Save generated scripts to a CSV file with detailed speaker information"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"youtube_scripts_{timestamp}.csv"

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([
                'Blog Title',
                'URL',
                'Number of Speakers',
                'Speaker Details',
                'Script Content'
            ])

            for script in scripts:
                speaker_details = '; '.join([
                    f"{s['name']} ({s['role']}, {s['background']}, {s['style']})"
                    for s in script['speakers']
                ])
                writer.writerow([
                    script['title'],
                    script['url'],
                    len(script['speakers']),
                    speaker_details,
                    script['content']
                ])
        print(f"\nScripts saved successfully to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {str(e)}")