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


## Optional: opening layout with a saved-latent continuation

Use [04-layout-first-clip.json](04-layout-first-clip.json) ([API](api/04-layout-first-clip.api.json)) **instead of 01**, then continue with **02**. This keeps the character/environment/face/prop picture order of 01/02 and adds `opening-layout.png` through native **MiniMaxH3AddGuide at frame 0**. It also saves Motion Context slot **1** in the same sequence folder, so template 02 can load that completed first clip.

This is the wiring used for the revised continuation example: a starting composition matching the rough guide helped keep the first segment's framing more stable in this test. It is not a guarantee of exact camera tracking. Ordinary Picture references are still whole-clip appearance references; the extra native frame-zero input is separate, and is not Picture 5 or a tail-frame lock. No additional ControlNet or model weights are required.

Template 04 uses **124 frames**. Its sampler latent still comes directly from Reference To Video; Add Guide changes only the positive conditioning passed to the Guider. The sampler output also feeds Save Latent. Template 03 remains the separate standalone fast-camera example described above.

### Preserve the full guide at frame-grid boundaries

In the local H3 build used for this episode, the reference-video encoder trims its input to the `17n + 5` frame grid. A 146-frame guide is trimmed to 141 even if generation is requested at 158. To retain all 146 original guide frames, pad 12 copies of its last frame **before generation**, making a 158-frame guide; do not offset the comparison afterward.

With 22 frames of inherited context removed, the 158-frame generation provides 136 new frames. The episode's equal-duration comparison displays the first 124 of those new frames against original guide frames 22 through 145. Thus the selected action is **124 + 124 = 248 frames (10.33 seconds at 24 fps)**; the pause at the join is an editorial hold shown separately.

All downloadable media names are placeholders. Six media loaders in 04 require your own four appearance images, guide video, and opening layout. Importing the template without those files can show missing-media warnings; select the real files before running. The UI was imported into the current frontend and all 25 nodes and generation inputs round-tripped to the API variant without submitting a GPU job. This validates wiring, not a fresh generation on another installation.


## Optional: native ending layout with Motion Context

Use [05-tail-layout-motion-context.json](05-tail-layout-motion-context.json) ([API](api/05-tail-layout-motion-context.api.json)) instead of **02**, after completing **01** or **04** and saving its actual first-clip context. This adds `ending-layout.png` to the existing native **MiniMaxH3AddGuide**, with **frame_idx = -1**. The native node resolves this to the last frame of the current generation. It is separate from the four ordinary Picture references and requires no additional ControlNet or model weights.

The graph passes Reference To Video positive conditioning through Add Guide, then Motion Context, then the Guider. Motion Context retains the ending anchor while pinning the inherited head. Add Guide has only one conditioning output; the sampler latent still comes directly from Reference To Video.

- Output generation: **1280 × 704**, **158 frames** at 24 fps.
- Native ending index: **157** before trimming.
- Motion Context removes **22 inherited frames**, leaving **136 new frames**. The ending anchor corresponds to new-frame index **135**.
- The continuation guide should include the same 22-frame overlap at its beginning. New output frame0 corresponds to guide frame22; keep the same source/result clock when comparing.
- Prepare an ending image with the same character, clothing, lighting and geography, and a camera composition consistent with the guide's end. The native node uses aspect-preserving cover-crop to the output canvas: allow headroom and use the output aspect ratio when framing the image.

The ending image guides the result; it is not a promise of pixel-identical output or perfect camera following. Review the actual transition and final frames, rather than pasting the target still over a failed result. The episode's revised motorcycle reveal combines this native ending image with its actual previous-clip Motion Context. The riding approach may be sped up in the edit, with the rough guide and output receiving identical timing changes; the generation originals remain unchanged.

All six media loaders require your own files: four appearance references, the continuation guide video, and `ending-layout.png`. Templates 01/02/03/04 remain unchanged. The UI was imported into the frontend and all 28 nodes round-tripped to the API inputs without submitting a generation job. Missing-media warnings are expected until you select your own files. No private images, voices or latent caches are included.
