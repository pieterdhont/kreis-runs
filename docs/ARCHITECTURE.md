# How Kreis Runs works

The app is a single HTML file (`app/kreis-runs/index.html`) with one ES-module script. It uses three.js r160 from a CDN, plus one data file, `kreis_body.js`, that holds the sculpted body. There's no build step. This document walks through the script in the order it runs.

## 1. Renderer, sky and light

- **Renderer:** `WebGLRenderer` with ACES filmic tone mapping, sRGB output and PCF soft shadows from one directional "sun" light, plus a hemisphere light.
- **Sky:** a large back-faced sphere with a two-stop gradient shader. It follows the camera.
- **Sun disc:** a flat circle with two rings, placed far away along a "disc direction" so it reads as part of the sky.
- **Day and dusk:** two palettes (sky, fog, ground, sun colour and intensity, hemisphere colours, light direction, exposure). Everything blends between them with one factor, `todK`.
- **Fog and shadows:** linear fog and the shadow camera bounds widen with camera distance, so wide shots stay readable.

## 2. The landscape

The world is a group made of 5 chunks, each 36 m long, that scrolls along −x at Kreis's speed. When a chunk falls more than 70 m behind him, it is rebuilt one place further ahead. Each chunk is generated from a seeded random generator (mulberry32) keyed by the chunk's index, so the land is endless but repeatable.

Each chunk contains:
- the path (a 4 cm slab with dashes and edge lines);
- colour-field meadows;
- an occasional arch over the path;
- sculptures on the near side of the path: plinths with spheres, stepped blocks, quarter-circle walls, pergolas, rings, half-discs and cones;
- white modernist houses on stilts with window bands, colour accents and stair towers;
- lollipop and cone trees;
- distant half-disc, cone and stepped hills;
- clouds.

All of it is built from a few shared unit geometries and cached materials, so rebuilds are cheap.

## 3. The character asset: `tools/sculpt_kreis.py`

Kreis's body and clothes are one watertight mesh, generated offline:

1. **Signed-distance sculpt.** About 40 named primitives (ellipsoids, round cones, a rounded band) in a hips-relative rest pose: cranium, jaw, chin, neck, chest, ribcage, waist, trapezius, shoulder caps, pelvis, obi, sleeves, bare upper arms, forearms, hands, thumbs, hakama thighs, flared lower legs with a flat-cut hem, shins, heels and toes. They are combined with smooth-min blends where flesh or cloth should flow together, and with hard unions where limbs must stay separate (arms from the torso, legs from each other).
2. **Meshing.** The field is sampled on a 3.5 mm grid and turned into a surface with marching cubes. The largest piece is kept, then Taubin smoothing, quadric decimation to about 60k triangles, and a little more smoothing.
3. **Labels.** Each vertex gets the name of the primitive nearest to it, which drives both colour and skinning.
4. **Colours.** Smooth bands instead of hard switches: blue trousers, black obi with a red stripe, a yellow top shading from gold at the waist to bright at the chest, a white neck and head, white hands, red shoes and a white tabi band. Crisp edges (the collar, sleeve hems and trouser hems) are separate thin geometry in the app.
5. **Skin weights** for 19 bones, computed per region from the position along each chain with smoothstep blends across every joint:
   - spine: waist to chest to neck to head;
   - shoulder caps: chest to shoulder;
   - arms: shoulder to elbow to wrist;
   - pelvis: hips to waist, and to the thigh on its own side;
   - legs: hips to thigh to knee to ankle;
   - feet: ankle to toe.

   Each vertex keeps its 4 strongest weights.
6. **Export.** Positions (float32), colours (uint8, sRGB), skin indices and weights (uint8), and index buffers for two small "probe" sub-meshes of the head and torso, all base64-encoded into `window.KREIS_BODY`.

## 4. Building the character in the app

- **Skeleton.** A `THREE.Bone` hierarchy mirrors the sculpt's rest pose exactly:
  - `hips`, then `waist`, `chest`, `neck` and `head` (the head bone is scaled 0.9);
  - shoulder groups on the torso, each carrying shoulder, elbow and wrist bones;
  - thigh, knee, ankle and toe bones on the hips.

  The body is one `SkinnedMesh`, plus a second skinned mesh that draws the ink outline (back faces pushed out along their normals, in a skinning-aware shader).
- **Materials.** `MeshToonMaterial` with a soft-edged 128-step ramp, vertex colours, and a fresnel rim term added with `onBeforeCompile`.
- **Face.** The eyes (iris, lower iris, pupil, two highlights, lash, lower lid), brows, cheek blush, nose and two mouths (a line and an open one) are flat shapes. They are projected onto the head by ray-casting against the head probe and offset along the surface normal. Eyes and brows live in small groups so they can blink, narrow and furrow.
- **Chest details.** The wrap line, family crest and sun disc are placed by ray-casting the torso probe from the front or back. The collar and the sleeve and trouser hems are thin black bands parented to the chest, shoulder and knee bones.

## 5. Locomotion

All of this happens in `pose(phase, sp, dt)`. `sp` is the internal speed value, and `speedOf(sp)` converts it to metres per second.

### Gait parameters, `gaitParams(sp)`
From the speed it derives:
- `run`: a 0→1 blend from walking to running, around 1.45–1.75 m/s;
- `spr`: a 0→1 blend from running to full sprint, from 3.2 to 9.6 m/s;
- steps per second (walk ≈ 1.45 + 0.5v; run 2.6 + 0.25v up to 3.2 m/s, then towards 5.4);
- ground-contact time (walk duty ≈ 0.62; run 0.31 − 0.04v, then towards 0.075 s at 10 m/s);
- flight time, and stance length `L = v × contact time`;
- heel-strike angle, forefoot-landing angle, toe-off angle, swing height, knee-drive reach and foot width.

Timings are human values scaled to Kreis's 0.67 m leg (×0.86, Froude scaling).

### Reach check
The hip height at touchdown is lowered (more knee bend) until both the landing ankle and the push-off ankle are within the leg's reach (0.66 m). The landing point is then clamped between the two limits.

### Feet, `footState`
In stance, the foot is fixed in the world, so in body space it moves back at exactly the speed the landscape scrolls. That's why the feet don't slide. Below about 4.5 m/s the foot rotates about the heel (heel strike), lies flat, then rotates about the ball of the foot (toe-off, with the toe bone bending to stay flat). Above that the foot lands on the ball and never sets the heel down. In swing, the ankle follows a cubic Bézier from toe-off to the next strike (heel kick up behind, then knee drive forward) while the foot pitch blends from toe-down to the landing angle.

### Legs, `legIK`
Analytic two-bone IK in hips space. The thigh aims with its knee pointing forward, and the knee folds by the law of cosines. The ankle orientation is set so the foot holds its ground pitch in world space.

### Body height
- **Walking:** a pendulum vault, highest at mid-stance.
- **Running:** a spring-mass dip during stance with a matching ballistic arc in flight (g = 9.81), continuous in position and velocity.

The two blend with `run`. A damped spring adds a jolt at each touchdown.

### Torso
- **Pelvis yaw** follows the measured thigh angles; **chest yaw** follows the measured arm angles. That keeps them in true opposition.
- **Obliquity:** the pelvis drops on the unloaded side, and the trunk sways over the loaded leg while staying upright.
- **Spine:** flexes at mid-stance and extends at push-off.
- **Lean** grows with speed and acceleration.
- **Shoulders** move forward and back with each arm.
- **Head** cancels the accumulated yaw and roll so the gaze stays on the path.
- **Breathing:** the chest scales in time with the stride.

### Arms
Shoulder swing comes from a hip-flexion keyframe curve for running (bigger at sprint) and a cosine swing for walking. The elbow bends more as the arm comes forward. Critically damped springs give the arms follow-through.

## 6. Cloth (cape, obi tails, sleeve ribbons)

`makeCloth` builds a particle grid from a rest shape in its parent's space, with the top row pinned. The cape is 12×22 with a split hem made by removing constraints and triangles across the centre of its lower half. The two obi tails are 3×15 and the sleeve ribbons 2×9. Constraints are structural, shear and bending, stored in typed arrays.

Each step (default 1/200 s, capped per frame so a slow frame can't snowball):

1. **Aerodynamics** per triangle: relative air is the wind minus the triangle's velocity. The wind is −v along x plus a slow breeze, reduced in the body's wake and given turbulence that scales with speed. Force = pressure drag along the normal plus a little skin friction, split over the three vertices.
2. **Verlet integration** with gravity, damping and a speed limit.
3. **Pins** interpolate across the frame.
4. **Constraint relaxation** (Gauss–Seidel, quality-dependent iterations).
5. **Collisions** once per step, skipped for particles far from the body: torso and pelvis spheres, thigh, shin, upper-arm and forearm capsules, the sun disc as a one-sided disc, and the path surface. Corrections move the previous position too, so collisions don't inject velocity.

## 7. Hair

Each of the 26 locks becomes an 8-particle strand (`makeStrand`). The first two particles ride with the head. The rest are integrated with gravity and drag from the same air (perpendicular to each segment), kept inextensible, pulled toward the styled rest shape with a stiffness that falls from root to tip, and kept outside a scalp sphere. Each lock mesh is then reshaped every frame: its rings follow a Catmull-Rom spine through the particles, oriented by quaternions interpolated between the particles, and its normals are rotated with them, so no normal recomputation is needed. The crown cap stays rigid on the head.

## 8. Camera

Each angle (Side, Chase, Orbit, Low, Crane) defines a look target, an offset and a lens. Director plays a shot list with cuts, zoom moves, roll and per-shot depth of field.

On top of that, every frame:
- **Zoom** scales the offset distance, smoothed in log space, with a closest distance derived from the lens. The look target blends toward the head as you zoom in, and the camera rises as you zoom out.
- **Dolly zoom** widens the field of view while scaling the distance by tan(old fov / 2) ÷ tan(new fov / 2).
- **Position and target** glide toward their new values. Zoom and lens respond faster than angle changes.
- **Elevation** (tilt) and **azimuth** (360° circle and drag) are applied around Kreis after the smoothing, then the move-pad offsets in camera-relative right, up and forward axes.
- **Handheld, slow push and dutch tilt** are added last.
- **Depth of field** uses three.js's `EffectComposer` with `BokehPass`, focused on the head, with the aperture scaled to the focus distance. It loads on first use.

## 9. Quality and the frame loop

Each frame:
1. measure the raw frame time;
2. ease the speed toward the slider value;
3. advance the gait phase and scroll the world;
4. recycle chunks;
5. animate the dust puffs;
6. `pose`;
7. `updateCloth`, which also runs `hairTargets`, `hairStep` and `hairMesh`;
8. the camera rig;
9. lighting;
10. render;
11. `autoQuality`.

The quality presets set the pixel ratio, shadow map size, cloth step length and cap, cloth iterations, and how often the hair is reshaped. Auto drops a level when the smoothed frame time stays above about 21 ms, and raises one when frames stay under 17.5 ms with less than 7 ms of CPU work.

Settings are stored in `localStorage` (inside try/catch, so the page still works when storage is unavailable).
