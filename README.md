# Kreis Runs

Kreis is an original character: a cel-shaded, anime-meets-Bauhaus runner with a flame-coloured crest, a yellow wrap top, a black obi, blue hakama, a red split cape and a sun disc on his back. **Kreis Runs** is a single-page Three.js app in which he runs, physically simulated, through an endless procedurally generated Bauhaus landscape.

- **One sculpted body on a 19-bone skeleton.** The body is generated from a signed-distance sculpt (`tools/sculpt_kreis.py`) and skinned to hips, spine, neck, head, arms, legs and toes.
- **Physically based locomotion from 0.8 to 10 m/s.** He walks, jogs, runs and sprints, with gait timings scaled from human data, planted feet with heel-to-toe roll, two-bone leg IK, a spring-mass bounce and ballistic flight, momentum lean and landing jolts.
- **Simulated cloth and hair.** The cape, obi tails and sleeve ribbons are Verlet cloth, and each hair lock is a particle strand. Both are pushed by air moving at his running speed, with turbulence in his wake, and collide with his body.
- **A full camera rig.** Six angles including an automatic Director mode, zoom on every angle, a 360° circle, drag-to-orbit, a hold-to-move pad, depth of field, letterbox, handheld, slow push, dutch tilt and dolly zoom.
- **Adaptive quality.** Auto lowers or raises resolution, shadow detail and simulation steps to keep the frame rate smooth.

The repository also contains **Kreis the Wanderer**, the original geometric Bauhaus figure Kreis started as, with a rotating viewer and a downloadable GLB.

## Quick start

Open `app/kreis-runs/index.html` in a current desktop browser (Chrome, Edge, Firefox or Safari). Three.js r160 loads from the jsDelivr CDN, so the page needs an internet connection.

If your browser blocks pages opened straight from disk, serve the folder instead:

```bash
cd app/kreis-runs
python -m http.server 8000
# then open http://localhost:8000
```

The Wanderer viewer works the same way from `app/kreis-the-wanderer/`.

## Repository layout

| Path | What it is |
|---|---|
| `app/kreis-runs/index.html` | The whole app: landscape, character rig, gait, cloth and hair simulation, cameras, UI |
| `app/kreis-runs/kreis_body.js` | The sculpted body mesh (positions, colours, skin weights) as base64 buffers |
| `app/kreis-the-wanderer/` | The geometric figure viewer, its inline model and the GLB file |
| `tools/sculpt_kreis.py` | Regenerates `kreis_body.js` from the signed-distance sculpt |
| `tools/build_figure.py` | Regenerates the Wanderer GLB and `model.js` |
| `tools/render-check.js` | Headless screenshots of the app at several angles and speeds, for visual review |
| `docs/USAGE.md` | How to use the app: every control, shortcut and tip |
| `docs/ARCHITECTURE.md` | How it works: rendering, sculpt pipeline, rig, gait model, cloth and hair solvers, cameras, quality |
| `docs/IMPROVEMENTS.md` | Possible next steps and known limitations |
| `CHANGELOG.md` | The iteration history, one entry per commit |

## Regenerating assets

```bash
pip install numpy scikit-image trimesh fast-simplification
python tools/sculpt_kreis.py 0.0035 60000   # voxel size (m), target triangles -> app/kreis-runs/kreis_body.js
python tools/build_figure.py                # -> app/kreis-the-wanderer/kreis_the_wanderer.glb and model.js
```

## Credits

The character, landscape and code are original. The app uses [three.js](https://threejs.org) r160 (MIT licence) from a CDN, and the Jost typeface from Google Fonts.

No licence has been chosen for this repository yet, so all rights are reserved by default. Add a `LICENSE` file if you want others to reuse it.
