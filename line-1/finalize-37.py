"""Blend this round's generated pigment into vacant rock and preserve old pixels."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def disc(x, y, cx, cy, rx, ry):
    d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
    return max(0.0, min(1.0, (1.0 - d) * 5.0))


def line(x, y, ax, ay, bx, by, radius):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    distance = ((x - ax - t * dx) ** 2 + (y - ay - t * dy) ** 2) ** .5
    return max(0.0, min(1.0, (radius - distance) / 2.0))


def main():
    png = load('png_helpers', ROOT / 'line-1/finalize-35.py')
    thumb = load('thumbnail', ROOT / 'gathering/make_thumbnail.py')
    wall = ROOT / 'artifacts/line-1/wall.png'
    output = ROOT / 'artifacts/line-1/wall-v18.png'
    original, generated = wall.read_bytes(), output.read_bytes()
    digest = lambda data: hashlib.sha256(data).hexdigest()
    previous = json.loads((ROOT / 'dist/line-1/36.json').read_text())
    assert digest(original) == previous['image'].rsplit('/', 1)[1]
    width, height, channels, old_rows = png.decode_png(original)
    gw, gh, gc, new_rows = png.decode_png(generated)
    assert (width, height, channels) == (gw, gh, gc) == (1254, 1254, 3)
    left, top, right, bottom = 361, 407, 471, 505
    changed = 0
    for y in range(top, bottom):
        for x in range(left, right):
            shape = max(
                disc(x, y, 380, 485, 16, 16),
                disc(x, y, 414, 460, 20, 17),
                disc(x, y, 451, 427, 18, 17),
                line(x, y, 391, 478, 401, 469, 5),
                line(x, y, 427, 450, 439, 438, 5))
            if not shape:
                continue
            p = x * 3
            old, painted = old_rows[y][p:p+3], new_rows[y][p:p+3]
            alpha = .82 * shape
            blended = bytes(round(old[i] * (1 - alpha) + painted[i] * alpha)
                            for i in range(3))
            if blended != old:
                old_rows[y][p:p+3] = blended
                changed += 1
    assert changed > 700
    final = png.encode_rgb(old_rows, width, height)
    fw, fh, fc, final_rows = png.decode_png(final)
    assert (fw, fh, fc) == (1254, 1254, 3)
    jpeg = thumb.jpeg(thumb.resize(width, height, final_rows))
    assert len(jpeg) < 100000
    _, _, _, before = png.decode_png(original)
    outside = 0
    actual = 0
    for y in range(height):
        for x in range(width):
            p = x * 3
            if before[y][p:p+3] != final_rows[y][p:p+3]:
                actual += 1
                if not (left <= x < right and top <= y < bottom):
                    outside += 1
    assert actual == changed and outside == 0
    record_path = ROOT / 'dist/line-1/37.json'
    jpeg_path = ROOT / 'dist/line-1/37.jpg'
    assert not record_path.exists() and not jpeg_path.exists()
    meaning = 'Three ascending stones trace saved ZTO observations through time.'
    record = {
        'name': 'Stones in Time',
        'image': 'https://api.imd.fun/artifacts/' + digest(final),
        'attributes': [{'trait_type': key, 'value': value} for key, value in (
            ('Cave', 'Base'), ('Wall', 'Line 1'), ('Number', 37),
            ('Left behind', 'snapshot-timeline'), ('Meaning', meaning),
            ('One thing', 'portable live Ethereum state snapshots'))],
    }
    output.write_bytes(final)
    wall.write_bytes(final)
    jpeg_path.write_bytes(jpeg)
    record_path.write_text(json.dumps(record, indent=2) + '\n')
    review = {
        'source_record': 36, 'record_number': 37,
        'source_sha256': digest(original), 'generated_sha256': digest(generated),
        'wall_sha256': digest(final), 'png_dimensions': [1254, 1254],
        'png_format': '8-bit RGB PNG', 'png_bytes': len(final),
        'jpeg_dimensions': [512, 512], 'jpeg_format': 'baseline JPEG',
        'jpeg_bytes': len(jpeg), 'addition_rectangle': [left, top, right-left, bottom-top],
        'changed_pixels': changed, 'changed_pixels_outside_rectangle': outside,
        'new_hands_or_stencils': 0, 'unmet_visual_requirements': [],
        'visual_limitations': ['Inherited rock has a photographic appearance and is preserved.'],
        'visual_review': 'Pending inspection of the final PNG and JPEG.'}
    (ROOT / 'line-1/wall-review-37.json').write_text(json.dumps(review, indent=2) + '\n')
    print(json.dumps(review, indent=2))


if __name__ == '__main__':
    main()
