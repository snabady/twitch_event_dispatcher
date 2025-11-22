from __future__ import annotations
import os
import shutil
import subprocess
import tempfile
import requests
import glob
import json
from typing import List, Optional

def _which(name: str) -> Optional[str]:
    return shutil.which(name)

def _run(cmd: List[str], capture: bool = True) -> subprocess.CompletedProcess:
    proc = subprocess.run(cmd, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None)
    if proc.returncode != 0:
        stderr = proc.stderr.decode(errors="ignore") if proc.stderr else ""
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nExit {proc.returncode}\nStderr:\n{stderr}")
    return proc

def _download(url: str, dst: str, chunk_size: int = 8192) -> None:
    with requests.get(url, stream=True, timeout=30) as r:
        r.raise_for_status()
        with open(dst, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

def _extract_frames_avifdec(avif_path: str, out_dir: str) -> List[str]:
    if _which("avifdec") is None:
        raise RuntimeError("avifdec nicht gefunden")
    pattern = os.path.join(out_dir, "frame_%04d.png")
    _run(["avifdec", avif_path, pattern])
    frames = sorted(glob.glob(os.path.join(out_dir, "frame_*.png")))
    return frames

def _extract_frames_ffmpeg(avif_path: str, out_dir: str) -> List[str]:
    pattern = os.path.join(out_dir, "frame_%04d.png")
    _run(["ffmpeg", "-y", "-vsync", "0", "-i", avif_path, pattern])
    frames = sorted(glob.glob(os.path.join(out_dir, "frame_*.png")))
    return frames

def _probe_frame_durations(avif_path: str) -> Optional[List[float]]:
    if _which("ffprobe") is None:
        return None
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_frames",
            "-print_format", "json",
            avif_path
        ], stderr=subprocess.DEVNULL)
        data = json.loads(out.decode())
        frames = data.get("frames", [])
        durations = []
        for f in frames:
            d = f.get("pkt_duration_time")
            if d is None:
                d = f.get("duration")
                tb = f.get("time_base")
                if d is not None and tb:
                    try:
                        num, den = tb.split("/")
                        tb_val = float(num) / float(den)
                        d = float(d) * tb_val
                    except Exception:
                        d = None
            if d is None:
                durations.append(None)
            else:
                try:
                    durations.append(float(d))
                except Exception:
                    durations.append(None)
        if not durations:
            return None
        if any(x is None for x in durations):
            return None
        return durations
    except Exception:
        return None

def _encode_frames_with_cwebp(frames: List[str], q: int, lossless: bool, tmpdir: str) -> List[str]:
    cwebp = _which("cwebp")
    if cwebp is None:
        raise RuntimeError("cwebp nicht gefunden")
    webp_frames: List[str] = []
    for i, f in enumerate(frames, start=1):
        out_frame = os.path.join(tmpdir, f"frame_{i:04d}.webp")
        cmd = [cwebp]
        if lossless:
            cmd += ["-lossless"]
        cmd += ["-q", str(q), f, "-o", out_frame]
        _run(cmd)
        webp_frames.append(out_frame)
    return webp_frames

def _assemble_with_webpmux(webp_frames: List[str], durations_ms: List[int], out_webp: str) -> None:
    """
    Correct webpmux invocation:
      webpmux -frame frame1.webp +100 -frame frame2.webp +100 -loop 0 -o out.webp
    Note: each '+<ms>' must be a separate argv element, not appended to filename.
    """
    webpmux = _which("webpmux")
    if webpmux is None:
        raise RuntimeError("webpmux nicht gefunden")
    cmd: List[str] = [webpmux]
    for fpath, dur in zip(webp_frames, durations_ms):
        # ensure absolute paths to avoid cwd confusion
        cmd += ["-frame", os.path.abspath(fpath), f"+{int(dur)}"]
    cmd += ["-loop", "0", "-o", out_webp]
    _run(cmd)

def avif_7tv_to_webp(url: str, output_path: str, fps: int = 30, quality: int = 75,
                    prefer_original_timing: bool = True, lossless: bool = False) -> str:
    if _which("ffmpeg") is None:
        raise RuntimeError("ffmpeg nicht im PATH")
    if _which("ffprobe") is None:
        raise RuntimeError("ffprobe nicht im PATH")

    out_path = output_path
    if os.path.isdir(output_path) or output_path == "." or output_path.endswith(os.sep):
        base = os.path.splitext(os.path.basename(url))[0] or "emote"
        out_path = os.path.join(output_path, base + ".webp")
    root, ext = os.path.splitext(out_path)
    if ext.lower() != ".webp":
        out_path = root + ".webp"
    os.makedirs(os.path.dirname(os.path.abspath(out_path)) or ".", exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="avif7tv_") as td:
        avif_file = os.path.join(td, "input.avif")
        frames_dir = os.path.join(td, "frames")
        os.makedirs(frames_dir, exist_ok=True)

        _download(url, avif_file)

        # extraction (prefer avifdec)
        frames: List[str] = []
        try:
            if _which("avifdec"):
                frames = _extract_frames_avifdec(avif_file, frames_dir)
            else:
                frames = _extract_frames_ffmpeg(avif_file, frames_dir)
        except Exception:
            frames = _extract_frames_ffmpeg(avif_file, frames_dir)

        if not frames:
            raise RuntimeError("Keine Frames extrahiert; Datei scheint ungültig oder leer zu sein.")

        # try to get frame durations
        durations_sec = None
        if prefer_original_timing:
            durations_sec = _probe_frame_durations(avif_file)

        # if we have durations and cwebp+webpmux available -> exact timing
        if prefer_original_timing and durations_sec and len(durations_sec) == len(frames) \
           and _which("cwebp") and _which("webpmux"):
            durations_ms = [max(1, int(round(d * 1000.0))) for d in durations_sec]
            webp_frames = _encode_frames_with_cwebp(frames, q=quality, lossless=lossless, tmpdir=td)
            _assemble_with_webpmux(webp_frames, durations_ms, out_path)
            return os.path.abspath(out_path)

        # fallback: simple ffmpeg build at constant fps
        pattern = os.path.join(frames_dir, "frame_%04d.png")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(fps),
            "-i", pattern,
            "-c:v", "libwebp",
            "-lossless", "1" if lossless else "0",
            "-qscale", str(quality),
            "-loop", "0",
            "-an", "-vsync", "0",
            out_path
        ]
        _run(cmd)
        return os.path.abspath(out_path)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: avif_7tv_to_webp_fixed.py <avif-url> <output.webp|out_dir> [fps] [quality] [prefer_original_timing:0|1] [lossless:0|1]")
        sys.exit(2)
    url = sys.argv[1]
    out = sys.argv[2]
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 75
    prefer = bool(int(sys.argv[5])) if len(sys.argv) > 5 else True
    lossless = bool(int(sys.argv[6])) if len(sys.argv) > 6 else False
    try:
        res = avif_7tv_to_webp(url, out, fps=fps, quality=quality, prefer_original_timing=prefer, lossless=lossless)
        print("Created:", res)
    except Exception as e:
        print("Error:", e)
        sys.exit(1)
