# Possible improvements

Ideas for where Kreis Runs could go next, grouped by area, with a note on how each could be approached. The known limitations come first.

## Known limitations

- **Hakama and sleeves don't flap.** They are part of the skinned body, so they bend with the legs and arms but don't respond to wind. The cape, obi tails, ribbons and hair are simulated.
- **No self-collision.** The cape can fold through itself and hair locks can pass through each other. It's rarely visible at normal zoom.
- **Collision shapes are approximate.** Spheres and capsules stand in for the body, so cloth can sit slightly off the surface or graze into the sleeves at extreme poses.
- **Push-off at the reach limit.** At the very top of the speed range the rear foot can leave the ground a fraction early when the stance is longer than the leg can cover.
- **Straight, flat path only.** No turns, slopes, steps or uneven ground.
- **No sound.**
- **Visual checks were done on still frames.** The motion was reviewed frame by frame in headless renders, not in long live sessions on many devices.

## Character and animation

- **Simulate the hakama and sleeves.** Cut them from the body sculpt into separate cloth meshes driven by the leg and arm bones (pinned at the waist and shoulders), or run a cheaper "skinned cloth" in which each vertex springs toward its skinned position.
- **Turning and curves.** Let the path bend. Banking, a shorter inside stride and a twist into the turn would follow from the same gait model.
- **Terrain.** Slopes and steps: raise each foot target to the ground height under it and tilt the stance. The IK and reach check already allow per-foot targets.
- **Starts, stops and jumps.** Proper acceleration phases (deep lean, short quick steps), a stop with a braking step, and a jump over arches using a ballistic arc for the whole body.
- **Facial animation.** Replace the flat face shapes with blend shapes on the sculpt, so cheeks, mouth and brows deform with effort, and add eye tracking toward the camera.
- **Sculpt detail.** Fingers, hakama pleats as real folds, sleeve folds at the elbow, and a more defined jaw and cheekbones. All are possible in the signed-distance sculpt.
- **Better skin weights.** Use heat-diffusion or geodesic weights instead of the per-region rules, for smoother shoulders and hips at extreme poses.
- **Walk-to-run hysteresis.** People switch to running at a higher speed than they switch back. Add hysteresis around 1.6 m/s.

## Cloth and hair

- **Run the solvers on the GPU.** Moving cloth and hair to WebGPU compute shaders (or WebGL transform feedback) would allow denser cloth, self-collision and more hair strands at the same frame rate.
- **Tether constraints** from the pins to each particle, so the cape can't overstretch in whip-like gusts.
- **Self-collision** with a spatial hash between cape particles, and capsule–capsule tests between hair strands.
- **Hair clumps and strands.** Add thin secondary strands driven by the main locks for a richer silhouette.
- **Wind.** An optional ambient-wind control (direction and strength) and gust events visible in the landscape (moving grass, swaying trees).

## Rendering and performance

- **Motion blur at sprint speed.** A per-object velocity buffer, or a cheap blur on the landscape only.
- **Landscape level of detail.** Pool meshes when chunks are rebuilt and merge static geometry per chunk into one draw call per material.
- **Instancing** for repeated trees, poles and dashes.
- **Shadow cascades** for wide shots, and contact shadows under the feet.
- **Mobile tuning.** A lower default pixel ratio on phones, a touch-first control layout, and a pause when the tab is hidden.
- **Profiling overlay.** A hidden toggle to show frame time, simulation time and the current quality level.

## Camera

- **Free-fly mode** with mouse look for full manual control.
- **Saved shots.** Store camera positions and replay them, or build a custom Director sequence.
- **Video capture.** Record a clip with `MediaRecorder` from the canvas. Downloads need care because the published page runs in a sandboxed frame.

## Landscape

- **Biomes along the run.** Gradually shift palettes and props (city, park, desert of shapes, night with lit windows).
- **Interaction.** Puffs of dust at colour fields, arches that ring when he passes, birds taking off.
- **Weather.** Rain with wet shading, snow, or wind-blown leaves that also push the cloth.

## Code and tooling

- **Split the single file into modules** (landscape, rig, gait, cloth, hair, camera, UI) with a small build or plain ES-module imports. The single file is about 1,200 dense lines.
- **Tests for the maths.** Unit tests for `gaitParams` (reach always satisfied, durations positive), `footState` (stance foot speed equals world speed) and the IK (the ankle reaches its target).
- **Automated visual checks.** Run `tools/render-check.js` in CI and compare screenshots against reference images.
- **Animated GLB export.** Bake the gait into keyframes and export the skinned body with animation, for use in Blender or game engines.
- **A licence.** Choose and add one if the project is to be shared.
