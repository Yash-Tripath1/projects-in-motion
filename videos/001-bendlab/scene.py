"""
BendLab — can a bending stem reveal the numbers behind it?

A ManimGX film about ONE project: BendLab, a parameter-identifiability
study of phototropic stem bending by Anadi Tripathi (project lead) with
Umaid.

Everything quantitative in this film comes from the BendLab repository
(https://github.com/Yash-Tripath1/Bendlab, snapshot 19 Oct 2026):

* Model (its `sim.py`):  tau * dr/dt = k * sin(phi - theta) - r,
  dtheta/dt = clip(r, -r_max, +r_max), integrated at 1-minute steps.
* The plotted plant is ZT0-1: measured stem angles from Brooks, Atamian
  & Harmer (2023), PLOS Biology, S13 Data Fig1C (CC BY), as shipped in
  BendLab's `data/real/`, with BendLab's fitted parameters from its
  `results/fit_fig1c.csv`:
  k = 23.03 deg/h, tau = 6.77 h, r_max = 43.91 deg/h, phi0 = 41.32 deg
  (RMSE 1.894 deg). Its realised peak bend rate, recomputed here with
  the same integrator, is 6.53 deg/h at 5.7 h — far below its fitted
  cap, which is why removing the cap leaves the RMSE at exactly 1.894.
* Fit quality (H5): median RMSE 1.80 deg over 48 measured trajectories
  vs a median across-plant SD of 8.58 deg (ratio 0.21).
* Degeneracy (H1): 10,000 uniform simulated plants, 6 behavioural
  clusters, largest cluster 2,859 plants; median within-cluster
  parameter-range retention k 25%, tau 36%, r_max 50%, phi0 25%.
  Weighted by the 44 clean real fits: 9%, 4%, 14%, 12%.
* Protocol dependence (H4): static- vs moving-light clusters,
  ARI 0.442 against a pre-specified persistence threshold of 0.50.
  (H2, the 45-degree step at hour 8, was NOT supported — the film says so.)

Render:
    pip install manimgx          # Python 3.13 or 3.14
    manimgx inspect scene.py     # storyboard + layout checks
    manimgx render scene.py      # -> BendLab.mp4 (1080p60)

Draft:
    manimgx render scene.py -r 1280x720 --fps 30
"""

from __future__ import annotations

import math

import numpy as np

import manimgx as m

# ------------------------------------------------------------ BendLab model
# Same explicit-Euler integrator as BendLab's sim.py (dt = 1 minute).

DT = 1.0 / 60.0
FIT_K, FIT_TAU, FIT_RMAX, FIT_PHI0 = 23.0298, 6.7682, 43.9052, 41.3160  # ZT0-1

# Measured ZT0-1 stem angles (degrees), hourly, Brooks et al. 2023 S13 Fig1C.
MEASURED_T = list(range(24))
MEASURED_THETA = [
    0.00, 0.96, 1.98, 6.84, 15.28, 24.36, 29.94, 35.62,
    40.28, 41.95, 45.55, 48.50, 53.75, 57.05, 57.05, 56.46,
    54.95, 53.23, 51.82, 49.27, 45.65, 42.59, 40.23, 39.37,
]


def simulate(k: float, tau: float, rmax: float, phi0: float, t_end: float = 23.5):
    """Return (times, thetas, rates) under static light at phi0 degrees."""
    n = int(round(t_end / DT))
    times = np.linspace(0.0, n * DT, n + 1)
    thetas = np.zeros(n + 1)
    rates = np.zeros(n + 1)
    theta, r = 0.0, 0.0
    for i in range(n):
        r += (k * math.sin(math.radians(phi0 - theta)) - r) * (DT / tau)
        r = max(-rmax, min(rmax, r))
        theta += r * DT
        thetas[i + 1], rates[i + 1] = theta, r
    return times, thetas, rates


_SIM_T, _SIM_THETA, _SIM_R = simulate(FIT_K, FIT_TAU, FIT_RMAX, FIT_PHI0)
THETA_OF_T = lambda x: float(np.interp(x, _SIM_T, _SIM_THETA))  # noqa: E731
RATE_OF_T = lambda x: float(np.interp(x, _SIM_T, _SIM_R))  # noqa: E731


# ------------------------------------------------------------------ helpers

def fit(mob: m.Mobject, max_width: float = 13.0) -> m.Mobject:
    if mob.width > max_width:
        mob.scale(max_width / mob.width)
    return mob


def header(text: str, color: m.ManimColor = m.WHITE) -> m.Text:
    title = fit(m.Text(text, font_size=40, color=color))
    title.to_edge(m.UP, buff=0.42)
    return title


def caption(text: str, color: m.ManimColor = m.GREY_B) -> m.Text:
    line = fit(m.Text(text, font_size=29, color=color), max_width=13.2)
    line.to_edge(m.DOWN, buff=0.42)
    return line


def box(label: str, color: m.ManimColor, width: float = 2.2, height: float = 1.0) -> m.VGroup:
    rect = m.Rectangle(width=width, height=height, color=color, fill_opacity=0.14, stroke_width=4)
    text = m.Text(label, font_size=28)
    if text.width > width - 0.25:
        text.scale((width - 0.25) / text.width)
    return m.VGroup(rect, text)


def plant(theta_deg: float, base: tuple[float, float] = (-5.0, -2.15)) -> m.VGroup:
    """A schematic sunflower whose stem curves toward theta (from vertical)."""
    points = [np.array([base[0], base[1], 0.0])]
    step = 3.3 / 7
    for i in range(7):
        ang = math.radians(theta_deg * (((i + 0.5) / 7) ** 1.15))
        points.append(points[-1] + np.array([step * math.sin(ang), step * math.cos(ang), 0.0]))
    stem = [m.Line(points[i], points[i + 1], color=m.GREEN, stroke_width=9) for i in range(7)]
    leaves = []
    for idx, side in ((2, -1), (4, 1)):
        ang = math.radians(theta_deg * (idx / 7))
        offset = np.array([side * math.cos(ang), -side * math.sin(ang), 0.0]) * 0.28
        leaves.append(m.Dot(points[idx] + offset, radius=0.14, color=m.GREEN))
    tip = points[-1]
    petals = [
        m.Circle(radius=0.095, color=m.YELLOW, fill_opacity=0.95).move_to(
            tip + np.array([0.24 * math.cos(a), 0.24 * math.sin(a), 0.0])
        )
        for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)
    ]
    head = m.Circle(radius=0.19, color=m.ORANGE, fill_opacity=0.95).move_to(tip)
    return m.VGroup(*stem, *leaves, *petals, head)


def sun(center: tuple[float, float] = (-1.0, 2.0)) -> m.VGroup:
    c = np.array([center[0], center[1], 0.0])
    disc = m.Circle(radius=0.38, color=m.YELLOW, fill_opacity=0.95).move_to(c)
    rays = []
    for a in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        d = np.array([math.cos(a), math.sin(a), 0.0])
        rays.append(m.Line(c + 0.5 * d, c + 0.74 * d, color=m.YELLOW, stroke_width=5))
    return m.VGroup(disc, *rays)


def mini_curve(position: list[float], width: float = 3.5, height: float = 1.85):
    axes = m.Axes(
        x_range=[0, 24, 12], y_range=[0, 60, 30],
        x_length=width, y_length=height,
        axis_config={"include_numbers": False},
    ).move_to(position)
    curve = axes.plot(THETA_OF_T, x_range=[0, 23.5], color=m.TEAL)
    return axes, curve


# --------------------------------------------------------------------- film

class BendLab(m.Scene):
    """Can a bending stem reveal the numbers behind it? BendLab's story."""

    def clear(self, run_time: float = 0.45) -> None:
        if self.mobjects:
            self.play(*[m.FadeOut(mob) for mob in list(self.mobjects)], run_time=run_time)

    # -- opener ------------------------------------------------------------

    def opener(self) -> None:
        title = m.Text("BENDLAB", font_size=66, color=m.GREEN).move_to([3.1, 2.35, 0])
        sub1 = fit(m.Text("Can a bending sunflower reveal", font_size=33, color=m.WHITE), 6.4).move_to([3.1, 1.45, 0])
        sub2 = fit(m.Text("the numbers behind its bend?", font_size=33, color=m.WHITE), 6.4).move_to([3.1, 0.95, 0])

        base = (-5.0, -2.15)
        vertical = m.Line([base[0], base[1], 0], [base[0], base[1] + 3.8, 0], color=m.GREY_B, stroke_width=3)
        the_plant = plant(0.0, base)
        the_sun = sun((-1.05, 2.05))
        clock = m.MathTex(r"t = 0\ \mathrm{h}, \quad \theta = 0^\circ", color=m.YELLOW).move_to([3.1, -0.15, 0])

        question = m.Text("Watch it bend. Then ask: is one curve enough?", font_size=30, color=m.TEAL)
        fit(question, 6.6)
        question.move_to([3.1, -1.55, 0])

        self.play(m.Write(title), run_time=0.9)
        self.play(m.FadeIn(sub1), m.FadeIn(sub2), m.Create(vertical), m.Create(the_plant), run_time=1.0)
        self.play(m.FadeIn(the_sun), m.FadeIn(clock), run_time=0.7)

        # ZT0-1's actual journey: slow start, overshoot to 57 deg, settle near 38.
        for t_h, th in [(5, 24.4), (9, 42.0), (13, 57.0), (23, 39.4)]:
            new_clock = m.MathTex(
                rf"t = {t_h}\ \mathrm{{h}}, \quad \theta = {th:.0f}^\circ", color=m.YELLOW
            ).move_to([3.1, -0.15, 0])
            self.play(m.Transform(the_plant, plant(th, base)), m.Transform(clock, new_clock), run_time=1.0)

        self.play(m.FadeIn(question, shift=m.UP), run_time=0.7)
        self.wait(0.9)
        self.clear()

    # -- the model ------------------------------------------------------------

    def model_machine(self) -> None:
        title = header("BendLab's bet: a deliberately tiny model", color=m.GREEN)

        eq1 = m.MathTex(r"\tau\,\frac{dr}{dt} = k\,\sin(\phi-\theta) - r", color=m.WHITE).scale(1.25)
        eq2 = m.MathTex(r"\frac{d\theta}{dt} = \mathrm{clip}\left(r,\,-r_{\max},\,+r_{\max}\right)", color=m.WHITE).scale(1.25)
        equations = m.VGroup(eq1, eq2).arrange(m.DOWN, buff=0.45).move_to([0, 1.55, 0])

        def card(symbol: str, name: str, unit: str, color: m.ManimColor) -> m.VGroup:
            rect = m.Rectangle(width=2.95, height=1.7, color=color, fill_opacity=0.12, stroke_width=4)
            sym = m.MathTex(symbol, color=color).scale(1.2).move_to([0, 0.48, 0])
            nm = m.Text(name, font_size=26, color=m.WHITE).move_to([0, -0.16, 0])
            un = m.Text(unit, font_size=24, color=m.GREY_B).move_to([0, -0.52, 0])
            return m.VGroup(rect, sym, nm, un)

        cards = m.VGroup(
            card(r"k", "response gain", "deg / h", m.BLUE),
            card(r"\tau", "sensing lag", "hours", m.PINK),
            card(r"r_{\max}", "bend-rate cap", "deg / h", m.RED),
            card(r"\phi_0", "light angle", "degrees", m.YELLOW),
        ).arrange(m.RIGHT, buff=0.35).move_to([0, -1.0, 0])

        note = caption("The lag tau is why real curves start flat, speed up, then slow down.", color=m.GREEN)

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Write(equations), run_time=1.3)
        self.play(m.LaggedStart(*[m.FadeIn(c, shift=m.UP) for c in cards], lag_ratio=0.3), run_time=1.5)
        self.play(m.FadeIn(note), run_time=0.6)
        self.wait(0.9)
        self.clear()

    # -- forward vs inverse ---------------------------------------------------

    def forward_inverse(self) -> None:
        title = header("Forwards is easy. Backwards is the trap.", color=m.BLUE)

        truth = box("truth in: 4 numbers", m.BLUE, width=3.9, height=1.15).move_to([-4.55, 1.35, 0])
        truth_vals = m.MathTex(
            r"k{=}23.0,\ \tau{=}6.77,\ r_{\max}{=}43.9,\ \phi_0{=}41.3^\circ", color=m.BLUE
        )
        fit(truth_vals, 4.5)
        truth_vals.next_to(truth, m.DOWN, buff=0.22)
        sim = box("simulate\n1-min steps", m.GREEN, width=2.3, height=1.35).move_to([-0.6, 1.35, 0])
        a1 = m.Arrow(truth.get_right(), sim.get_left(), buff=0.08, color=m.WHITE)
        top_axes, top_curve = mini_curve([3.9, 1.35, 0])
        a2 = m.Arrow(sim.get_right(), top_axes.get_left(), buff=0.08, color=m.WHITE)
        top_label = m.MathTex(r"\theta(t)\ \text{generated}", color=m.TEAL).next_to(top_axes, m.UP, buff=0.18)

        bot_axes, bot_curve = mini_curve([-4.55, -1.65, 0])
        bot_label = m.Text("a real plant gives only this curve", font_size=26, color=m.TEAL)
        fit(bot_label, 4.4)
        bot_label.next_to(bot_axes, m.DOWN, buff=0.18)
        bot_label.shift(0.45 * m.RIGHT)
        infer = box("infer?", m.ORANGE, width=2.1, height=1.2).move_to([-0.6, -1.65, 0])
        a3 = m.Arrow(bot_axes.get_right(), infer.get_left(), buff=0.08, color=m.WHITE)
        unknowns = box("????", m.RED, width=3.2, height=1.15).move_to([3.9, -1.65, 0])
        unk_vals = m.MathTex(r"k?\quad \tau?\quad r_{\max}?\quad \phi_0?", color=m.RED)
        fit(unk_vals, 4.2)
        unk_vals.next_to(unknowns, m.DOWN, buff=0.22)
        a4 = m.Arrow(infer.get_right(), unknowns.get_left(), buff=0.08, color=m.WHITE)

        self.play(m.Write(title), run_time=0.8)
        self.play(m.FadeIn(truth), m.FadeIn(truth_vals), m.Create(a1), m.FadeIn(sim), run_time=1.0)
        self.play(m.Create(a2), m.Create(top_axes), m.Create(top_curve), m.FadeIn(top_label), run_time=1.2)
        self.play(m.Create(bot_axes), m.Create(bot_curve), m.FadeIn(bot_label), run_time=1.0)
        self.play(
            m.Create(a3), m.FadeIn(infer), m.Create(a4), m.FadeIn(unknowns), m.FadeIn(unk_vals),
            run_time=1.0,
        )
        self.wait(0.9)
        self.clear()

    # -- real sunflowers --------------------------------------------------------

    def real_fit(self) -> None:
        title = header("First test: can 4 numbers fit real sunflowers?", color=m.YELLOW)

        axes = m.Axes(
            x_range=[0, 24, 4], y_range=[0, 60, 15],
            x_length=7.4, y_length=3.8,
            axis_config={"include_numbers": False},
        ).move_to([-2.75, -0.45, 0])
        xlab = m.Text("hours since light on", font_size=25, color=m.GREY_B).next_to(axes, m.DOWN, buff=0.32)
        tick_labels = m.VGroup(
            m.Text("0", font_size=24, color=m.GREY_B).move_to(axes.c2p(0, 0) + np.array([-0.35, -0.05, 0])),
            m.Text("60", font_size=24, color=m.GREY_B).move_to(axes.c2p(0, 60) + np.array([-0.5, 0, 0])),
            m.Text("24", font_size=24, color=m.GREY_B).move_to(axes.c2p(24, 0) + np.array([0, -0.38, 0])),
        )
        dots = m.VGroup(
            *[m.Dot(axes.c2p(t, th), radius=0.062, color=m.YELLOW) for t, th in zip(MEASURED_T, MEASURED_THETA)]
        )
        curve = axes.plot(THETA_OF_T, x_range=[0, 23.5], color=m.TEAL)
        legend = m.VGroup(
            m.Text("dots: measured plant ZT0-1", font_size=26, color=m.YELLOW),
            m.Text("line: BendLab's 4-parameter fit", font_size=26, color=m.TEAL),
        ).arrange(m.DOWN, buff=0.2).move_to([-2.75, 2.35, 0])

        stats = m.VGroup(
            m.Text("ALL 48 MEASURED PLANTS", font_size=25, color=m.GREY_B),
            m.Text("1.80 deg", font_size=46, color=m.TEAL),
            m.Text("median model error (RMSE)", font_size=25, color=m.WHITE),
            m.Text("8.58 deg", font_size=46, color=m.YELLOW),
            m.Text("median plant-to-plant spread", font_size=25, color=m.WHITE),
            m.Text("error / spread = 0.21", font_size=30, color=m.GREEN),
        )
        for s in stats:
            fit(s, 4.3)
        stats.arrange(m.DOWN, buff=0.24).move_to([4.55, -0.25, 0])

        source = caption("Measured data: Brooks et al., PLOS Biology 2023, S13 Fig1C (CC BY).")

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(axes), m.FadeIn(xlab), m.FadeIn(tick_labels), run_time=0.9)
        self.play(m.LaggedStart(*[m.FadeIn(d) for d in dots], lag_ratio=0.06), run_time=1.5)
        self.play(m.Create(curve), m.FadeIn(legend), run_time=1.5)
        self.play(m.LaggedStart(*[m.FadeIn(s, shift=m.RIGHT) for s in stats], lag_ratio=0.22), run_time=1.6)
        self.play(m.FadeIn(source), run_time=0.5)
        self.wait(0.9)
        self.clear()

    # -- the invisible cap ------------------------------------------------------

    def invisible_cap(self) -> None:
        title = header("The invisible speed limit", color=m.RED)

        axes = m.Axes(
            x_range=[0, 24, 4], y_range=[-5, 50, 10],
            x_length=7.4, y_length=3.9,
            axis_config={"include_numbers": False},
        ).move_to([-2.75, -0.45, 0])
        ylab = m.Text("bend rate, deg/h", font_size=25, color=m.GREY_B).next_to(axes, m.UP, buff=0.25)
        rate_curve = axes.plot(RATE_OF_T, x_range=[0, 23.5], color=m.TEAL)
        cap_line = m.Line(axes.c2p(0, FIT_RMAX), axes.c2p(24, FIT_RMAX), color=m.RED, stroke_width=6)
        cap_label = m.Text("fitted cap r_max = 43.9", font_size=26, color=m.RED)
        cap_label.move_to(axes.c2p(13.5, FIT_RMAX) + np.array([0, 0.38, 0]))
        peak = m.Dot(axes.c2p(5.7, 6.53), radius=0.09, color=m.YELLOW)
        peak_label = m.Text("fastest this plant ever bends: 6.5 / h", font_size=25, color=m.YELLOW)
        fit(peak_label, 5.4)
        peak_label.move_to(axes.c2p(13.5, 14.0))

        verdict = m.VGroup(
            m.Text("plant ZT0-1, refitted:", font_size=27, color=m.WHITE),
            m.Text("with cap      RMSE 1.894 deg", font_size=27, color=m.TEAL),
            m.Text("cap removed   RMSE 1.894 deg", font_size=27, color=m.ORANGE),
            m.Text("IDENTICAL", font_size=42, color=m.RED),
            m.Text("r_max leaves no trace in this curve.", font_size=27, color=m.WHITE),
        )
        for v in verdict:
            fit(v, 4.4)
        verdict.arrange(m.DOWN, buff=0.3).move_to([4.55, -0.35, 0])

        note = caption("A limit the plant never rches cannot be recovered — at any measurement precision.", color=m.RED)

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(axes), m.FadeIn(ylab), run_time=0.8)
        self.play(m.Create(rate_curve), run_time=1.3)
        self.play(m.Create(cap_line), m.FadeIn(cap_label), run_time=0.8)
        self.play(m.FadeIn(peak), m.FadeIn(peak_label), run_time=0.7)
        self.play(m.FadeOut(cap_line), m.FadeOut(cap_label), run_time=0.9)  # remove the cap: nothing changes
        self.play(m.LaggedStart(*[m.FadeIn(v, shift=m.RIGHT) for v in verdict], lag_ratio=0.25), run_time=1.5)
        self.play(m.FadeIn(note), run_time=0.5)
        self.wait(0.9)
        self.clear()

    # -- 10,000 plants ------------------------------------------------------------

    def population(self) -> None:
        title = header("Same behaviour. Very different insides.", color=m.PURPLE)

        # 48 dots stand in for 10,000 simulated plants.
        initial = m.VGroup()
        for i in range(48):
            x = -6.15 + (i % 8) * 0.66 + 0.14 * math.sin(i * 2.3)
            y = 1.75 - (i // 8) * 0.62 + 0.12 * math.cos(i * 1.7)
            initial.add(m.Dot([x, y, 0], radius=0.075, color=m.GREY_B))

        centers = [(-5.5, 1.05), (-3.8, 1.05), (-2.1, 1.05), (-5.5, -0.85), (-3.8, -0.85), (-2.1, -0.85)]
        colors = [m.GREEN, m.BLUE, m.ORANGE, m.PINK, m.TEAL, m.YELLOW]
        clustered = m.VGroup()
        for i in range(48):
            cx, cy = centers[i // 8]
            a = (i % 8) * math.pi / 4
            clustered.add(m.Dot([cx + 0.36 * math.cos(a), cy + 0.36 * math.sin(a), 0],
                               radius=0.075, color=colors[i // 8]))

        left_label = m.Text("10,000 simulated plants -> 6 behaviour clusters", font_size=26, color=m.WHITE)
        fit(left_label, 5.8)
        left_label.move_to([-3.8, 2.35, 0])
        big_label = m.Text("largest cluster alone: 2,859 plants", font_size=26, color=m.GREEN)
        big_label.move_to([-3.8, -2.15, 0])
        ring = m.Circle(radius=0.68, color=m.GREEN, stroke_width=5).move_to([centers[0][0], centers[0][1], 0])

        # Range-retention bars (H1, then the real-fit-weighted rerun).
        names = ["k", "tau", "r_max", "phi_0"]
        uniform = [25, 36, 50, 25]
        weighted = [9, 4, 14, 12]
        row_y = [1.35, 0.72, 0.09, -0.54]
        x0, track_w = 1.15, 4.0

        tracks = m.VGroup(*[
            m.Rectangle(width=track_w, height=0.34, color=m.GREY_B, fill_opacity=0.06, stroke_width=3)
            .move_to([x0 + track_w / 2, y, 0]) for y in row_y
        ])
        row_labels = m.VGroup(*[
            m.Text(n, font_size=26, color=m.WHITE).move_to([0.45, y, 0]) for n, y in zip(names, row_y)
        ])

        def bars(values: list[int], color: m.ManimColor) -> m.VGroup:
            group = m.VGroup()
            for v, y in zip(values, row_y):
                w = track_w * v / 100
                group.add(m.Rectangle(width=w, height=0.34, color=color, fill_opacity=0.85)
                          .move_to([x0 + w / 2, y, 0]))
                group.add(m.Text(f"{v}%", font_size=26, color=color).move_to([5.75, y, 0]))
            return group

        phase = m.Text("uniform population: parameter range kept inside a cluster", font_size=25, color=m.PURPLE)
        fit(phase, 6.2)
        phase.move_to([3.15, 2.1, 0])
        phase2 = m.Text("...after weighting by 44 clean real-plant fits", font_size=25, color=m.GREEN)
        fit(phase2, 6.2)
        phase2.move_to([3.15, 2.1, 0])

        bars_now = bars(uniform, m.PURPLE)
        bars_next = bars(weighted, m.GREEN)
        note = caption("Real data shrink the ambiguity from 25-50% to 4-14% — they do not erase it.", color=m.PURPLE)

        self.play(m.Write(title), run_time=0.8)
        self.play(m.FadeIn(left_label), m.LaggedStart(*[m.FadeIn(d) for d in initial], lag_ratio=0.02), run_time=1.2)
        self.play(m.Transform(initial, clustered), run_time=1.6)
        self.play(m.Create(ring), m.FadeIn(big_label), run_time=0.8)
        self.play(m.FadeIn(phase), m.Create(tracks), m.FadeIn(row_labels), m.FadeIn(bars_now), run_time=1.2)
        self.wait(0.5)
        self.play(m.Transform(phase, phase2), m.Transform(bars_now, bars_next), run_time=1.4)
        self.play(m.FadeIn(note), run_time=0.5)
        self.wait(0.9)
        self.clear()

    # -- protocols ------------------------------------------------------------------

    def protocols(self) -> None:
        title = header("Change the light, change the categories", color=m.ORANGE)

        centers = [(-5.2, 0.75), (-3.4, 0.75), (-1.6, 0.75)]
        colors = [m.GREEN, m.BLUE, m.PINK]

        def grid_offsets() -> list[tuple[float, float]]:
            return [(((j % 4) - 1.5) * 0.34, ((j // 4) - 1) * 0.34) for j in range(12)]

        static_dots = m.VGroup()
        for i in range(36):
            cx, cy = centers[i // 12]
            ox, oy = grid_offsets()[i % 12]
            static_dots.add(m.Dot([cx + ox, cy + oy, 0], radius=0.085, color=colors[i // 12]))

        slots = [0, 0, 0]
        moving_dots = m.VGroup()
        for i in range(36):
            group = (i // 4) % 3  # every group of 4 lands in a different moving-light cluster
            ox, oy = grid_offsets()[slots[group]]
            slots[group] += 1
            cx, cy = centers[group]
            moving_dots.add(m.Dot([cx + ox, cy + oy, 0], radius=0.085, color=colors[i // 12]))

        regime = m.Text("clusters under STATIC light", font_size=28, color=m.WHITE).move_to([-3.4, 2.1, 0])
        regime2 = m.Text("same plants under MOVING light", font_size=28, color=m.ORANGE).move_to([-3.4, 2.1, 0])

        gauge_title = m.Text("do the clusters persist? (ARI)", font_size=26, color=m.WHITE).move_to([3.65, 1.95, 0])
        track = m.Line([1.45, 0.95, 0], [5.95, 0.95, 0], color=m.WHITE, stroke_width=5)
        threshold_x = 1.45 + 4.5 * 0.50
        marker_x = 1.45 + 4.5 * 0.442
        threshold = m.Line([threshold_x, 0.6, 0], [threshold_x, 1.3, 0], color=m.RED, stroke_width=5)
        threshold_label = m.Text("persistence line 0.50", font_size=25, color=m.RED).move_to([5.05, 1.5, 0])
        marker = m.Dot([marker_x, 0.95, 0], radius=0.11, color=m.YELLOW)
        marker_label = m.Text("measured 0.442", font_size=28, color=m.YELLOW).move_to([2.35, 1.5, 0])
        verdict = m.Text("below the line: behaviour classes\nare protocol-dependent", font_size=27, color=m.ORANGE)
        fit(verdict, 4.6)
        verdict.move_to([3.65, -0.15, 0])

        honest = caption(
            "Honest twist: a 45-degree light step at hour 8 did NOT improve recovery under BendLab's first metric.",
            color=m.ORANGE,
        )

        self.play(m.Write(title), run_time=0.8)
        self.play(m.FadeIn(regime), m.LaggedStart(*[m.FadeIn(d) for d in static_dots], lag_ratio=0.02), run_time=1.2)
        self.wait(0.4)
        self.play(m.Transform(regime, regime2), m.Transform(static_dots, moving_dots), run_time=1.6)
        self.play(
            m.FadeIn(gauge_title), m.Create(track), m.Create(threshold),
            m.FadeIn(threshold_label), m.FadeIn(marker), m.FadeIn(marker_label),
            run_time=1.1,
        )
        self.play(m.FadeIn(verdict), m.FadeIn(honest), run_time=0.7)
        self.wait(1.0)
        self.clear()

    # -- outro -------------------------------------------------------------------------

    def outro(self) -> None:
        final_plant = plant(39.4, (-5.3, -2.15))
        the_sun = sun((-1.35, 2.05))

        line1 = m.Text("A good fit is not", font_size=46, color=m.WHITE).move_to([2.2, 1.9, 0])
        line2 = m.Text("a unique explanation.", font_size=46, color=m.GREEN).move_to([2.2, 1.25, 0])
        sub = fit(
            m.Text("BendLab maps what one bending curve can — and cannot — tell us.",
                   font_size=29, color=m.GREY_B),
            7.6,
        ).move_to([2.2, 0.35, 0])
        credits = m.VGroup(
            m.Text("BENDLAB", font_size=34, color=m.GREEN),
            m.Text("Anadi Tripathi (lead), with Umaid", font_size=28, color=m.WHITE),
            m.Text("github.com/Yash-Tripath1/Bendlab", font_size=26, color=m.BLUE),
        ).arrange(m.DOWN, buff=0.28).move_to([2.2, -1.25, 0])
        footer = caption("Minimal phenomenological model — not an auxin mechanism.  Data: Brooks et al. 2023 (CC BY).  Animated with ManimGX.")

        self.play(m.Create(final_plant), m.FadeIn(the_sun), run_time=1.0)
        self.play(m.Write(line1), m.Write(line2), run_time=1.1)
        self.play(m.FadeIn(sub), run_time=0.7)
        self.play(m.LaggedStart(*[m.FadeIn(c, shift=m.UP) for c in credits], lag_ratio=0.3), run_time=1.1)
        self.play(m.FadeIn(footer), run_time=0.5)
        self.wait(1.8)

    # -- film ------------------------------------------------------------------------------

    def construct(self) -> None:
        self.next_section("opener")
        self.opener()
        self.next_section("model")
        self.model_machine()
        self.next_section("forward-vs-inverse")
        self.forward_inverse()
        self.next_section("real-sunflowers")
        self.real_fit()
        self.next_section("invisible-cap")
        self.invisible_cap()
        self.next_section("ten-thousand-plants")
        self.population()
        self.next_section("protocols")
        self.protocols()
        self.next_section("outro")
        self.outro()
