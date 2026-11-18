# H3: 3D guide video + Motion Context

Generate a finished shot from reference pictures, a rendered 3D guide video and a prompt. Then carry the first generation's video/audio latent into the next clip.

## Open in ComfyUI

1. Open [01-first-clip.json](01-first-clip.json), choose your installed models and reference files, and run the first clip. It saves latent slot **1**.
2. Open [02-motion-context.json](02-motion-context.json), select the second guide video, and keep the same resolution and sequence folder. It loads slot **1**, generates the continuation and saves slot **2**.
3. The Trim node removes the repeated opening from both picture and sound. Join the trimmed continuation to the first clip in your editor.

These are reusable templates based on the wiring used in the video, with placeholder reference filenames. They do not include reference images, voice recordings, model weights or latent caches. Replace the example prompts and references with your own project.

## The important connections

| Purpose | Connection |
| --- | --- |
| 3D guide video | Load Video → Get Video Components → **video reference** on MiniMax H3 Reference To Video |
| Appearance and task | Picture references + prompt → the same reference-conditioning node |
| First clip cache | Sampler latent output → Save Latent |
| Continue a completed clip | Load Latent → Motion Context's previous-latent input |
| Context conditioning | Current reference conditioning → Motion Context → Guider |
| New starting latent | Current reference node's latent output → Sampler, separately |
| Remove repetition | Decoded image/audio → Motion Context Trim → Create Video / Save Video |

Motion Context uses a **previous completed generation**, not feedback from the current sampler execution.

## References for templates 01/02

Place your files in ComfyUI's input folder, then select them in the loader nodes:

- `character-body.png`: character and wardrobe reference.
- `scene-reference.png`: environment reference.
- `character-face.png`: face reference.
- `prop-reference.png`: optional project prop reference; update the prompt if you remove it.
- `3d-guide-clip-1.mp4` and `3d-guide-clip-2.mp4`: your rendered 3D animations at 24 fps.

The model receives the rendered video, not a Blender/Three.js scene file. Make intended front/back, character placement and camera direction visible and consistent with your picture references and prompt.

## Settings in templates 01/02

- Six-step Pika H3 Flex sampling, 1280 × 704, 24 fps.
- First clip: **124 frames**.
- Continuation: **158 frames**, explicitly on H3's `17n + 5` frame grid.
- Motion Context: **22 video frames / 18 audio frames**.
- Sequence folder: `h3_3d_guide/sequence_01`; Save uses the `clip` prefix inside that folder. Start a new folder for a different sequence.

After removing 22 repeated frames, the 158-frame continuation has **136 new frames**. Any extra tail cut for an equal-length comparison is an editing step, not something Trim does automatically. The published continuation uses 158 explicitly because an intermediate API request of 146 rounds up internally, while importing that off-grid value in the frontend can snap it differently.

## Dependencies

- A ComfyUI build with MiniMax H3 reference-to-video nodes and matching H3 model / text-encoder / video-and-audio VAE files.
- [Pika H3 Flex](https://github.com/Pika-Labs/Pika-H3-Flex) and its matching adapter.
- [ComfyUI H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context).

Model filenames in the templates reflect the local setup used for the episode; select the corresponding installed files on your machine. JSON import and node/wiring validation do not certify a fresh run on another installation.

## API format

[First clip API graph](api/01-first-clip.api.json) · [Motion Context API graph](api/02-motion-context.api.json)

The API and UI variants have the same generation inputs and links. UI-only node positions and fixed-seed controls are included in the normal ComfyUI files.

## Optional: add an opening-frame layout

[03-optional-first-frame.json](03-optional-first-frame.json) is a separate eight-second, two-character example based on the fast-camera test. [API version](api/03-optional-first-frame.api.json).

It adds a native **MiniMaxH3AddGuide** node with **frame_idx = 0**. An opening layout image sets an initial composition in addition to the ordinary character pictures and rough guide video. Use a resolved starting-frame image matching the guide's initial camera view, rather than an unrelated character portrait. This extra image is the opening composition used in the camera test, separate from the four character references. This is not ControlNet, an animated body-pose reference, or a guarantee of exact camera following.

| Role | Example file |
| --- | --- |
| Picture 1: first fighter's body and clothes | `fighter-a-body.png` |
| Picture 2: first fighter's face | `fighter-a-face.png` |
| Picture 3: second fighter's body and clothes | `fighter-b-body.png` |
| Picture 4: second fighter's face | `fighter-b-face.png` |
| Additional initial composition, not Picture 5 | `opening-layout.png` |
| Actual rendered camera/position guide | `3d-guide-fast-camera.mp4` |

This picture order differs from templates 01/02. Replace every placeholder with your own file and update the prompt when changing the reference order or camera route. The included prompt is an example with a push toward the first face, a fast move to the second face, then a pullback. It does not invent a matching camera route in a different guide video.

Important wiring:

- Reference To Video's **positive** → Add Guide's **positive**.
- Reference To Video's **latent** → Add Guide's **latent** input.
- Video VAE → Add Guide's **vae**; opening layout Load Image → **image**.
- Add Guide's single **positive/CONDITIONING** output → Basic Guider.
- Reference To Video's **latent** still feeds the sampler directly. Add Guide does not produce a new sampler latent.

The native node must exist in your ComfyUI build. This local example uses the same installed H3/Pika models as the other templates; no extra ControlNet weights were added.

Template 03 is a **standalone clip**: 192 frames at 24 fps, six-step Pika sampling, and no Motion Context cache writer. It does not create slot 1 for template 02. Use the original 01→02 sequence for the saved-latent continuation example; do not point template 02 at an unrelated old cache after running 03.

For the coarse guide, generic bodies can control camera and root positions while the prompt lets H3 invent bodily acting. Simple eyes and a mouth can indicate where a face belongs and which direction it faces; the character pictures define the actual human features. Inspect the native-speed source/result comparison. The tested fast-camera sequence followed the broad shot order, but its close-up crops and transitions were not frame-exact.

No reference media, private voice recordings, model weights or latent caches are included.
