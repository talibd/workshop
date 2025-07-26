import subprocess
from typing import List, Tuple


def _get_video_size(path: str) -> Tuple[int, int]:
    """Return width and height of the given video using ffprobe."""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height",
        "-of",
        "csv=p=0:s=x",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def _layout_params(layout: str, width: int, height: int) -> Tuple[str, str, str]:
    """Return scale and position for overlay based on layout."""
    if layout == "fullscreen":
        scale = f"{width}:{height}"
        pos = "0:0"
    elif layout == "center box":
        scale = f"{width // 2}:{height // 2}"
        pos = "(main_w-overlay_w)/2:(main_h-overlay_h)/2"
    elif layout == "text-clip":
        scale = f"{width // 3}:-1"
        pos = "(main_w-overlay_w)/2:main_h-overlay_h-50"
    else:
        raise ValueError(f"Unknown layout: {layout}")
    return scale, pos


def compose_video(
    video_path: str,
    subtitles_path: str,
    overlays: List[Tuple[str, float, float]],
    layout: str = "fullscreen",
    output_path: str = "output.mp4",
) -> str:
    """Burn subtitles and overlay images onto a video using FFmpeg.

    Parameters
    ----------
    video_path: str
        Path to the source video.
    subtitles_path: str
        Path to an SRT subtitle file to burn into the video.
    overlays: List[Tuple[str, float, float]]
        Each tuple contains (image_path, start_time, duration).
    layout: str
        One of ``"fullscreen"``, ``"center box"`` or ``"text-clip"`` to
        control the overlay placement.
    output_path: str
        Where to write the resulting video.

    Returns
    -------
    str
        The path to the rendered video.
    """
    width, height = _get_video_size(video_path)

    # Prepare input arguments
    cmd = ["ffmpeg", "-y", "-i", video_path]
    for img, _, duration in overlays:
        cmd.extend(["-loop", "1", "-t", str(duration), "-i", img])

    # Build filter complex
    filter_parts = [f"[0:v]subtitles={subtitles_path}[v0]"]
    current = "v0"
    for idx, (_, start, duration) in enumerate(overlays, 1):
        scale, pos = _layout_params(layout, width, height)
        filter_parts.append(f"[{idx}:v]scale={scale}[ov{idx}]")
        filter_parts.append(
            f"[{current}][ov{idx}]overlay={pos}:enable='between(t,{start},{start+duration})'[v{idx}]"
        )
        current = f"v{idx}"

    filter_complex = ";".join(filter_parts)

    cmd.extend([
        "-filter_complex",
        filter_complex,
        "-map",
        f"[{current}]",
        "-map",
        "0:a?",
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        "-movflags",
        "+faststart",
        output_path,
    ])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr}")

    return output_path
