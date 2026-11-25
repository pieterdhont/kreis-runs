# Changelog

Each entry is one commit. Kreis Runs was developed in quick iterations. Some early in-place versions of the page (the first landscape and the first articulated runner) were overwritten before they could be saved, so the history starts from the first preserved snapshot.

| # | Commit | What changed |
|---|---|---|
| 1 | Kreis the Wanderer | Original geometric Bauhaus figure built from primitive solids, multicolour GLB and rotating viewer |
| 2 | Running scene with flowing hair, zoom and cinematic cameras | Endless procedural Bauhaus landscape, articulated runner, day and dusk, faceted hair, zoom on every angle, Low and Crane angles, Director mode, depth of field, letterbox, handheld, slow push, dutch tilt, dolly zoom |
| 3 | Anime-Bauhaus redesign | Cel shading and ink outlines, anime face, flame crest, wrap top with crest, obi with tails, lined sleeves, hakama, tabi |
| 4 | Skinned limbs, keyframed gait, expressions, 360° camera | Continuous skinned arms, legs and hakama, keyframed running, blinking and effort expressions, split cape, sleeve ribbons, 360° circle and drag-to-orbit |
| 5 | Softer shading, gradients, flowing hair | Soft toon ramp, rim light, colour gradients, blush, hair that bends along its length, eased speed changes |
| 6 | Continuous skinned upper body | One skinned torso with spine and neck bones, slimmer silhouette, tapered hands |
| 7 | Single sculpted mesh on a 19-bone skeleton | Signed-distance sculpt, marching cubes, ~60k-triangle body with colours and skin weights; `tools/sculpt_kreis.py` |
| 8 | Physics-based running with planted feet | Velocity, cadence and contact/flight times from speed; locked stance feet; heel-to-toe roll; leg IK; spring-mass and ballistic hips; feet on the path surface |
| 9 | Reachable sprint gait, speed-adaptive motion, move pad | Reach-checked landing and push-off; strike, kick, knee drive, arms and lean scale with speed; hold-to-move camera pad and WASD/QE |
| 10 | Walk-to-sprint continuum with momentum | Walking with double support and vault; human-scaled gait timings; acceleration lean, landing jolt, pelvis and chest counter-rotation; speed in m/s |
| 11 | Speed up to 10 m/s | Elite-scaled cadence and contact times, forefoot landing, big toe-off, high heel recovery, wide arm swing, top-speed posture |
| 12 | Torso driven by the limbs | Chest follows the arms and pelvis follows the thighs, stance-side sway, spine flex and extension, shoulder girdle, head stabilisation, breathing |
| 13 | Simulated cloth | Verlet cape, obi tails and ribbons with aerodynamic drag, wake turbulence and body collisions |
| 14 | Faster cloth, adaptive quality | About 8× cheaper cloth step, capped substeps, Auto/High/Balanced/Fast quality |
| 15 | Physics hair strands | Every lock a strand held to its style, pushed by the same air, about half the previous hair cost |
| 16 | Documentation | README, usage guide, architecture notes, improvement ideas, render-check tool |
