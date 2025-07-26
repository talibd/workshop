# Flask Upload Example

This repository contains a simple Flask application with an `/upload` endpoint. The endpoint saves the uploaded video in the `uploads/` directory and transcribes it using the OpenAI Whisper API.

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Set the `OPENAI_API_KEY` environment variable before running the server so the
application can access the Whisper API:

```bash
export OPENAI_API_KEY=your-key-here
```

## Running the app

```bash
python app.py
```

The server will start on `http://localhost:5000`.

## Usage

Send a POST request with `multipart/form-data` containing the `file` field:

```bash
curl -F "file=@path/to/video.mp4" http://localhost:5000/upload
```
The server responds with the JSON transcription result, including the full text
and timestamped segments. The file is also saved in the `uploads/` directory.
