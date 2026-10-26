# MEER: free script-to-animation implementation roadmap

This document turns the existing LTX fast-lane experiment into a realistic implementation plan. It is not a claim that the Android app has already been modified or that a production worker is deployed.

## User experience target
The user enters a script and chooses a character (Rayo/Bella/Rusty/Bruno). MEER:
1. Splits the script into ordered scenes.
2. Shows a scene list with dialogue, action, background and character reference.
3. Queues generation; the user may return later to collect the finished video.
4. Generates new clips when a free GPU worker is available; otherwise reports queued/paused state.
5. If the user chooses fallback, uses existing library clips and clearly marks them as reused footage.
6. Combines clips, TTS, music and captions, then verifies the exported MP4.

## What the current experiment tells us
The existing `test/colab-factory/meer-ltx-fastlane-test.ipynb` documents an LTX-Video 2B distilled proof. Its notes record a T4 result around 4.8 minutes per 5-second clip, and OOM failures at longer frame counts. Treat those as notebook-reported measurements, not an independent verification in this change. This means free GPU generation is not unlimited and a 1–3 minute story may take a long time, with GPU quota as a hard limit. A queue can improve convenience, but cannot manufacture free compute hours.

## Required implementation phases

### Phase 1 — safe test, no APK changes
- Run the notebook's 3-clip proof using a free GPU account.
- Confirm the model weights download, GPU memory, output duration, and MP4 decode.
- Use one reference still for the same character and review every frame for body/face/logo drift.
- Record actual wall time, peak VRAM, clip dimensions, output file size and failure rate.
- Do not start a large queue until one complete 3-clip proof passes.

### Phase 2 — scene planner
Create a pure local JavaScript planner (no paid LLM/API) that converts user-entered script lines into editable scene records. It should preserve exact dialogue, allow user edits, and require a reference image for each character. Prompt templates should explicitly lock character color, shape, eyes, mouth, marks, camera and motion direction. A deterministic template can follow a script but cannot reliably infer every nuanced action from arbitrary prose; show a preview for approval.

### Phase 3 — queued worker
- Worker reads queued scene jobs and processes one clip at a time.
- Store status: queued, running, complete, failed; include retry count and last error.
- Checkpoint each completed clip and resume after worker interruption.
- Use GitHub only for small proof artifacts if needed; avoid committing large generated videos into the source repository for routine production. Use user-controlled storage with clear limits for production.
- Put access tokens in Colab/Kaggle secret storage only. Never embed them in app JavaScript, APK resources or logs.
- Respect free account terms and quotas. No hidden paid fallback or billing.

### Phase 4 — render and export
- Normalize all clips to the same portrait resolution, frame rate and codec before stitching.
- Generate speech from the exact dialogue text using the existing native TTS path.
- Mux audio/video using the app's established Android pipeline; test the final MP4 on a real phone.
- Add music at a safe level, subtitle timing, duration validation and explicit failure messages.
- A completed status is set only after the exported MP4 is re-opened and its video/audio streams are checked.

## Acceptance tests
- New generated clip is demonstrably not a clip selected from `adv-clips/manifest.json`.
- Same reference character is used for all scenes in a story.
- Dialogue matches the script exactly.
- User can review and edit the scene plan before spending free GPU time.
- A failed scene can retry without regenerating successful scenes.
- A job can resume after a notebook session ends.
- Fallback footage is labelled as existing library footage.
- Final MP4 has a video stream, audible TTS, subtitles when enabled, correct order and playable duration.
- A real-device test confirms audio is present and playback is smooth.

## Non-negotiable honest limits
- No paid API calls or billing by default.
- No guarantee of unlimited free GPU, instant delivery, exact pixel-perfect story fidelity, or perfect character identity in every generated frame.
- If quota is exhausted, the app must say “queued/paused” or offer library fallback; never pretend the new animation is finished.
- Do not release as production-ready until the acceptance tests pass.
