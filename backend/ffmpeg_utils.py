import subprocess
from typing import List, Tuple


def _hex_to_ass_color(hex_color: str) -> str:
    """Convert ``#RRGGBB`` into ``&H00BBGGRR`` format used by ASS styles."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("invalid color format")
    r = hex_color[0:2]
    g = hex_color[2:4]
    b = hex_color[4:6]
    return f"&H00{b}{g}{r}"


def _position_to_alignment(pos: str) -> int:
    """Return ASS alignment value for a simple position string."""
    mapping = {"bottom": 2, "top": 8, "center": 5}
    return mapping.get(pos, 2)


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
    font_size: int = 24,
    font_color: str = "#ffffff",
    position: str = "bottom",
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
    font_size: int
        Font size for burned subtitles.
    font_color: str
        Hex color (``"#RRGGBB"``) for subtitle text.
    position: str
        One of ``"bottom"``, ``"top"`` or ``"center"`` subtitle placement.

    Returns
    -------
    str
        The path to the rendered video.
    """
    width, height = _get_video_size(video_path)
    alignment = _position_to_alignment(position)
    color_code = _hex_to_ass_color(font_color)
    force_style = f"Fontsize={font_size},PrimaryColour={color_code},Alignment={alignment}"

    # Prepare input arguments
    cmd = ["ffmpeg", "-y", "-i", video_path]
    for img, _, duration in overlays:
        cmd.extend(["-loop", "1", "-t", str(duration), "-i", img])

    # Build filter complex
    filter_parts = [f"[0:v]subtitles={subtitles_path}:force_style='{force_style}'[v0]"]
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


def generate_preview_clip(
    video_path: str,
    subtitles_path: str,
    overlays: List[Tuple[str, float, float]],
    timestamp: float,
    layout: str = "fullscreen",
    output_path: str = "preview.mp4",
    font_size: int = 24,
    font_color: str = "#ffffff",
    position: str = "bottom",
) -> str:
    """Create a 10-second clip starting at ``timestamp`` with overlays.

    Parameters
    ----------
    video_path: str
        Path to the source video.
    subtitles_path: str
        Path to an SRT subtitle file to burn into the clip.
    overlays: List[Tuple[str, float, float]]
        Each tuple contains (image_path, start_time, duration) where
        ``start_time`` is relative to the beginning of the preview clip.
    timestamp: float
        The start time of the preview in the original video.
    layout: str
        Overlay placement, same options as ``compose_video``.
    output_path: str
        Where to write the resulting clip.
    font_size: int
        Font size for burned subtitles.
    font_color: str
        Hex color (``"#RRGGBB"``) for subtitle text.
    position: str
        Subtitle placement (``"bottom"``, ``"top"`` or ``"center"``).

    Returns
    -------
    str
        The path to the preview clip.
    """
    width, height = _get_video_size(video_path)
    alignment = _position_to_alignment(position)
    color_code = _hex_to_ass_color(font_color)
    force_style = f"Fontsize={font_size},PrimaryColour={color_code},Alignment={alignment}"

    cmd = ["ffmpeg", "-y", "-ss", str(timestamp), "-t", "10", "-i", video_path]
    for img, _, duration in overlays:
        cmd.extend(["-loop", "1", "-t", str(duration), "-i", img])

    filter_parts = [f"[0:v]subtitles={subtitles_path}:force_style='{force_style}'[v0]"]
    current = "v0"
    for idx, (_, start, duration) in enumerate(overlays, 1):
        scale, pos = _layout_params(layout, width, height)
        filter_parts.append(f"[{idx}:v]scale={scale}[ov{idx}]")
        filter_parts.append(
            f"[{current}][ov{idx}]overlay={pos}:enable='between(t,{start},{start + duration})'[v{idx}]"
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
