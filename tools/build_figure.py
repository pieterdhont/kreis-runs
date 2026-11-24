"""Builds 'Kreis the Wanderer', an original Bauhaus-style figure, as a multicolor GLB (Y-up, metres)."""
import base64, os
import numpy as np
import trimesh
from trimesh.transformations import rotation_matrix, translation_matrix

RED, YELLOW, BLUE = "#D7261E", "#F2C200", "#1F4FA3"
BLACK, WHITE = "#161616", "#F4F1EA"

def hex_rgba(h):
    h = h.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)] + [1.0]

materials = {}
def mat(name, color, rough=0.55):
    if name not in materials:
        materials[name] = trimesh.visual.material.PBRMaterial(
            name=name, baseColorFactor=hex_rgba(color), metallicFactor=0.0, roughnessFactor=rough)
    return materials[name]

scene = trimesh.Scene()
def add(mesh, name, color, matname, rough=0.55):
    mesh.visual = trimesh.visual.TextureVisuals(material=mat(matname, color, rough))
    scene.add_geometry(mesh, node_name=name, geom_name=name)

def cyl_between(p0, p1, r, sections=64):
    """Cylinder with its axis running from p0 to p1."""
    p0, p1 = np.array(p0, float), np.array(p1, float)
    v = p1 - p0
    c = trimesh.creation.cylinder(radius=r, height=np.linalg.norm(v), sections=sections)
    z = np.array([0, 0, 1.0]); d = v / np.linalg.norm(v)
    axis = np.cross(z, d)
    if np.linalg.norm(axis) > 1e-9:
        ang = np.arccos(np.clip(z @ d, -1, 1))
        c.apply_transform(rotation_matrix(ang, axis))
    c.apply_translation((p0 + p1) / 2)
    return c

def sphere(c, r):
    s = trimesh.creation.icosphere(subdivisions=4, radius=r)
    s.apply_translation(c)
    return s

def box(c, ext):
    b = trimesh.creation.box(extents=ext)
    b.apply_translation(c)
    return b

# Base: black square plinth with a white inset square
add(box([0, -0.03, 0], [0.56, 0.06, 0.56]), "base", BLACK, "black")
add(box([0, 0.0015, 0], [0.44, 0.003, 0.44]), "base_inset", WHITE, "white")

# Feet (red half-blocks) and legs (blue cylinders)
for side, x in (("L", 0.085), ("R", -0.085)):
    add(box([x, 0.035, 0.025], [0.11, 0.064, 0.17]), f"foot_{side}", RED, "red")
    add(cyl_between([x, 0.06, 0], [x, 0.40, 0], 0.045), f"leg_{side}", BLUE, "blue")

# Hips (black bar) and torso (yellow cylinder)
add(box([0, 0.42, 0], [0.25, 0.06, 0.15]), "hips", BLACK, "black")
add(cyl_between([0, 0.45, 0], [0, 0.72, 0], 0.12), "torso", YELLOW, "yellow")
# Chest emblem: a small blue circle on the front of the torso
emb = trimesh.creation.cylinder(radius=0.045, height=0.01, sections=64)
emb.apply_translation([0, 0.62, 0.12])
add(emb, "chest_circle", BLUE, "blue")

# Arms in A-pose (about 35 degrees from vertical), black shoulder joints, white hands
for side, sx in (("L", 1), ("R", -1)):
    sh = np.array([sx * 0.15, 0.70, 0])
    ang = np.radians(35)
    hand = sh + 0.30 * np.array([sx * np.sin(ang), -np.cos(ang), 0])
    add(sphere(sh, 0.052), f"shoulder_{side}", BLACK, "black")
    add(cyl_between(sh, hand, 0.038), f"arm_{side}", BLUE, "blue")
    add(sphere(hand, 0.05), f"hand_{side}", WHITE, "white")

# Collar and head
add(cyl_between([0, 0.72, 0], [0, 0.755, 0], 0.085), "collar", BLACK, "black")
add(sphere([0, 0.885, 0], 0.13), "head", WHITE, "white", rough=0.4)
for side, x in (("L", 0.045), ("R", -0.045)):
    add(sphere([x, 0.895, 0.118], 0.019), f"eye_{side}", BLACK, "black")
# Brow: a thin red bar, the one straight line on the face
add(box([0, 0.94, 0.112], [0.12, 0.014, 0.02]), "brow", RED, "red")

# Cloak: a flat red triangle hung from the shoulders down the back
tri = np.array([(-0.25, 0.30), (0.25, 0.30), (0, 0.80)])
z0, z1 = -0.17, -0.142
verts = np.array([[x, y, z0] for x, y in tri] + [[x, y, z1] for x, y in tri])
faces = [[0, 2, 1], [3, 4, 5],                      # back, front
         [0, 1, 4], [0, 4, 3], [1, 2, 5], [1, 5, 4], [2, 0, 3], [2, 3, 5]]
cloak = trimesh.Trimesh(verts, faces, process=True)
cloak.fix_normals()
add(cloak, "cloak", RED, "red")

# Sun disc: a yellow circle behind the cloak, black rim, blue centre on its back
disc = trimesh.creation.cylinder(radius=0.23, height=0.024, sections=96)
disc.apply_translation([0, 0.66, -0.21])
add(disc, "sun_disc", YELLOW, "yellow")
rim = trimesh.creation.torus(major_radius=0.23, minor_radius=0.013, major_sections=96, minor_sections=24)
rim.apply_translation([0, 0.66, -0.21])
add(rim, "sun_rim", BLACK, "black")
dot = trimesh.creation.cylinder(radius=0.075, height=0.01, sections=64)
dot.apply_translation([0, 0.66, -0.226])
add(dot, "sun_centre", BLUE, "blue")

APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "app", "kreis-the-wanderer")
out = os.path.join(APP, "kreis_the_wanderer.glb")
scene.export(out)
b = scene.bounds
print("saved", out, "bounds", np.round(b, 3), "parts", len(scene.geometry))

# the viewer page loads the model inline from model.js
with open(out, "rb") as f:
    open(os.path.join(APP, "model.js"), "w").write('window.KREIS_GLB="' + base64.b64encode(f.read()).decode() + '";')
print("wrote model.js")
