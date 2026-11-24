"""Sculpts Kreis (original character) as one continuous surface with a signed-distance field,
then meshes, smooths, colours and skin-weights it for a 19-bone skeleton.
Coordinates: hips-local rest pose, metres, y up, z forward (face), x = character's left.
Output: kreis_body.js  (window.KREIS_BODY with base64 buffers)."""
import base64, json, math, os, sys
import numpy as np
from skimage import measure
import trimesh
import fast_simplification

VOX = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0035
TARGET_TRIS = int(sys.argv[2]) if len(sys.argv) > 2 else 60000

# ---------- skeleton rest positions (must match the page) ----------
SPREAD = 0.13
HIPX = 0.072
WAIST = np.array([0, 0.075, 0.0]); CHEST = np.array([0, 0.225, 0.0]); NECK = np.array([0, 0.385, 0.0])
HEAD_O = np.array([0, 0.427, 0.0])
def arm_frame(sx):
    sh = np.array([sx * 0.126, 0.363, 0.0])
    d = np.array([math.sin(sx * SPREAD), -math.cos(SPREAD), 0.0])
    return sh, d
def leg_frame(sx):
    hip = np.array([sx * HIPX, -0.03, 0.0])
    return hip, hip + [0, -0.34, 0], hip + [0, -0.67, 0]

# ---------- SDF primitives ----------
def ellipsoid(p, c, r):
    q = (p - c) / r
    k0 = np.linalg.norm(q, axis=1)
    k1 = np.linalg.norm(q / r, axis=1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)

def round_cone(p, a, b, r1, r2):
    a = np.asarray(a, float); b = np.asarray(b, float)
    ba = b - a; l2 = ba @ ba; rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
    pa = p - a; y = pa @ ba; z = y - l2
    xv = pa * l2 - np.outer(y, ba); x2 = np.einsum('ij,ij->i', xv, xv)
    y2 = y * y * l2; z2 = z * z * l2
    k = np.sign(rr) * rr * rr * x2
    d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
    d1 = np.sqrt(x2 + z2) * il2 - r2
    d2 = np.sqrt(x2 + y2) * il2 - r1
    return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))

def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0.0) / k
    return np.minimum(a, b) - h * h * k * 0.25

def band(p, cy, h, rx, rz, round_=0.006):
    """rounded elliptical band (the obi) centred at height cy"""
    q = p.copy(); q[:, 2] *= rx / rz
    rad = np.sqrt(q[:, 0] ** 2 + q[:, 2] ** 2) - (rx - round_)
    dy = np.abs(p[:, 1] - cy) - (h / 2 - round_)
    out = np.sqrt(np.maximum(rad, 0) ** 2 + np.maximum(dy, 0) ** 2) + np.minimum(np.maximum(rad, dy), 0)
    return out - round_

# ---------- the sculpt: each named part, how it blends ----------
def parts(p):
    P = {}
    # head: cranium, jaw and a small pointed chin
    P['cranium'] = ellipsoid(p, [0, 0.525, 0.0], [0.081, 0.085, 0.087])
    P['jaw'] = ellipsoid(p, [0, 0.476, 0.014], [0.056, 0.05, 0.06])
    P['chin'] = ellipsoid(p, [0, 0.449, 0.032], [0.021, 0.02, 0.024])
    P['neck'] = round_cone(p, [0, 0.37, -0.004], [0, 0.462, 0.006], 0.034, 0.028)
    # torso
    P['chest'] = ellipsoid(p, [0, 0.292, 0.006], [0.112, 0.084, 0.083])
    P['rib'] = ellipsoid(p, [0, 0.225, 0.0], [0.103, 0.075, 0.076])
    P['waist'] = ellipsoid(p, [0, 0.145, 0.0], [0.086, 0.07, 0.064])
    for s, sx in (('L', 1), ('R', -1)):
        sh, d = arm_frame(sx)
        P['trap' + s] = round_cone(p, [0, 0.385, -0.006], sh + [0, 0.012, -0.004], 0.03, 0.032)
        P['cap' + s] = ellipsoid(p, sh + [sx * -0.004, 0.006, 0.0], [0.05, 0.046, 0.046])
    P['pelvis'] = ellipsoid(p, [0, 0.0, 0.0], [0.112, 0.088, 0.088])
    P['obi'] = band(p, 0.056, 0.058, 0.112, 0.088)
    # arms: sleeve over the upper arm, bare blue elbow and forearm, tapered hand and thumb
    for s, sx in (('L', 1), ('R', -1)):
        sh, d = arm_frame(sx)
        P['sleeve' + s] = round_cone(p, sh + d * 0.0, sh + d * 0.15, 0.047, 0.05)
        P['upper' + s] = round_cone(p, sh + d * 0.1, sh + d * 0.2, 0.034, 0.03)
        P['fore' + s] = round_cone(p, sh + d * 0.2, sh + d * 0.385, 0.03, 0.019)
        wr = sh + d * 0.385
        P['hand' + s] = round_cone(p, wr + d * 0.012, wr + d * 0.062 + [0, 0, 0.004], 0.019, 0.022)
        P['thumb' + s] = round_cone(p, wr + d * 0.02 + [0, 0, 0.014], wr + d * 0.045 + [sx * -0.004, 0, 0.026], 0.009, 0.008)
    # legs: hakama trousers (thigh and flared lower), bare shin and ankle below the hem, shoe heel and toe
    for s, sx in (('L', 1), ('R', -1)):
        hip, kn, an = leg_frame(sx)
        P['thigh' + s] = round_cone(p, hip + [0, 0.02, 0], kn, 0.064, 0.058)
        hem_y = an[1] + 0.025
        lower = round_cone(p, kn, [an[0], hem_y, 0], 0.058, 0.068)
        P['lower' + s] = np.maximum(lower, hem_y - p[:, 1])       # flat-cut hem
        P['shin' + s] = round_cone(p, kn + [0, -0.18, 0], an, 0.03, 0.021)
        heel = ellipsoid(p, an + [0, -0.022, 0.012], [0.04, 0.032, 0.072])
        P['heel' + s] = np.maximum(heel, (an[1] - 0.038) - p[:, 1])
        toe = ellipsoid(p, an + [0, -0.026, 0.1], [0.036, 0.026, 0.06])
        P['toe' + s] = np.maximum(toe, (an[1] - 0.038) - p[:, 1])
    return P

def combine(P):
    head = smin(smin(P['cranium'], P['jaw'], 0.035), P['chin'], 0.015)
    torso = smin(smin(P['chest'], P['rib'], 0.04), P['waist'], 0.04)
    for s in 'LR':
        torso = smin(torso, P['trap' + s], 0.03)
        torso = smin(torso, P['cap' + s], 0.03)
    core = smin(torso, P['pelvis'], 0.04)
    core = np.minimum(core, P['obi'])
    core = smin(core, P['neck'], 0.03)
    core = smin(core, head, 0.025)
    for s in 'LR':
        arm = np.minimum(np.minimum(P['sleeve' + s], P['upper' + s]), P['fore' + s])
        arm = smin(arm, P['hand' + s], 0.012)
        arm = smin(arm, P['thumb' + s], 0.006)
        arm = smin(arm, P['cap' + s], 0.025)             # blend only at the shoulder
        core = np.minimum(core, arm)
        leg = smin(P['thigh' + s], P['lower' + s], 0.03)
        leg = np.minimum(leg, P['shin' + s])
        foot = smin(P['heel' + s], P['toe' + s], 0.012)
        leg = smin(leg, foot, 0.006)
        core = smin(core, np.maximum(leg, -1), 0.0001) if False else np.minimum(core, smin(leg, P['pelvis'], 0.035))
    return core

# ---------- evaluate on a grid in slabs, mesh it ----------
lo = np.array([-0.24, -0.76, -0.14]); hi = np.array([0.24, 0.63, 0.21])
nx, ny, nz = (np.ceil((hi - lo) / VOX).astype(int) + 1)
xs = lo[0] + np.arange(nx) * VOX; ys = lo[1] + np.arange(ny) * VOX; zs = lo[2] + np.arange(nz) * VOX
vol = np.empty((nx, ny, nz), np.float32)
X, Z = np.meshgrid(xs, zs, indexing='ij')
for j0 in range(0, ny, 24):
    j1 = min(ny, j0 + 24)
    Y = ys[j0:j1]
    pts = np.stack(np.broadcast_arrays(X[:, None, :], Y[None, :, None], Z[:, None, :]), -1).reshape(-1, 3)
    vol[:, j0:j1, :] = combine(parts(pts)).reshape(nx, j1 - j0, nz)
    print(f'slab {j1}/{ny}', end='\r', flush=True)
print()
verts, faces, _, _ = measure.marching_cubes(vol, 0.0, spacing=(VOX, VOX, VOX))
verts += lo
print('marching cubes:', len(verts), 'verts', len(faces), 'faces')
mesh = trimesh.Trimesh(verts, faces[:, ::-1], process=True)
mesh = max(mesh.split(only_watertight=False), key=lambda m: len(m.faces))   # drop stray specks
trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=12)
v2, f2 = fast_simplification.simplify(mesh.vertices.astype(np.float32), mesh.faces.astype(np.int64), target_reduction=max(0.0, 1 - TARGET_TRIS / len(mesh.faces)))
mesh = trimesh.Trimesh(v2, f2, process=True)
trimesh.smoothing.filter_taubin(mesh, lamb=0.5, nu=-0.53, iterations=4)
mesh.fix_normals()
V = mesh.vertices.astype(np.float64); F = mesh.faces.astype(np.int64)
print('final:', len(V), 'verts', len(F), 'faces', 'watertight', mesh.is_watertight)

# ---------- labels: which sculpt part each vertex belongs to ----------
P = parts(V)
names = list(P.keys())
D = np.stack([P[n] for n in names], 1)
lab = np.array(names)[np.argmin(D, 1)]

def smo(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)
def srgb(h):
    return np.array([(h >> 16) & 255, (h >> 8) & 255, h & 255], float)

WHITE, BLACK, RED = srgb(0xf4f1ea), srgb(0x161616), srgb(0xd7261e)
Y0, Y1 = srgb(0xe2a400), srgb(0xffd94a)
B0, B1 = srgb(0x173f8f), srgb(0x2f63c6)
col = np.zeros((len(V), 3))
BONES = ['hips', 'waist', 'chest', 'neck', 'head', 'shL', 'elL', 'wrL', 'shR', 'elR', 'wrR', 'thL', 'knL', 'anL', 'toeL', 'thR', 'knR', 'anR', 'toeR']
BI = {n: i for i, n in enumerate(BONES)}
W = np.zeros((len(V), len(BONES)))

def spine_w(i, y):
    if y < 0.25:
        w = smo(0.125, 0.255, y); W[i, BI['waist']] += 1 - w; W[i, BI['chest']] += w
    else:
        w = smo(0.372, 0.41, y); W[i, BI['chest']] += 1 - w; W[i, BI['neck']] += w

for i, (p, L) in enumerate(zip(V, lab)):
    x, y, z = p
    side = L[-1] if L[-1] in 'LR' else ('L' if x >= 0 else 'R')
    sx = 1 if side == 'L' else -1
    base = L[:-1] if L[-1] in 'LR' and L not in ('cranium',) else L
    core = base in ('cranium', 'jaw', 'chin', 'neck', 'chest', 'rib', 'waist', 'trap', 'cap', 'pelvis', 'obi')
    if core:
        # colour from smooth bands (no per-vertex hard switches): blue trousers, black obi with red stripe,
        # yellow top, black collar ring, white neck and head
        rxz = math.hypot(x, z - 0.002)
        c = Y0 + (Y1 - Y0) * smo(0.1, 0.33, y)
        c = B0 + (B1 - B0) * smo(-0.09, 0.03, y) + (c - (B0 + (B1 - B0) * smo(-0.09, 0.03, y))) * smo(0.024, 0.034, y)
        ob = smo(0.024, 0.032, y) * (1 - smo(0.08, 0.088, y))
        c = c + (BLACK - c) * ob
        st = smo(0.0485, 0.0515, y) * (1 - smo(0.0575, 0.0605, y))
        c = c + (RED - c) * st
        ring = 1 - smo(0.05, 0.064, rxz)
        wn = smo(0.386, 0.393, y) * (1 - smo(0.05, 0.062, rxz))
        if base in ('cranium', 'jaw', 'chin'): wn = 1.0
        c = c + (WHITE - c) * wn
        col[i] = c
    if base in ('cranium', 'jaw', 'chin'):
        w = smo(0.43, 0.47, y); W[i, BI['neck']] += 1 - w; W[i, BI['head']] += w
    elif base == 'neck':
        if y < 0.405:
            w = smo(0.37, 0.405, y); W[i, BI['chest']] += 1 - w; W[i, BI['neck']] += w
        else:
            w = smo(0.43, 0.47, y); W[i, BI['neck']] += 1 - w; W[i, BI['head']] += w
    elif base in ('chest', 'rib', 'waist', 'trap', 'cap'):
        if base == 'cap':
            sh, d = arm_frame(sx); s_ = (p - sh) @ d; a = smo(-0.025, 0.035, s_)
            spine_w(i, y); W[i] *= (1 - a); W[i, BI['sh' + side]] += a
        else:
            spine_w(i, y)
    elif base in ('pelvis',):
        wz = smo(0.03, 0.09, y); W[i, BI['hips']] += 1 - wz; W[i, BI['waist']] += wz
        dd = -(y + 0.03); wt = smo(-0.01, 0.06, dd) * smo(0.0, 0.05, abs(x))
        if wt > 0: W[i] *= (1 - wt); W[i, BI['th' + side]] += wt
    elif base == 'obi':
        wz = smo(0.03, 0.09, y); W[i, BI['hips']] += 1 - wz; W[i, BI['waist']] += wz
    elif base in ('sleeve', 'upper', 'fore', 'hand', 'thumb'):
        sh, d = arm_frame(sx); s = (p - sh) @ d
        if base == 'sleeve':
            cy_ = Y0 + (Y1 - Y0) * (1 - smo(0.0, 0.15, s) * 0.7); col[i] = cy_
        elif base in ('upper', 'fore'):
            col[i] = B1 + (B0 - B1) * smo(0.1, 0.385, s)
        else:
            col[i] = WHITE
        if s < 0.1:
            a = smo(-0.02, 0.035, s); spine_w(i, y); W[i] *= (1 - a); W[i, BI['sh' + side]] += a
        elif s < 0.3:
            a = smo(0.17, 0.23, s); W[i, BI['sh' + side]] += 1 - a; W[i, BI['el' + side]] += a
        else:
            a = smo(0.362, 0.392, s); W[i, BI['el' + side]] += 1 - a; W[i, BI['wr' + side]] += a
    elif base in ('thigh', 'lower', 'shin', 'heel', 'toe'):
        hip, kn, an = leg_frame(sx); dd = -(y - hip[1])
        if base in ('thigh', 'lower'):
            hem_y = an[1] + 0.025
            cb_ = B1 + (B0 - B1) * smo(0.0, 0.645, dd); col[i] = cb_
        elif base == 'shin':
            col[i] = B0 + (WHITE - B0) * (1 - smo(an[1] + 0.024, an[1] + 0.032, y))
        else:
            col[i] = RED
        if base == 'heel':
            W[i, BI['an' + side]] += 1
        elif base == 'toe':
            a = smo(0.062, 0.088, z); W[i, BI['an' + side]] += 1 - a; W[i, BI['toe' + side]] += a
        elif dd < 0.06:
            a = smo(-0.05, 0.05, dd); W[i, BI['hips']] += 1 - a; W[i, BI['th' + side]] += a
        elif dd < 0.5:
            a = smo(0.29, 0.39, dd); W[i, BI['th' + side]] += 1 - a; W[i, BI['kn' + side]] += a
        else:
            a = smo(0.635, 0.69, dd); W[i, BI['kn' + side]] += 1 - a; W[i, BI['an' + side]] += a
    else:
        col[i] = WHITE; W[i, BI['chest']] += 1

# keep the 4 strongest influences, normalise, quantise
order = np.argsort(-W, 1)[:, :4]
wt = np.take_along_axis(W, order, 1)
wt = wt / np.maximum(wt.sum(1, keepdims=True), 1e-9)
wq = np.round(wt * 255).astype(np.int32)
wq[:, 0] += 255 - wq.sum(1)
si = order.astype(np.uint8); sw = np.clip(wq, 0, 255).astype(np.uint8)

# probe sub-meshes for projecting the face, hair roots and chest details
cent = V[F].mean(1)
headF = F[(cent[:, 1] > 0.415)]
torsoF = F[(cent[:, 1] > 0.08) & (cent[:, 1] < 0.44) & (np.abs(cent[:, 0]) < 0.14)]

b64 = lambda a: base64.b64encode(np.ascontiguousarray(a).tobytes()).decode()
idx_t = np.uint16 if len(V) < 65536 else np.uint32
out = {'n': int(len(V)), 'idxType': 'u16' if idx_t == np.uint16 else 'u32', 'bones': BONES,
       'pos': b64(V.astype(np.float32)), 'col': b64(np.clip(col, 0, 255).astype(np.uint8)),
       'si': b64(si), 'sw': b64(sw), 'idx': b64(F.astype(idx_t)),
       'headIdx': b64(headF.astype(idx_t)), 'torsoIdx': b64(torsoF.astype(idx_t))}
js = 'window.KREIS_BODY=' + json.dumps(out) + ';'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'app', 'kreis-runs', 'kreis_body.js')
open(OUT, 'w').write(js)
mesh.visual.vertex_colors = np.c_[np.clip(col, 0, 255), np.full(len(V), 255)].astype(np.uint8)
mesh.export('kreis_body_preview.glb')   # vertex-coloured preview, written to the current folder
print('labels:', {n: int((lab == n).sum()) for n in names if (lab == n).sum()})
print('wrote kreis_body.js', round(len(js) / 1e6, 2), 'MB')
