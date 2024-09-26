# Install the necessary libraries
!pip install youtube-transcript-api
!pip install ipywidgets
!pip install openai==0.28.0

# Import the necessary libraries
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import re
import ipywidgets as widgets
from IPython.display import display, HTML
from getpass import getpass
from urllib.parse import urlparse, parse_qs
import textwrap  # Import textwrap for text wrapping
import json

# Set your OpenAI API key securely
openai.api_key = getpass("Enter your OpenAI API key: ")

# Function to extract video IDs, timestamps, and context from text
def extract_video_info(text):
    lines = text.strip().split('\n')
    results = []
    context = ""
    for line in lines:
        line = line.strip()
        if not line:
            continue  # Skip empty lines
        url_match = re.search(r'(https?://[^\s]+)', line)
        if url_match:
            url = url_match.group(1)
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            video_id = None
            timestamp = None
            if 'youtu.be' in parsed_url.netloc:
                video_id = parsed_url.path.lstrip('/')
                timestamp = query_params.get('t', [None])[0]
            elif 'youtube.com' in parsed_url.netloc:
                video_id = query_params.get('v', [None])[0]
                timestamp = query_params.get('t', [None])[0]
            if video_id:
                timestamp = int(timestamp) if timestamp else None
                context_text = context.strip()
                results.append((video_id, timestamp, context_text))
                context = ""
        else:
            context += line + " "
    return results

# Function to fetch and truncate the transcript around the timestamp
def fetch_truncated_transcript(video_id, timestamp, window=240):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        if timestamp is None:
            timestamp = transcript[0]['start']
        start_time = max(0, timestamp - window)
        end_time = timestamp + window
        truncated_entries = [
            entry for entry in transcript if (entry['start'] + entry['duration'] >= start_time) and (entry['start'] <= end_time)
        ]
        truncated_transcript = ''
        for entry in truncated_entries:
            time_stamp = round(entry['start'], 2)
            text = entry['text']
            truncated_transcript += f"Time: {time_stamp} - Text: {text}\n"
        return truncated_transcript, timestamp
    except Exception as e:
        return f"Failed to fetch the transcript: {str(e)}", None

# Function to use GPT model for generating insights from transcript in JSON format
def chatgpt_call(truncated_transcript, timestamp, context_timestamp):
    prompt = f"""
    Consult this transcript:
    "{truncated_transcript}"

    Task:
    - Locate and extract the passage at timestamp {timestamp}. Ensure to include surrounding context if relevant for clarity.

    Requirements:
    - Do not edit or modify the actual content of the passage.
    - Remove any "time: [X] - Text:" formatting and present the text as a coherent paragraph.
    - Make minor proofreading and transcription corrections for readability.

    Context:
    - The core idea of interest is around the timestamp {timestamp}, specifically relating to the idea of "{context_timestamp}".

    Goal:
    - Your goal is to extract the idea that was talked about at timestamp {timestamp}.
    - It should form a coherent argument or observation, so attempt to go as far back and as far forward as you need to in order to not cut the idea off, and the note extracted is intelligible on its own right.

    Output Specification:
    Format the response as a JSON object with these key-value pairs:
    - "Commentary": A string containing your model's comments on the output.
    - "Title": A short, descriptive and specific title for this piece of text about the idea captured.
    - "Text": A string of the exact transcript text with the additional context as needed and with minor proofreading for readability. No additional comments should be included.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Extract and format a passage from a transcript based on a specific timestamp. Output must be in JSON format, adhering to the prompt instructions."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        output = response.choices[0].message['content'].strip()
        cleaned_output = output.replace('```json', '').replace('```', '').strip()
        json_output = json.loads(cleaned_output)
        return json_output  # Fetching the entire JSON output including title, commentary, and text
    except json.JSONDecodeError as e:
        return f"JSON decoding error: {e}\nResponse received: '{output}'"
    except Exception as e:
        return f"An error occurred: {e}"

# Function to display all insights in one textarea with a copy button
def display_html_insight(all_insights):
    all_insights_text = "\n\n".join([f"**{insight['Title']}**\n{insight['Text']}" for insight in all_insights])  # Create formatted insights text
    html = f"""
    <textarea id='text_area_all' style="width:90%; height:200px;">{all_insights_text}</textarea><br>
    <button onclick="copyToClipboard()">Copy</button>
    <script>
    function copyToClipboard() {{
      var copyText = document.getElementById('text_area_all');
      copyText.select();  // Select the text field
      document.execCommand('copy');  // Copy the text inside the text field
    }}
    </script>
    """
    display(HTML(html))

# Function to process input after button click
def process_input(button):
    text_input = textarea.value.strip()
    video_info_list = extract_video_info(text_input)
    all_insights = []  # List to store all insights
    for idx, (video_id, timestamp, context_timestamp) in enumerate(video_info_list):
        truncated_transcript, used_timestamp = fetch_truncated_transcript(video_id, timestamp)
        if truncated_transcript:
            json_output = chatgpt_call(truncated_transcript, used_timestamp, context_timestamp)
            all_insights.append(json_output)  # Append each JSON output to the list
        else:
            print("No transcript text available to generate insights.")
    if all_insights:
        display_html_insight(all_insights)  # Display all insights in one textarea

# Create UI components
textarea = widgets.Textarea(
    value='',
    placeholder='Paste your text and YouTube links here. Each link should contain the video ID and timestamp.',
    description='Input:',
    disabled=False,
    layout={'width': '100%', 'height': '200px'}
)

button = widgets.Button(description="Continue")
button.on_click(process_input)

# Display UI components
display(textarea, button)
