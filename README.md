# Flask Upload Example

This repository contains a simple Flask application with an `/upload` endpoint that accepts a video file and saves it locally in the `uploads/` directory.

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
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

The uploaded file will be stored in the `uploads/` directory.
