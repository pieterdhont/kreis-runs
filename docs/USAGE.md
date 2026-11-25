# Using Kreis Runs

Open `app/kreis-runs/index.html` (see the README for serving it locally). Kreis starts running at a jog. All settings except the camera position are remembered in your browser between visits.

## The scene

- **Distance counter** (top right): metres run since the page loaded.
- **Move pad** (bottom right): moves the camera; see *Moving the camera*.
- **Shot label** (bottom left, Director mode only): names the current shot.

## Controls

### Run and Pause
Freezes everything: Kreis, cloth, hair and the landscape. The camera can still be moved, zoomed and orbited while paused, which is useful for inspecting a single moment of the stride.

### Camera angles

| Angle | What it shows |
|---|---|
| **Side** | A telephoto tracking shot from the side, the classic way to watch the gait |
| **Chase** | From behind and to one side, looking down the path ahead |
| **Orbit** | Circles Kreis slowly |
| **Low** | Near the ground in front of him, looking up |
| **Crane** | High and wide, looking down over the landscape |
| **Director** | Cuts automatically between seven shots, each with its own zoom move: establishing push-in, tracking, face close-up with shallow focus, low-angle hero with a tilt, chase with a dolly zoom, orbit pull-out and aerial pull-back |

Camera changes glide into place, except in Director mode, which uses hard cuts.

### 360° circle
Makes any angle, Director included, circle all the way around Kreis while keeping that angle's height, distance and lens.

### Orbiting by hand
Drag the scene with the mouse or one finger to orbit around Kreis (left and right) and tilt (up and down). This works on every angle and combines with the 360° circle.

### Zoom
Use the scroll wheel, a two-finger pinch, the slider, or the − and + buttons. The range goes from a close-up where his face fills the frame to a wide aerial view. When you zoom out, the camera rises to look over the land. When you zoom in close, it aims at his head.

### Moving the camera
Hold the **joystick** to slide the camera left, right, up or down. Hold the **rocker** beside it to move forward or back. The further you push, the faster it moves. Moves follow your current view, so "left" is always left on screen, and the on-screen speed is the same at any zoom. **Centre** removes your moves. The **Move pad** button shows or hides the pad.

### Reset view
Resets zoom, orbit, tilt and camera moves. Double-clicking the scene does the same.

### Light
Choose **Day** or **Dusk**. Dusk brings a low orange sun, long shadows and a darker sky. The light fades between the two.

### Speed
The slider sets his actual running speed in metres per second, from 0.8 to 10. The label shows the speed and the gait:

| Speed | Gait | What to look for |
|---|---|---|
| below 1.5 m/s | walk | both feet on the ground together, body rising over each step, relaxed arms |
| 1.5–2.1 m/s | jog | first flight phase between steps, bent elbows |
| 2.1–3.2 m/s | run | longer flight, stronger lean |
| 3.2–6.5 m/s | sprint | forefoot landings, high heel kick, driving arms |
| 6.5–10 m/s | full sprint | about 5.4 steps per second, very short ground contact, cape flying flat |

Changes ease in over a second or two. Dragging the slider quickly shows him leaning into acceleration or back when braking.

### Quality

| Setting | Effect |
|---|---|
| **Auto** (default) | Picks High, Balanced or Fast from the frame rate. The label shows which one it is using. |
| **High** | Full resolution (up to 1.75× on sharp screens), sharpest shadows, most cloth simulation steps |
| **Balanced** | Slightly reduced resolution and shadow detail |
| **Fast** | 1× resolution, softer shadows, lighter cloth, hair shape updated every other frame |

### Cinema effects
These combine with any angle and with zoom:

- **Depth of field:** keeps Kreis sharp and blurs the world, more strongly when zoomed in. This is the most demanding effect.
- **Letterbox:** black bars slide in for a 2.39:1 widescreen frame.
- **Handheld:** a gentle camera sway.
- **Slow push:** the zoom slowly breathes in and out.
- **Dutch tilt:** tilts the horizon.
- **Dolly zoom:** the lens widens while the camera moves in, so the world stretches behind Kreis while he stays the same size.

## Keyboard shortcuts

| Key | Action |
|---|---|
| Space | Pause and run |
| 1–6 | Side, Chase, Orbit, Low, Crane, Director |
| C | 360° circle on or off |
| Arrow keys | Orbit left and right, tilt up and down |
| W A S D | Move the camera forward, left, back, right |
| Q / E | Move the camera down / up |
| + / − | Zoom in / out |
| 0 | Reset zoom |
| N | Day or dusk |
| Z | Dolly zoom |

## Good views to try

- **The gait:** Side at about 1.5× zoom, dragging the speed slowly from a walk to a full sprint.
- **The cape and hair:** Chase or Low at 2–3× zoom, at 3 m/s and then at 10 m/s.
- **The face:** Low at 3–4× zoom with the speed above 3 m/s, to see the eyes narrow and the mouth open.
- **The twist of shoulders against hips:** turn on 360° circle and watch from the front.
- **Something cinematic:** Director with Letterbox and Depth of field at Dusk.

## Troubleshooting

- **The scene stays blank or says it couldn't start:** the page needs internet access to load three.js from the CDN, and a browser with WebGL. Try serving it over `http://localhost` instead of opening the file directly.
- **Stuttering:** set Quality to Fast, turn off Depth of field, or make the browser window smaller.
- **The camera is lost somewhere:** press Reset view, or double-click the scene.
