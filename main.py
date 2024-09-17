# YouTube Video Note-Taking POC

## Overview
This Python-based application serves as a proof of concept for a note-taking feature specifically designed for YouTube videos. It allows users to extract and format specific passages from YouTube video transcripts based on user-provided timestamps and descriptions. This tool is ideal for users looking to quickly gather notes from their favorite sections of videos without manually tracking down the information.

## Features
- **Extract Video IDs and Timestamps:** Parses user-inputted YouTube URLs to extract video IDs and timestamps.
- **Retrieve and Truncate Transcripts:** Utilizes the YouTube Transcript API to fetch full video transcripts and truncate them around the specified timestamps.
- **Generate Formatted Passages:** Sends the relevant transcript sections to an AI model (GPT-4) to extract and neatly format passages.
- **User-Friendly Output:** Provides the extracted passages in a clear and readable format, ready for note-taking or content review.

## Usage Instructions
1. **Prepare Input Data:**
   - Input should be provided in the format: `idea description: timestamp URL`.
   - To get a timestamp URL, right-click on the desired time point in a YouTube video and select "Copy URL at current time."

2. **Running the Application:**
   - This project is designed to run in Google Colab, providing a user-friendly interface and seamless environment setup.
   - Open the notebook in Google Colab, follow the on-screen prompts to paste the formatted input into the provided text area, and press the "Continue" button to process the input and retrieve the formatted notes.

## Current Limitations
- This is an early version and the user experience is not fully optimized.
- Currently, the application requires manual input of URLs and descriptions, which may not be ideal for all users.

## Future Enhancements
- **Browser Extension:** Plans are underway to transform this POC into a browser extension. This will allow users to select and note sections directly within the YouTube interface, eliminating the need to manually track and input text.

## Note
This project is intended as a proof of concept. The functionality and user interface are basic and intended for demonstration purposes. User feedback is welcome to improve the tool as development progresses.
