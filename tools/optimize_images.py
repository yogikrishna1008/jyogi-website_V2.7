#!/usr/bin/env python3
"""
Jyogi Image Optimizer
Compresses and resizes images for web deployment.
Outputs: WebP + AVIF + JPG fallback at multiple sizes.

Usage:
  python3 tools/optimize_images.py                    # optimize everything in image/
  python3 tools/optimize_images.py image/moonstone_pearl.jpg
  python3 tools/optimize_images.py image/ --sizes 160,640
  python3 tools/optimize_images.py image/ --out image/opt --quality 82
"""

import os, sys, argparse, json, time
from pathlib import Path

try:
    from PIL import Image, ImageOps
    Image.MAX_IMAGE_PIXELS = None  # allow large images
except ImportError:
    sys.exit("Pillow not found. Run: pip3 install Pillow")

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_SIZES   = [160, 640, 1152]   # widths in pixels
DEFAULT_QUALITY = 82                  # JPEG / WebP quality (1-95)
DEFAULT_AVIF_Q  = 60                  # AVIF quality (0-100, lower = smaller)
INPUT_DIR       = "image"
OUTPUT_DIR      = "image/opt"
EXTS            = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}
SKIP_PREFIX     = ("crystal-placeholder",)   # already optimised placeholders

# ── Colours for terminal output ───────────────────────────────────────────────
G = "\033[32m"; Y = "\033[33m"; R = "\033[31m"; C = "\033[36m"; X = "\033[0m"

def human(n):
    """Bytes → human-readable string."""
    for u in ("B","KB","MB","GB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} GB"

def pct_saved(orig, new):
    if orig == 0: return 0
    return int(100 * (orig - new) / orig)

def resize_image(img, width):
    """Return a copy of img resized to `width` px, preserving aspect ratio."""
    if img.width <= width:
        return img.copy()
    ratio  = width / img.width
    height = max(1, int(img.height * ratio))
    return img.resize((width, height), Image.LANCZOS)

def save_webp(img, path, quality):
    img.save(path, "WEBP", quality=quality, method=6)

def save_avif(img, path, quality):
    # Pillow 10+ supports AVIF via pillow-avif-plugin or built-in
    try:
        img.save(path, "AVIF", quality=quality)
    except Exception:
        # Fallback: save as WebP with .avif extension note
        path = Path(str(path).replace(".avif", "-fb.webp"))
        img.save(path, "WEBP", quality=quality)

def save_jpg(img, path, quality):
    rgb = img.convert("RGB")
    rgb.save(path, "JPEG", quality=quality, optimize=True, progressive=True)

def optimize_file(src: Path, out_dir: Path, sizes, quality, avif_q, manifest):
    stem = src.stem
    if any(stem.startswith(p) for p in SKIP_PREFIX):
        return

    try:
        img = Image.open(src)
        img = ImageOps.exif_transpose(img)   # auto-rotate
        if img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGBA" if img.mode == "P" else "RGB")
    except Exception as e:
        print(f"  {R}SKIP{X} {src.name}: {e}")
        return

    orig_size = src.stat().st_size
    saved_total = 0
    files_written = []

    processed_widths = set()
    for w in sizes:
        actual_w = min(w, img.width)   # never upscale
        if actual_w in processed_widths:
            continue                    # skip duplicate (e.g. 640+1152 both → 900px original)
        processed_widths.add(actual_w)

        resized = resize_image(img, actual_w)
        base    = out_dir / f"{stem}-{w}"   # keep requested size in filename for consistency

        # WebP
        wp = base.with_suffix(".webp")
        save_webp(resized, wp, quality)
        files_written.append(str(wp.name))

        # AVIF (640+ only — tiny AVIF not worth the encode time)
        if actual_w >= 640:
            av = base.with_suffix(".avif")
            save_avif(resized, av, avif_q)
            files_written.append(str(av.name))

        # JPG fallback
        jf = base.with_suffix(".jpg")
        save_jpg(resized, jf, quality)
        files_written.append(str(jf.name))

    # "Per-request saving": compare original vs what the browser downloads for 640px WebP
    best_file = f"{stem}-640.webp"
    best_path = out_dir / best_file
    if not best_path.exists():
        # fallback to the smallest WebP generated
        webps = [(out_dir/f).stat().st_size for f in files_written if f.endswith(".webp") and (out_dir/f).exists()]
        per_req_size = min(webps) if webps else orig_size
    else:
        per_req_size = best_path.stat().st_size
    saving = pct_saved(orig_size, per_req_size)

    manifest[stem] = {
        "source": str(src),
        "sizes":  sizes,
        "files":  files_written,
        "original_bytes": orig_size,
        "per_request_bytes": per_req_size,
        "saving_pct": saving,
    }

    print(f"  {G}✓{X} {src.name:<45} {human(orig_size):>8} → {human(per_req_size):>8} (640px WebP)  {Y}{saving}% saved{X}")

def run(args):
    sizes   = sorted(int(s) for s in args.sizes.split(","))
    quality = args.quality
    avif_q  = args.avif_quality
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect source files
    src_path = Path(args.input)
    if src_path.is_file():
        sources = [src_path]
    elif src_path.is_dir():
        sources = sorted(
            f for f in src_path.iterdir()
            if f.is_file() and f.suffix.lower() in EXTS and f.parent.name != "opt"
        )
    else:
        sys.exit(f"Input not found: {args.input}")

    if not sources:
        print(f"{Y}No images found in {args.input}{X}")
        return

    print(f"\n{C}Jyogi Image Optimizer{X}")
    print(f"  Input   : {src_path}")
    print(f"  Output  : {out_dir}")
    print(f"  Sizes   : {sizes}px wide")
    print(f"  Quality : WebP/JPG={quality}  AVIF={avif_q}")
    print(f"  Images  : {len(sources)} files\n")

    manifest = {}
    t0 = time.time()

    for src in sources:
        optimize_file(src, out_dir, sizes, quality, avif_q, manifest)

    elapsed = time.time() - t0

    # Write manifest
    mf = out_dir / "_manifest.json"
    existing = {}
    if mf.exists():
        try:
            existing = json.loads(mf.read_text())
        except Exception:
            pass
    existing.update(manifest)
    mf.write_text(json.dumps(existing, indent=2))

    # Summary
    total_orig = sum(m["original_bytes"]     for m in manifest.values())
    total_new  = sum(m["per_request_bytes"] for m in manifest.values())
    print(f"\n{C}{'─'*60}{X}")
    print(f"  Processed : {len(manifest)} image(s) in {elapsed:.1f}s")
    print(f"  Before    : {human(total_orig)}")
    print(f"  After     : {human(total_new)}")
    print(f"  Saved     : {G}{human(total_orig - total_new)} ({pct_saved(total_orig, total_new)}%){X}")
    print(f"  Manifest  : {mf}\n")

def main():
    p = argparse.ArgumentParser(description="Optimize images for jyogi.in web deployment")
    p.add_argument("input",         nargs="?", default=INPUT_DIR,   help=f"File or directory (default: {INPUT_DIR})")
    p.add_argument("--out",         default=OUTPUT_DIR,              help=f"Output directory (default: {OUTPUT_DIR})")
    p.add_argument("--sizes",       default=",".join(str(s) for s in DEFAULT_SIZES), help="Comma-separated widths e.g. 160,640,1152")
    p.add_argument("--quality",     type=int, default=DEFAULT_QUALITY, help="WebP/JPG quality 1-95 (default 82)")
    p.add_argument("--avif-quality",type=int, default=DEFAULT_AVIF_Q,  help="AVIF quality 0-100 (default 60)")
    args = p.parse_args()
    run(args)

if __name__ == "__main__":
    main()
