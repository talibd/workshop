import { useState } from 'react';
import KeywordToggleList from '../components/KeywordToggleList';

export default function UploadPage() {
  const [videoFile, setVideoFile] = useState(null);
  const [brollImages, setBrollImages] = useState([]);
  const [subtitleStyle, setSubtitleStyle] = useState({
    fontFamily: 'Arial',
    fontSize: '24',
    color: '#ffffff',
    backgroundColor: '#00000080',
    position: 'bottom'
  });

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideoFile(file);
    }
  };

  const handleBrollChange = (e) => {
    const files = Array.from(e.target.files || []);
    setBrollImages(files);
  };

  const handleStyleChange = (e) => {
    const { name, value } = e.target;
    setSubtitleStyle({ ...subtitleStyle, [name]: value });
  };

  const handleRender = async () => {
    const payload = {
      fontSize: subtitleStyle.fontSize,
      fontColor: subtitleStyle.color,
      position: subtitleStyle.position,
      video: 'video.mp4',
      subtitles: 'subs.srt'
    };
    try {
      await fetch('http://localhost:5000/render', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (err) {
      console.error(err);
    }
  };

  const videoUrl = videoFile ? URL.createObjectURL(videoFile) : null;

  return (
    <div className="container">
      <h1>Video Upload</h1>
      <input type="file" accept="video/*" onChange={handleFileChange} />

      <div className="style-controls">
        <label>
          Font Family:
          <select name="fontFamily" value={subtitleStyle.fontFamily} onChange={handleStyleChange}>
            <option value="Arial">Arial</option>
            <option value="Helvetica">Helvetica</option>
            <option value="Times New Roman">Times New Roman</option>
          </select>
        </label>

        <label>
          Font Size:
          <input
            type="number"
            name="fontSize"
            value={subtitleStyle.fontSize}
            onChange={handleStyleChange}
            min="10"
          />
        </label>

        <label>
          Text Color:
          <input type="color" name="color" value={subtitleStyle.color} onChange={handleStyleChange} />
        </label>

        <label>
          Background:
          <input type="color" name="backgroundColor" value={subtitleStyle.backgroundColor} onChange={handleStyleChange} />
        </label>

        <label>
          Position:
          <select name="position" value={subtitleStyle.position} onChange={handleStyleChange}>
            <option value="bottom">Bottom</option>
            <option value="top">Top</option>
            <option value="center">Center</option>
          </select>
        </label>
      </div>

      {videoUrl && (
        <div className="video-wrapper">
          <video src={videoUrl} controls style={{ maxWidth: '100%' }} />
          <div
            className="subtitle-preview"
            style={{
              fontFamily: subtitleStyle.fontFamily,
              fontSize: subtitleStyle.fontSize + 'px',
              color: subtitleStyle.color,
              backgroundColor: subtitleStyle.backgroundColor,
              bottom: subtitleStyle.position === 'bottom' ? '10px' : 'auto',
              top: subtitleStyle.position === 'top' ? '10px' : subtitleStyle.position === 'center' ? '50%' : 'auto',
              transform: subtitleStyle.position === 'center' ? 'translateY(-50%)' : 'none'
            }}
          >
            Subtitle Preview
          </div>
        </div>
      )}

      <KeywordToggleList keywords={["nature", "people", "technology"]} />

      <div className="broll-upload">
        <h2>Upload B-roll Images</h2>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handleBrollChange}
        />
        <div className="broll-previews">
          {brollImages.map((img, idx) => (
            <img
              key={idx}
              src={URL.createObjectURL(img)}
              alt={`b-roll ${idx + 1}`}
              className="broll-thumb"
            />
          ))}
        </div>
      </div>

      <button className="render-btn" onClick={handleRender}>Render</button>

      <style jsx>{`
        .container {
          padding: 2rem;
        }
        .style-controls label {
          display: block;
          margin: 0.5rem 0;
        }
        .video-wrapper {
          position: relative;
          margin-top: 1rem;
        }
        .subtitle-preview {
          position: absolute;
          width: 100%;
          text-align: center;
          pointer-events: none;
        }
        .broll-upload {
          margin-top: 2rem;
        }
        .broll-previews {
          display: flex;
          flex-wrap: wrap;
          margin-top: 0.5rem;
        }
        .broll-thumb {
          height: 80px;
          margin-right: 0.5rem;
          margin-bottom: 0.5rem;
        }
        .render-btn {
          margin-top: 1rem;
          padding: 0.5rem 1rem;
          font-size: 1rem;
        }
      `}</style>
    </div>
  );
}

