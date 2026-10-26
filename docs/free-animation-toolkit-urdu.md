# MEER: Free-first animated video toolkit (Urdu guide)

This guide is a practical starting point, not a promise of unlimited free video generation. Free hosted GPUs have quotas and may be unavailable. Model licences and hosted-service rules must be checked before commercial use.

## 1. Recommended workflow

1. Accept a story/script and split it into one short action per line.
2. Keep one character reference image and a fixed character description.
3. Generate a short image-to-video clip for each line with LTX-Video, using the same reference image where supported.
4. Check each clip; retry only failed/mismatched scenes.
5. Normalize clips with FFmpeg (same dimensions, 24 fps, H.264, no B-frames).
6. Generate narration using local TTS if possible; gTTS is an online convenience and is not a guaranteed permanent service.
7. Create SRT subtitles from script lines (timings need correction against actual narration).
8. Add licensed/own music at low volume; mix narration clearly above music.
9. Concatenate/mux to MP4 and verify that the final file has video AND audio streams.

## 2. Useful official links

- MEER repository: https://github.com/Hamzaagsm/videomaker
- Experimental MEER Colab notebook: https://colab.research.google.com/github/Hamzaagsm/videomaker/blob/feature/script-to-3d-cartoon-plan/test/colab-factory/meer-script-to-animation.ipynb
- LTX-Video official repository: https://github.com/Lightricks/LTX-Video
- LTX-Video model page: https://huggingface.co/Lightricks/LTX-Video
- FFmpeg: https://ffmpeg.org/
- Piper local TTS: https://github.com/rhasspy/piper
- Google Colab: https://colab.research.google.com/

## 3. Model URL used by the current prototype

```python
LTX_2B_DISTILLED_URL = "https://huggingface.co/Lightricks/LTX-Video/resolve/main/ltxv-2b-0.9.8-distilled.safetensors"
LTX_LOCAL = "ltxv-2b-0.9.8-distilled.safetensors"
LTX_SIZE = 6340744492  # expected bytes for the file noted by this notebook
```

Download and size-check the weights before loading. If the size changes upstream, verify the current official model files rather than blindly forcing the old byte count. A failed download, changed filename, missing dependency, or incompatible model/config can stop the notebook.

## 4. Free vs. genuinely unlimited

- Google Colab free GPU: no guaranteed GPU, runtime length, or quota. Treat it as a test environment, not a production server.
- Local generation: no per-generation API fee if you run an open model yourself, but requires suitable GPU/RAM/storage and electricity. CPU-only generation may be extremely slow.
- Hosted free inference: limits and terms can change; do not build the app around an undocumented or temporary free endpoint.
- gTTS: online service convenience, not a guaranteed permanent free commercial API. For more control, use local TTS such as Piper after checking available voice/licence.
- Music: use original music or assets whose licence explicitly permits your intended use. Do not assume every “free download” can be used commercially.

## 5. Character consistency and scene accuracy

- Use one clean, full-character reference image with no text/watermark.
- Keep the same exact character description in every prompt.
- Change only the action, camera and background for each scene.
- Use short clips first (2–3 scenes) to validate the pipeline.
- Image conditioning helps but does not guarantee pixel-identical characters or literal script compliance. Review clips and retry mismatches.
- Do not create a whole 2-minute video in one model call. Generate scene-by-scene and checkpoint completed clips.

## 6. Suggested FFmpeg commands

Normalize a generated clip to a consistent vertical format:

```bash
ffmpeg -y -i input.mp4 -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=24" -an -c:v libx264 -pix_fmt yuv420p -bf 0 -g 48 -crf 22 normalized.mp4
```

Mux narration with visuals (replace filenames):

```bash
ffmpeg -y -i visuals.mp4 -i narration.mp3 -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -shortest final.mp4
```

Add subtitles by burning in an SRT (font availability varies):

```bash
ffmpeg -y -i final.mp4 -vf "subtitles=subtitles.srt" -c:v libx264 -crf 22 -c:a copy final-subtitled.mp4
```

Always test commands on a short sample first. The exact FFmpeg filter syntax may need adjustment for Windows paths or Colab.

## 7. Minimum test checklist

- [ ] Run only 2–3 scenes first.
- [ ] Confirm every generated clip exists and has non-zero size.
- [ ] Use ffprobe to confirm video codec, frame rate, duration and audio stream.
- [ ] Listen to the final MP4; do not assume audio muxing succeeded.
- [ ] Check subtitle timing manually.
- [ ] Confirm the music and any downloaded assets have a suitable licence.
- [ ] Save intermediate clips and a checkpoint so a runtime interruption does not force a full restart.
- [ ] Never put private tokens/API keys inside the Android APK or public repository.

## 8. Integration into the Android app

The current Colab notebook is a prototype and does not itself add generation to the APK. A reliable app integration needs a job queue and worker that can run the model, progress/status updates, storage for generated clips, retry/checkpoint handling, and a secure download/export step. If using only a user's Colab session, the user must run the notebook manually; it is not a permanent backend service.
