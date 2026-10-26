# MEER script-to-3D-cartoon pipeline (free-first)

## Goal
Generate new scene clips from a user script, while keeping the same 3D cartoon character recognisable across scenes. This is a design and acceptance checklist; it does not claim that an APK or GPU worker has already been built or tested.

## Important current-state findings
- `adv-clips/manifest.json` maps existing character names, clips, kinds, dialogue and slots. This is a reusable-clip fallback, not fresh scene generation.
- `patch_v458.py` documents the v4.58 coin wallet; it explicitly says coins do not create new scenes.
- `test/colab-factory/meer-ltx-fastlane-test.ipynb` describes an experimental LTX-Video 2B distilled image-to-video queue. Its own notes identify free GPU quota and throughput as constraints. Treat this as experimental until a run produces and validates clips.
- Do not add paid API calls, hard-coded secrets, hidden billing, or promises of unlimited generation.

## Proposed architecture
1. **Script planner (on device, no API):** split script into 1–3 minute target duration; produce ordered scene records with dialogue, action, environment, camera motion, character IDs and target seconds. Keep the user's original dialogue unchanged unless they request rewriting.
2. **Character bible:** each character has a stable reference image, name, visual description, colors, distinctive marks, and a negative prompt for unwanted redesigns. For Rayo, preserve red body, lightning-bolt mark, windshield eyes and bumper smile. Use the same reference image as the first frame / conditioning image for every generated clip where supported.
3. **Scene generation worker (free GPU, queued):** use the existing LTX-Video 2B distilled experiment as a candidate, after validating its license, hardware fit and output quality. Generate short clips one at a time. Never pretend that a notebook is an always-on free server; free GPU sessions and quotas are limited.
4. **Fallback:** if generation fails or quota is unavailable, offer the existing manifest-based clips and label them as reused library scenes. Do not silently claim they are newly generated.
5. **Composition:** use the app's existing native video/audio pipeline where possible. Normalize generated clips to one resolution, frame rate and codec before stitching. Keep TTS, music, captions and final MP4 muxing as separate verifiable steps.
6. **Job status:** persist story ID, scene index, generation status, asset checksum and error. Retry only the failed scene; do not rerun already completed clips.
7. **Privacy and security:** keep GitHub tokens and other credentials in notebook/worker secrets; never place them in the APK, JavaScript, repository, logs or prompt text.

## Suggested scene record
```json
{
  "story_id": "example-story",
  "scene_index": 1,
  "duration_seconds": 5,
  "character_ids": ["Rayo"],
  "dialogue": "Hi friends! I am Rayo!",
  "action": "Rayo drives slowly toward the camera and waves with his headlights",
  "environment": "bright flower meadow, gentle breeze",
  "camera": "smooth low tracking shot",
  "reference_image": "characters/rayo-reference.png",
  "generation_status": "queued"
}
```

## Acceptance tests before shipping an APK
- [ ] One new 5-second scene is generated from a prompt (not selected from adv-clips).
- [ ] Three scenes use the same Rayo reference image and pass a human visual consistency check.
- [ ] Scene actions and backgrounds match their corresponding script lines.
- [ ] A failed generation can be retried without duplicating completed scenes.
- [ ] Offline/no-GPU fallback is clearly labelled as library footage.
- [ ] Exported MP4 has video, audible TTS, optional music and subtitles; audio starts and ends correctly.
- [ ] Validate resolution, frame rate, duration, playback and file size on an actual Android device.
- [ ] Confirm the selected model's licence and all free-tier quotas before distributing.

## Free-tier reality
“Free-first” means no paid API is called and users are told when a free GPU is unavailable. It cannot guarantee unlimited generation, a particular completion time, or identical characters in every frame. Keep an optional low-cost local/static-scene fallback, but never introduce billing without explicit consent.
