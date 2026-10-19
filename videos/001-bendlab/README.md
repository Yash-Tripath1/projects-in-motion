# 001 — BendLab

Part of [**ManimGX Videos**](../../README.md) — one folder per film, video + code together.

**Can a bending sunflower reveal the numbers behind its bend?**

A 60-second [ManimGX](https://github.com/academa-labs/manimgx) film about
[**BendLab**](https://github.com/Yash-Tripath1/Bendlab) —
*Parameter identifiability in a minimal model of phototropic stem bending*,
by **Anadi Tripathi** (project lead) with **Umaid**.

▶️ **Watch: [`BendLab_slow_0.5x.mp4`](BendLab_slow_0.5x.mp4)** — the readable cut:
120.3 s (exactly half speed), 1920×1080, 60 fps.
The original 60.15 s render is [`BendLab.mp4`](BendLab.mp4); both are the
same film, frame for frame — the slow cut only stretches the timestamps
(FFmpeg `setpts=2.0*PTS`, with the final end-card hold padded back in).
On GitHub, click a file and press play. Times in the table below are for
the original cut; double them for the slow cut.

## The story in 8 scenes

| Time | Scene | What you see |
|---|---|---|
| 0:00 | **The bend** | A sunflower bends toward the light: θ = 0° → overshoot at 57° (13 h) → settle near 39° (23 h), using plant ZT0-1's measured angles. |
| 0:09 | **A deliberately tiny model** | `τ·dr/dt = k·sin(φ−θ) − r`, `dθ/dt = clip(r, −r_max, +r_max)` — and its four parameters: gain `k`, sensing lag `τ`, bend-rate cap `r_max`, light angle `φ₀`. |
| 0:15 | **Forwards vs backwards** | Simulating a curve from known parameters is easy. A real plant hands you only the curve. BendLab is about the way back. |
| 0:21 | **Real sunflowers** | Measured ZT0-1 points, then BendLab's fitted curve through them. Across all 48 plants: **median error 1.80° vs plant-to-plant spread 8.58°** (ratio 0.21). |
| 0:29 | **The invisible speed limit** | ZT0-1's bend rate peaks at **6.5 °/h**, far below its fitted cap of **43.9 °/h**. Delete the cap and the fit is *identical* — RMSE 1.894° both ways. `r_max` is exactly unidentifiable from this curve. |
| 0:37 | **10,000 plants** | Six behaviour clusters still contain **25–50%** of every parameter's range (largest cluster: 2,859 plants). Weighting by 44 clean real-plant fits shrinks that to **4–14%** — better, not solved. |
| 0:47 | **Change the light…** | Clusters measured under moving light don't match the static-light ones: **ARI 0.442**, below BendLab's pre-specified 0.50 persistence line. And honestly: a 45° step at hour 8 did *not* improve recovery under the first metric. |
| 0:54 | **The lesson** | *A good fit is not a unique explanation.* |

## Re-render it

Python 3.13 or 3.14. No LaTeX, ffmpeg or GPU needed
(Linux wheels bundle CPU rendering).

From this folder (`videos/001-bendlab/`):

```bash
pip install -r ../../requirements.txt   # shared repo requirements (manimgx)
manimgx inspect scene.py       # storyboard + layout checks — "no problems in 65 samples"
manimgx render scene.py        # -> BendLab.mp4 (1080p60)

# faster draft while editing:
manimgx render scene.py -r 1280x720 --fps 30
```

Storyboard PNGs from `inspect` are generated previews and are
git-ignored at the repository root; this folder keeps only `poster.jpg`.

This copy was rendered headlessly on CPU (ManimGX 0.1.1, Python 3.13)
in 261 s; on a GPU it is far quicker.

`scene.py` is organised as one method per scene (`opener`,
`model_machine`, `forward_inverse`, `real_fit`, `invisible_cap`,
`population`, `protocols`, `outro`), registered with
`self.next_section(...)` in `construct()` — so `manimgx present scene.py`
also works as slides.

## Where every number comes from

All quantities are from the BendLab repository (snapshot 19 Oct 2026) —
nothing was invented for the film:

| Film claim | BendLab source |
|---|---|
| Model equations, 1-minute Euler steps | `sim.py`, `PROBLEM_STATEMENT.md` §2 |
| ZT0-1 fit: k = 23.03 °/h, τ = 6.77 h, r_max = 43.91 °/h, φ₀ = 41.32°, RMSE 1.894° | `results/fit_fig1c.csv` |
| Measured ZT0-1 stem angles (dots) | `data/real/stem_angles_plosbiol2023_s13.xlsx`, sheet Fig1C — hourly points are embedded in `scene.py`, and the full half-hourly series + fit is in [`data/zt0_1_measured_and_fit.csv`](data/zt0_1_measured_and_fit.csv) |
| Peak realised bend rate 6.53 °/h at 5.7 h | recomputed here with BendLab's integrator at the fitted parameters; agrees with the exact-degeneracy result in `docs/RESULTS_ROUND0.md` §2.2 (RMSE 1.894° with and without the cap) |
| 48 plants, median RMSE 1.80°, spread 8.58°, ratio 0.21 | README “Model fitting (H5)” |
| 10,000 plants, 6 clusters, largest 2,859; retention 25/36/50/25%, weighted 9/4/14/12% | README (H1, weighted population), `docs/RESULTS_ROUND0.md` §3 |
| ARI 0.442 vs 0.50 threshold; 45° step at 8 h not supported (H2) | README principal findings, `PROBLEM_STATEMENT.md` H2/H4 |

**What is schematic, honestly:** the sunflower drawing and its stem
outline illustrate the stem *angle*; the model's outputs are angle and
bend rate, as in BendLab's own visual simulator. The cluster scenes use
48 and 36 dots to stand for the 10,000-plant populations — the
statistics printed on screen are the real ones. The film also keeps
BendLab's own scope note: this is a minimal phenomenological model,
not a model of auxin transport or differential growth.

## Credits & licences

- **BendLab:** Anadi Tripathi ([@Yash-Tripath1](https://github.com/Yash-Tripath1))
  with Umaid — [github.com/Yash-Tripath1/Bendlab](https://github.com/Yash-Tripath1/Bendlab)
  (MIT). Live site: <https://yash-tripath1.github.io/Bendlab/>
- **Measured data:** Brooks, Atamian & Harmer (2023),
  *Multiple light signaling pathways control solar tracking in sunflowers*,
  PLOS Biology, S13 Data, [doi:10.1371/journal.pbio.3002344](https://doi.org/10.1371/journal.pbio.3002344) — **CC BY**, included with attribution.
- **Animation engine:** [ManimGX](https://manimgx.academa.ai/) by Academa Labs —
  Manim CE's Python API on a Rust/wgpu core.
- **This film's code:** MIT (see the repository-root [`LICENSE`](../../LICENSE)).

## Files

```text
001-bendlab/
├── BendLab_slow_0.5x.mp4   # readable cut, 2:00 (recommended)
├── BendLab.mp4                   # original render, 1:00
├── scene.py                      # the whole film as one ManimGX Scene
├── poster.jpg                    # one still from the real-fit scene
├── data/zt0_1_measured_and_fit.csv
└── README.md                     # this file
```

## Use it in the BendLab repo

Drop `BendLab.mp4` into the BendLab README (drag it into the GitHub
editor, or attach it to a release and link it), or link this folder
from the GitHub Pages site next to the simulator.
