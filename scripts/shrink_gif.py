"""Re-encode a GIF (e.g. from render_snapshots.py --movie gif) smaller: optional resize,
one shared adaptive palette, and frame differencing.

    uv run python scripts/shrink_gif.py IN.gif OUT.gif [--width 400] [--colors 64]
        [--hold-last 1.5]
"""

from __future__ import annotations

import argparse

from PIL import Image


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--width", type=int, help="resize to this width (default: keep)")
    ap.add_argument("--colors", type=int, default=64, help="palette size (default %(default)s)")
    ap.add_argument("--fps", type=float, help="frame rate (default: keep)")
    ap.add_argument("--hold-last", type=float, default=0.0, help="extra seconds on the last frame")
    args = ap.parse_args(argv)

    im = Image.open(args.src)
    ms = args.fps and 1000.0 / args.fps or im.info.get("duration", 100)
    frames = []
    for k in range(im.n_frames):
        im.seek(k)
        f = im.convert("RGB")
        if args.width and f.width != args.width:
            f = f.resize((args.width, round(f.height * args.width / f.width)), Image.LANCZOS)
        frames.append(f)
    # one palette from a sample of frames, so colours do not flicker between frames
    sample = Image.new("RGB", (frames[0].width, frames[0].height * 4))
    for i, k in enumerate(range(0, len(frames), max(1, len(frames) // 4))):
        if i < 4:
            sample.paste(frames[k], (0, frames[0].height * i))
    pal = sample.quantize(colors=args.colors, method=Image.Quantize.MEDIANCUT)
    out = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    durations = [round(ms)] * len(out)
    durations[-1] += round(1000 * args.hold_last)
    out[0].save(
        args.dst,
        save_all=True,
        append_images=out[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"{args.dst}: {len(out)} frames, {out[0].size[0]}x{out[0].size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
