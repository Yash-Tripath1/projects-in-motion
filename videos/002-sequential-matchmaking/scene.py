"""
Sequential Matchmaking — when a winning policy meets twelve times the data.

An animated research explainer about Anadi Tripathi's sequential
reciprocal-matching study, based on the paper supplied by the author:

    "A Reported +0.175 Advantage Does Not Survive Twelve Times the Data:
     a two-phase non-replication study in sequential reciprocal matching"

Canonical project snapshot used for this film:
    https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab
    repository HEAD 7e00189b9b98715ac7db860b1a10b392c14a2052 (20 Oct 2026)
    paper-pinned commit e9515580aac62e818113f5aa17c4de1780697eca
    archived concept DOI 10.5281/zenodo.23457651

The attached PDF and the repository's PAPER.pdf are byte-identical
(SHA-256 8e6207ba408c11d1e17d927cc2249b9dc8ebfc8b0686e119c0745bfd37e432d9).

Sign convention used consistently below, matching the paper's Figure 1 and
`results/analysis_120seeds_four_arm.json`:

    paired difference = candidate arm - greedy

Thus the 120-seed result for the Phase 1 incumbent is
potential_ask - greedy = -0.0326, 95% CI [-0.0903, +0.0250].

All people and outcomes in the underlying study are synthetic simulator
records. Nothing in the film is evidence about a real matching service.

Render:
    pip install manimgx          # Python 3.13 or 3.14
    manimgx inspect scene.py     # storyboard + layout checks
    manimgx render scene.py      # -> SequentialMatchmaking.mp4 (1080p60)
"""

from __future__ import annotations

import math

import numpy as np

import manimgx as m


# --------------------------------------------------------------------------
# Result values traced to the paper and repository result files.
# --------------------------------------------------------------------------

# Phase 2 seed outcomes, in seed-ID order 1101..1220, for potential_ask
# relative to greedy: W = potential_ask higher, T = tie, L = lower.
# Derived from results/analysis_120seeds_four_arm.json; counts 44/18/58.
PHASE2_TILES = (
    "LLWLLLTWWLLWLWLWWLWTWLLLTTLWLTTWLTLWLLWLLTWTWTWWWWLLTLLWWLLLLLL"
    "WWLLWLWWLTLLLTWLWWWLTTLLWLWLLLWWWLLLLWWLWLWTLLLWWTWLTWLLW"
)

# 120-seed primary outcome: (arm, estimate, CI low, CI high, events, colour).
ARM_ROWS = [
    ("greedy", 0.402, 0.357, 0.448, 579, m.BLUE),
    ("potential_ask", 0.369, 0.324, 0.416, 532, m.RED),
    ("random_feasible", 0.332, 0.292, 0.374, 478, m.GREY_B),
    ("no_ask", 0.098, 0.075, 0.122, 141, m.ORANGE),
]

# Mean askable members reported in paper section 5.4(a).
ASKABLE_BY_DAY = [(0, 45), (5, 30), (10, 15), (15, 3), (20, 0)]

# MDE(n) = (z_0.975 + z_0.80) * paired SD / sqrt(n), for the
# disagreement_aware contrast: (1.95996 + 0.84162) * 0.2136 = 0.5984.
MDE_COEFF = 0.5984


# --------------------------------------------------------------------------
# Small drawing helpers (kept deliberately close to the BendLab film's API use)
# --------------------------------------------------------------------------

def fit(mob: m.Mobject, max_width: float = 13.0) -> m.Mobject:
    if mob.width > max_width:
        mob.scale(max_width / mob.width)
    return mob


def label(text: str, size: int = 28, color: m.ManimColor = m.WHITE,
          max_width: float | None = None) -> m.Text:
    out = m.Text(text, font_size=size, color=color)
    if max_width is not None:
        fit(out, max_width)
    return out


def header(text: str, color: m.ManimColor = m.WHITE) -> m.Text:
    title = fit(m.Text(text, font_size=40, color=color), 13.2)
    title.to_edge(m.UP, buff=0.42)
    return title


def caption(text: str, color: m.ManimColor = m.GREY_B) -> m.Text:
    line = fit(m.Text(text, font_size=27, color=color), max_width=13.2)
    line.to_edge(m.DOWN, buff=0.42)
    return line


def chip(text: str, color: m.ManimColor, width: float = 2.8,
         height: float = 0.62, font_size: int = 24) -> m.VGroup:
    rect = m.Rectangle(
        width=width, height=height, color=color,
        fill_opacity=0.13, stroke_width=4,
    )
    words = fit(m.Text(text, font_size=font_size, color=m.WHITE), width - 0.25)
    return m.VGroup(rect, words)


def panel(width: float, height: float, color: m.ManimColor = m.GREY_B) -> m.Rectangle:
    return m.Rectangle(
        width=width, height=height, color=color,
        fill_opacity=0.045, stroke_width=3,
    )


def dashed_line(start, end, color: m.ManimColor = m.WHITE,
                dash: float = 0.16, gap: float = 0.11,
                stroke_width: int = 4) -> m.VGroup:
    a = np.array(start, dtype=float)
    b = np.array(end, dtype=float)
    total = float(np.linalg.norm(b - a))
    direction = (b - a) / total
    pieces = []
    at = 0.0
    while at < total:
        stop = min(total, at + dash)
        pieces.append(
            m.Line(a + direction * at, a + direction * stop,
                   color=color, stroke_width=stroke_width)
        )
        at += dash + gap
    return m.VGroup(*pieces)


def interval(x_of_value, y: float, lo: float, hi: float, estimate: float,
             color: m.ManimColor, cap: float = 0.18) -> m.VGroup:
    x_lo, x_hi, x_est = x_of_value(lo), x_of_value(hi), x_of_value(estimate)
    return m.VGroup(
        m.Line([x_lo, y, 0], [x_hi, y, 0], color=color, stroke_width=9),
        m.Line([x_lo, y - cap, 0], [x_lo, y + cap, 0], color=color, stroke_width=5),
        m.Line([x_hi, y - cap, 0], [x_hi, y + cap, 0], color=color, stroke_width=5),
        m.Dot([x_est, y, 0], radius=0.105, color=color),
    )


def vertical_bar(x: float, baseline: float, value: float, scale: float,
                 color: m.ManimColor, width: float = 1.25) -> m.Rectangle:
    height = value * scale
    return m.Rectangle(
        width=width, height=height, color=color,
        fill_opacity=0.78, stroke_width=3,
    ).move_to([x, baseline + height / 2, 0])


def person_token(center, color: m.ManimColor, scale: float = 1.0) -> m.VGroup:
    x, y = center
    head = m.Circle(radius=0.13 * scale, color=color, fill_opacity=0.95)
    head.move_to([x, y + 0.17 * scale, 0])
    body = m.Circle(radius=0.19 * scale, color=color, fill_opacity=0.75)
    body.move_to([x, y - 0.20 * scale, 0])
    return m.VGroup(body, head)


def profile_card(center, title: str, color: m.ManimColor,
                 rows: list[str], unknown: bool = False) -> m.VGroup:
    x, y = center
    card = m.Rectangle(
        width=1.72, height=2.22, color=color,
        fill_opacity=0.08, stroke_width=4,
    ).move_to([x, y, 0])
    person = person_token((x, y + 0.60), color, scale=0.78)
    name = fit(m.Text(title, font_size=24, color=color), 1.45).move_to([x, y + 0.13, 0])
    pieces = [card, person, name]
    for i, row in enumerate(rows):
        yy = y - 0.30 - 0.30 * i
        dot_color = m.RED if unknown and i == 1 else m.GREEN
        dot = m.Dot([x - 0.57, yy, 0], radius=0.055, color=dot_color)
        words = fit(
            m.Text(row, font_size=24, color=m.WHITE), 1.12
        ).move_to([x + 0.20, yy, 0])
        pieces.extend([dot, words])
    return m.VGroup(*pieces)


def member_grid(center, colored: int = 200, spacing: float = 0.17,
                radius: float = 0.039, palette=None) -> m.VGroup:
    """Exactly 200 dots in a 20 x 10 grid; the first `colored` get palette colours."""
    if palette is None:
        palette = [m.BLUE, m.TEAL, m.PURPLE, m.YELLOW, m.GREEN]
    cx, cy = center
    dots = m.VGroup()
    for i in range(200):
        col, row = i % 20, i // 20
        x = cx + (col - 9.5) * spacing
        y = cy + (4.5 - row) * spacing
        color = palette[i % len(palette)] if i < colored else m.GREY_B
        dots.add(m.Dot([x, y, 0], radius=radius, color=color))
    return dots


# --------------------------------------------------------------------------
# Film
# --------------------------------------------------------------------------

class SequentialMatchmaking(m.Scene):
    """A Phase 1 policy win, its selection traps, and a 120-seed re-test."""

    def clear(self, run_time: float = 0.45) -> None:
        if self.mobjects:
            self.play(*[m.FadeOut(mob) for mob in list(self.mobjects)], run_time=run_time)

    # -- 1. opener -----------------------------------------------------------

    def opener(self) -> None:
        title1 = fit(label("SEQUENTIAL", 58, m.BLUE), 6.6).move_to([-3.65, 2.25, 0])
        title2 = fit(label("MATCHMAKING", 58, m.TEAL), 6.6).move_to([-3.65, 1.55, 0])
        subtitle = fit(
            label("When a winning policy meets\ntwelve times the data", 31, m.WHITE), 6.3
        ).move_to([-3.65, 0.55, 0])

        badge = chip("Phase 1 advantage: +0.175", m.RED, width=4.9, height=0.78, font_size=29)
        badge.move_to([-3.65, -0.72, 0])
        question = fit(
            label("A real edge - or the winner of a noisy screen?", 28, m.YELLOW), 6.5
        ).move_to([-3.65, -1.62, 0])
        cross = m.VGroup(
            m.Line([-1.28, -0.38, 0], [-0.98, -0.08, 0], color=m.RED, stroke_width=7),
            m.Line([-1.28, -0.08, 0], [-0.98, -0.38, 0], color=m.RED, stroke_width=7),
        )

        # A small synthetic member network; one introduced pair is highlighted.
        offsets = [
            (-1.5, 1.35), (-0.45, 1.75), (0.65, 1.45), (1.55, 1.05),
            (-1.65, 0.25), (-0.55, 0.45), (0.65, 0.35), (1.65, 0.05),
            (-1.25, -0.95), (-0.15, -0.75), (0.9, -1.0), (1.65, -1.35),
        ]
        centers = [(3.75 + x, 0.45 + y) for x, y in offsets]
        colors = [m.BLUE, m.TEAL, m.PURPLE, m.GREEN, m.YELLOW, m.ORANGE]
        links = [(0, 1), (1, 2), (2, 3), (4, 5), (5, 6), (6, 7),
                 (8, 9), (9, 10), (10, 11), (1, 5), (5, 9), (2, 6)]
        network_links = m.VGroup(*[
            m.Line([*centers[a], 0], [*centers[b], 0], color=m.GREY_B, stroke_width=3)
            for a, b in links
        ])
        people = m.VGroup(*[
            person_token(c, colors[i % len(colors)], scale=0.82)
            for i, c in enumerate(centers)
        ])
        winning_link = m.Line(
            [*centers[5], 0], [*centers[10], 0], color=m.YELLOW, stroke_width=9
        )
        network_label = fit(
            label("synthetic members - one feasible introduction", 23, m.YELLOW), 5.6
        ).move_to([3.75, -1.75, 0])

        note = caption("All members and outcomes in this study are synthetic simulator data.")

        self.play(m.Write(title1), m.Write(title2), run_time=0.9)
        self.play(m.FadeIn(subtitle, shift=m.UP), run_time=0.7)
        self.play(m.Create(network_links), m.FadeIn(people), run_time=1.1)
        self.play(m.Create(winning_link), m.FadeIn(network_label), run_time=0.8)
        self.play(m.FadeIn(badge, shift=m.UP), run_time=0.7)
        self.play(m.Create(cross), m.FadeIn(question), run_time=0.8)
        self.play(m.FadeIn(note), run_time=0.5)
        self.wait(0.8)
        self.clear()

    # -- 2. the daily allocation problem -------------------------------------

    def daily_problem(self) -> None:
        title = header("Every day: spend questions, then choose pairs", color=m.BLUE)

        pool_frame = panel(3.95, 2.65, m.BLUE).move_to([-5.0, 0.05, 0])
        pool = member_grid((-5.0, 0.05), colored=200, spacing=0.165, radius=0.038)
        pool_label = fit(
            label("200 synthetic members\narriving on days 0-20", 23, m.BLUE), 3.8
        ).move_to([-5.0, 2.02, 0])

        budget_label = fit(
            label("ask budget: 12 units/day", 24, m.TEAL), 3.7
        ).move_to([-5.0, -1.48, 0])
        budget_dots = m.VGroup()
        for i in range(12):
            group, within = divmod(i, 3)
            x = -6.28 + group * 0.82 + within * 0.22
            budget_dots.add(m.Dot([x, -1.88, 0], radius=0.075, color=m.TEAL))
        budget_note = fit(
            label("hard bundle = 3    soft field = 1", 21, m.GREY_B), 3.8
        ).move_to([-5.0, -2.25, 0])

        steps = m.VGroup(
            chip("1  OBSERVE", m.BLUE, width=2.45, height=0.58),
            chip("2  ASK", m.TEAL, width=2.45, height=0.58),
            chip("3  REFRESH", m.PURPLE, width=2.45, height=0.58),
            chip("4  GATE + MATCH", m.YELLOW, width=2.45, height=0.58),
        ).arrange(m.DOWN, buff=0.32).move_to([-0.95, 0.42, 0])
        down_arrows = m.VGroup(*[
            m.Arrow([-0.95, y, 0], [-0.95, y - 0.28, 0], color=m.WHITE, buff=0.03)
            for y in (1.28, 0.38, -0.52)
        ])
        pool_arrow = m.Arrow(pool_frame.get_right(), steps[0].get_left(), color=m.WHITE, buff=0.08)
        loop_label = fit(label("repeat for 60 decision days", 22, m.GREY_B), 2.8)
        loop_label.move_to([-0.95, -1.82, 0])

        gate_frame = panel(5.15, 3.45, m.YELLOW).move_to([3.85, 0.25, 0])
        card_a = profile_card(
            (2.25, 0.58), "MEMBER A", m.BLUE,
            ["age", "zones", "times"],
        )
        card_b = profile_card(
            (5.45, 0.58), "MEMBER B", m.PURPLE,
            ["age", "zones ?", "times"], unknown=True,
        )
        card_b_known = profile_card(
            (5.45, 0.58), "MEMBER B", m.PURPLE,
            ["age", "zones", "times"], unknown=False,
        )
        arrow_ab = m.Arrow([3.20, 0.92, 0], [4.50, 0.92, 0], color=m.WHITE, buff=0.05)
        arrow_ba = m.Arrow([4.50, 0.28, 0], [3.20, 0.28, 0], color=m.WHITE, buff=0.05)
        reciprocal = fit(
            label("both directions must pass", 21, m.WHITE), 2.7
        ).move_to([3.85, -0.80, 0])
        blocked = chip("UNKNOWN HARD FIELD: BLOCKED", m.RED, width=4.35, height=0.58, font_size=21)
        blocked.move_to([3.85, -1.28, 0])
        passed = chip("FEASIBLE: INTRODUCE THE PAIR", m.GREEN, width=4.35, height=0.58, font_size=21)
        passed.move_to([3.85, -1.28, 0])

        score = caption(
            "Score (MSMI/100): mutual second-meeting intentions per 100 arrived members - roughly one event per episode.",
            color=m.YELLOW,
        )

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(pool_frame), m.FadeIn(pool_label), run_time=0.7)
        self.play(
            m.LaggedStart(*[m.FadeIn(d) for d in pool], lag_ratio=0.004),
            run_time=1.5,
        )
        self.play(m.FadeIn(budget_label), m.FadeIn(budget_dots), m.FadeIn(budget_note), run_time=0.8)
        self.play(
            m.Create(pool_arrow),
            m.LaggedStart(*[m.FadeIn(s, shift=m.RIGHT) for s in steps], lag_ratio=0.22),
            m.Create(down_arrows),
            run_time=1.5,
        )
        self.play(m.FadeIn(loop_label), m.Create(gate_frame), m.FadeIn(card_a), m.FadeIn(card_b), run_time=1.0)
        self.play(m.Create(arrow_ab), m.Create(arrow_ba), m.FadeIn(reciprocal), m.FadeIn(blocked), run_time=0.9)
        self.wait(0.35)
        self.play(m.Transform(card_b, card_b_known), m.FadeOut(blocked), run_time=0.65)
        self.play(m.FadeIn(passed), m.FadeIn(score), run_time=0.7)
        self.wait(0.9)
        self.clear()

    # -- 3. Phase 1 ------------------------------------------------------------

    def phase_one(self) -> None:
        title = header("Phase 1 found a clear winner", color=m.RED)
        baseline = -2.05
        scale = 4.7

        grid = m.VGroup()
        ticks = m.VGroup()
        for value in (0.0, 0.2, 0.4, 0.6):
            y = baseline + value * scale
            grid.add(dashed_line([-6.0, y, 0], [-0.72, y, 0], color=m.GREY_B, dash=0.13, gap=0.10, stroke_width=2))
            ticks.add(label(f"{value:.1f}", 21, m.GREY_B).move_to([-6.45, y, 0]))
        axis = m.Line([-6.0, baseline, 0], [0.35, baseline, 0], color=m.WHITE, stroke_width=4)
        y_label = fit(label("MSMI per 100 arrived members", 23, m.GREY_B), 5.2)
        y_label.move_to([-2.85, 1.55, 0])

        greedy_bar = vertical_bar(-4.45, baseline, 0.350, scale, m.BLUE, width=1.45)
        potential_bar = vertical_bar(-1.55, baseline, 0.525, scale, m.RED, width=1.45)
        greedy_value = label("0.350", 34, m.BLUE).move_to([-4.45, baseline + 0.350 * scale + 0.58, 0])
        potential_value = label("0.525", 38, m.RED).move_to([-1.55, baseline + 0.525 * scale + 0.58, 0])
        greedy_name = fit(label("greedy\n42 events", 24, m.BLUE), 1.8).move_to([-4.45, -2.72, 0])
        potential_name = fit(label("potential_ask\n63 events", 24, m.RED), 2.0).move_to([-1.55, -2.72, 0])

        diff_arrow = m.Arrow(
            [-0.35, baseline + 0.350 * scale, 0],
            [-0.35, baseline + 0.525 * scale, 0],
            color=m.YELLOW, buff=0.04,
        )
        diff_label = label("+0.175", 34, m.YELLOW).move_to([0.48, 0.18, 0])

        stats = m.VGroup(
            label("THE SCREEN", 24, m.GREY_B),
            label("17 configurations", 31, m.WHITE),
            label("10 seeds x 6 families", 28, m.WHITE),
            label("60 episodes per arm", 28, m.WHITE),
            label("difference", 24, m.GREY_B),
            label("+0.175", 46, m.YELLOW),
            label("95% CI [+0.092, +0.258]", 26, m.WHITE),
            label("p = 0.016", 28, m.WHITE),
        )
        for text in stats:
            fit(text, 4.3)
        stats.arrange(m.DOWN, buff=0.23).move_to([3.65, -0.10, 0])

        note = caption("The confidence interval excludes zero. It looks like a discovery.", color=m.RED)

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(grid), m.Create(axis), m.FadeIn(ticks), m.FadeIn(y_label), run_time=0.8)
        self.play(m.FadeIn(greedy_bar, shift=m.UP), m.FadeIn(greedy_value), m.FadeIn(greedy_name), run_time=0.9)
        self.play(m.FadeIn(potential_bar, shift=m.UP), m.FadeIn(potential_value), m.FadeIn(potential_name), run_time=0.9)
        self.play(m.Create(diff_arrow), m.FadeIn(diff_label), run_time=0.7)
        self.play(
            m.LaggedStart(*[m.FadeIn(s, shift=m.RIGHT) for s in stats], lag_ratio=0.14),
            run_time=1.6,
        )
        self.play(m.FadeIn(note), run_time=0.5)
        self.wait(0.9)
        self.clear()

    # -- 4. selection traps and exact recovery --------------------------------

    def selection_traps(self) -> None:
        title = header("Three reasons not to trust the trophy yet", color=m.ORANGE)
        centers = [-4.65, 0.0, 4.65]
        frames = m.VGroup(*[
            panel(4.15, 3.55, color).move_to([x, 0.55, 0])
            for x, color in zip(centers, [m.RED, m.ORANGE, m.YELLOW])
        ])
        headings = m.VGroup(
            fit(label("1  MAX OF 17", 28, m.RED), 3.75).move_to([-4.65, 2.02, 0]),
            fit(label("2  SAME SEEDS TWICE", 28, m.ORANGE), 3.75).move_to([0, 2.02, 0]),
            fit(label("3  COARSE RULER", 28, m.YELLOW), 3.75).move_to([4.65, 2.02, 0]),
        )

        # Card 1: anonymous noisy estimates. The heights are a labelled
        # schematic; only the count (17) and maximum-selection logic are data.
        heights = [0.65, 0.9, 0.52, 1.02, 0.78, 0.58, 1.14, 0.84, 0.69,
                   1.22, 0.74, 0.96, 1.48, 0.62, 1.05, 0.81, 0.57]
        screen_bars = m.VGroup()
        for i, h in enumerate(heights):
            color = m.RED if i == 12 else m.GREY_B
            screen_bars.add(
                m.Rectangle(width=0.105, height=h, color=color, fill_opacity=0.85, stroke_width=1)
                .move_to([-6.10 + i * 0.181, -0.10 + h / 2, 0])
            )
        screen_base = m.Line([-6.25, -0.10, 0], [-3.05, -0.10, 0], color=m.WHITE, stroke_width=3)
        screen_text = fit(
            label("pick the maximum,\nthen report that maximum", 23, m.WHITE), 3.5
        ).move_to([-4.65, -0.58, 0])
        schematic = label("schematic heights", 18, m.GREY_B).move_to([-4.65, -1.08, 0])

        # Card 2: the disclosed pilot seeds inside the later measurement set.
        pilot = m.VGroup(
            chip("101", m.RED, width=0.83, height=0.5, font_size=21),
            chip("102", m.RED, width=0.83, height=0.5, font_size=21),
            chip("303", m.RED, width=0.83, height=0.5, font_size=21),
        ).arrange(m.RIGHT, buff=0.18).move_to([0, 1.28, 0])
        pilot_label = label("used to SELECT it", 21, m.RED).move_to([0, 1.68, 0])
        seed_arrow = m.Arrow([0, 0.92, 0], [0, 0.48, 0], color=m.WHITE, buff=0.04)
        seed_tiles = m.VGroup()
        for i in range(10):
            col, row = i % 5, i // 5
            color = m.RED if i in (0, 1, 5) else m.GREY_B
            seed_tiles.add(
                m.Rectangle(width=0.34, height=0.34, color=color, fill_opacity=0.75, stroke_width=2)
                .move_to([-0.84 + col * 0.42, 0.16 - row * 0.44, 0])
            )
        seed_text = fit(
            label("the same three are inside\nthe 10-seed measurement", 23, m.WHITE), 3.5
        ).move_to([0, -0.84, 0])

        # Card 3: observed gap versus Phase 1's own resolution estimate.
        x0 = 3.02
        x_of = lambda v: x0 + 10.8 * v  # noqa: E731 - local screen mapping
        ruler = m.Line([x0, -0.12, 0], [x_of(0.30), -0.12, 0], color=m.WHITE, stroke_width=4)
        observed = m.Rectangle(
            width=x_of(0.175) - x0, height=0.30, color=m.YELLOW,
            fill_opacity=0.8, stroke_width=2,
        ).move_to([(x0 + x_of(0.175)) / 2, 0.98, 0])
        resolution = m.Rectangle(
            width=x_of(0.234) - x0, height=0.30, color=m.RED,
            fill_opacity=0.8, stroke_width=2,
        ).move_to([(x0 + x_of(0.234)) / 2, 0.22, 0])
        observed_label = fit(label("observed gap 0.175", 21, m.YELLOW), 2.5).move_to([3.95, 1.38, 0])
        resolution_label = fit(label("resolution 0.234", 21, m.RED), 2.5).move_to([4.15, 0.60, 0])
        ruler_text = fit(
            label("at 60 episodes/arm,\nthe ruler is coarser than the gap", 23, m.WHITE), 3.6
        ).move_to([4.65, -0.72, 0])

        recovery_frame = panel(12.9, 0.82, m.GREEN).move_to([0, -2.05, 0])
        recovery = fit(
            label("RECOVERY GATE: rebuilt code matched the stored record on 60/60 episodes - 0.525, 63 events", 25, m.GREEN),
            12.4,
        ).move_to([0, -2.05, 0])
        signed = fit(
            label("A prose-based signed variant scored 0.367 (44 events). Test code, not a description.", 23, m.RED),
            11.8,
        ).move_to([0, -2.78, 0])

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(frames), m.FadeIn(headings), run_time=0.8)
        self.play(m.Create(screen_base), m.FadeIn(screen_bars), m.FadeIn(screen_text), m.FadeIn(schematic), run_time=1.0)
        self.play(m.FadeIn(pilot_label), m.FadeIn(pilot), m.Create(seed_arrow), m.FadeIn(seed_tiles), m.FadeIn(seed_text), run_time=1.1)
        self.play(
            m.Create(ruler), m.FadeIn(observed), m.FadeIn(resolution),
            m.FadeIn(observed_label), m.FadeIn(resolution_label), m.FadeIn(ruler_text),
            run_time=1.1,
        )
        self.wait(0.4)
        self.play(m.Create(recovery_frame), m.FadeIn(recovery), run_time=0.8)
        self.play(m.FadeIn(signed), run_time=0.55)
        self.wait(0.95)
        self.clear()

    # -- 5. the fresh-seed replication -----------------------------------------

    def fresh_test(self) -> None:
        title = header("Then: 120 fresh seeds, paired world-for-world", color=m.BLUE)

        design = m.VGroup(
            chip("seeds 1101-1220", m.BLUE, width=2.85),
            chip("720 episodes / arm", m.TEAL, width=3.05),
            chip("6 scenario families", m.PURPLE, width=3.15),
            chip("50,000 bootstraps", m.YELLOW, width=3.05),
        ).arrange(m.RIGHT, buff=0.22).move_to([0, 2.48, 0])

        # Forest plot, difference = potential_ask - greedy.
        x_of = lambda v: -4.85 + (v + 0.14) * 17.4  # noqa: E731
        zero = dashed_line([x_of(0), -0.48, 0], [x_of(0), 1.50, 0], color=m.WHITE)
        axis = m.Line([x_of(-0.14), -0.48, 0], [x_of(0.32), -0.48, 0], color=m.WHITE, stroke_width=4)
        tick_text = m.VGroup()
        for value in (-0.1, 0.0, 0.1, 0.2, 0.3):
            tick_text.add(label(f"{value:+.1f}", 19, m.GREY_B).move_to([x_of(value), -0.78, 0]))
        axis_label = fit(
            label("potential_ask - greedy (MSMI/100)", 22, m.GREY_B), 5.6
        ).move_to([-1.65, -1.12, 0])

        phase1_label = fit(label("Phase 1\n10 seeds", 23, m.RED), 1.7).move_to([-6.05, 1.28, 0])
        phase2_label = fit(label("Phase 2\n120 fresh", 23, m.BLUE), 1.7).move_to([-6.05, 0.28, 0])
        phase1_interval = interval(x_of, 1.28, 0.092, 0.258, 0.175, m.RED)
        phase2_interval = interval(x_of, 0.28, -0.0903, 0.0250, -0.0326, m.BLUE)
        phase1_value = fit(
            label("+0.175  [+0.092, +0.258]  p=0.016", 23, m.WHITE), 4.15
        ).move_to([4.82, 1.28, 0])
        phase2_value = fit(
            label("-0.033  [-0.090, +0.025]  p=0.356", 23, m.WHITE), 4.15
        ).move_to([4.82, 0.28, 0])
        gap_arrow = m.Arrow(
            [x_of(-0.0326), 0.55, 0], [x_of(0.175), 1.02, 0],
            color=m.YELLOW, buff=0.06,
        )
        gap_text = fit(
            label("7.09 standard errors apart - intervals do not overlap", 23, m.YELLOW), 6.7
        ).move_to([-0.85, 1.82, 0])

        scores = m.VGroup(
            label("120-SEED SCORES", 22, m.GREY_B),
            label("greedy  0.402  -  579 events", 27, m.BLUE),
            label("potential_ask  0.369  -  532 events", 27, m.RED),
        ).arrange(m.DOWN, buff=0.24).move_to([-3.65, -2.05, 0])
        for text in scores:
            fit(text, 5.7)

        # One tile per paired seed, in the repository's seed order.
        tile_colors = {"W": m.RED, "T": m.GREY_B, "L": m.BLUE}
        tiles = m.VGroup()
        for i, code in enumerate(PHASE2_TILES):
            col, row = i % 15, i // 15
            tiles.add(
                m.Rectangle(
                    width=0.14, height=0.14, color=tile_colors[code],
                    fill_opacity=0.88, stroke_width=1,
                ).move_to([2.28 + col * 0.205, -1.50 - row * 0.185, 0])
            )
        tile_title = fit(
            label("each tile: one paired seed (ID order)", 21, m.WHITE), 3.9
        ).move_to([4.00, -1.12, 0])
        tile_legend = fit(
            label("potential wins 44   ties 18   greedy wins 58", 20, m.GREY_B), 5.0
        ).move_to([3.72, -3.06, 0])

        method_note = caption(
            "Uncertainty resamples seed blocks - because scenario families reuse members within a seed.",
            color=m.BLUE,
        )

        self.play(m.Write(title), run_time=0.8)
        self.play(
            m.LaggedStart(*[m.FadeIn(c, shift=m.DOWN) for c in design], lag_ratio=0.16),
            run_time=1.1,
        )
        self.play(
            m.Create(axis), m.Create(zero), m.FadeIn(tick_text), m.FadeIn(axis_label),
            m.FadeIn(phase1_label), m.FadeIn(phase2_label),
            run_time=0.9,
        )
        self.play(m.Create(phase1_interval), m.FadeIn(phase1_value), run_time=0.9)
        self.play(m.FadeIn(tile_title), run_time=0.45)
        self.play(
            m.LaggedStart(*[m.FadeIn(t) for t in tiles], lag_ratio=0.006),
            run_time=1.7,
        )
        self.play(m.Create(phase2_interval), m.FadeIn(phase2_value), m.FadeIn(tile_legend), run_time=0.9)
        self.play(m.Create(gap_arrow), m.FadeIn(gap_text), run_time=0.8)
        self.play(m.FadeIn(scores), m.FadeIn(method_note), run_time=0.7)
        self.wait(1.0)
        self.clear()

    # -- 6. what did replicate ---------------------------------------------------

    def asking_matters(self) -> None:
        title = header("The ranking vanished. The structure did not.", color=m.TEAL)
        x_of = lambda v: -4.65 + 12.2 * v  # noqa: E731; 0.00..0.50 domain
        rows_y = [1.65, 0.92, 0.19, -0.54]

        grid = m.VGroup()
        tick_labels = m.VGroup()
        for value in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5):
            grid.add(dashed_line([x_of(value), -1.0, 0], [x_of(value), 2.05, 0], color=m.GREY_B, dash=0.11, gap=0.10, stroke_width=2))
            tick_labels.add(label(f"{value:.1f}", 19, m.GREY_B).move_to([x_of(value), -1.28, 0]))
        axis_label = fit(
            label("MSMI per 100 arrived members (95% seed-block CI)", 21, m.GREY_B), 6.8
        ).move_to([-1.60, -1.68, 0])

        arm_groups = []
        for (name, estimate, lo, hi, events, color), y in zip(ARM_ROWS, rows_y):
            name_text = fit(label(name, 23, color), 2.15).move_to([-5.90, y, 0])
            line = interval(x_of, y, lo, hi, estimate, color, cap=0.14)
            value_text = fit(label(f"{estimate:.3f}\n{events} events", 20, m.WHITE), 1.25)
            value_text.move_to([2.25, y, 0])
            arm_groups.append(m.VGroup(name_text, line, value_text))
        arm_group = m.VGroup(*arm_groups)

        callouts = m.VGroup(
            label("WHAT REPLICATED", 22, m.GREY_B),
            label("+0.304", 43, m.TEAL),
            label("greedy - no_ask", 25, m.WHITE),
            label("[+0.261, +0.349], p < 0.001", 22, m.WHITE),
            label("+0.070", 36, m.BLUE),
            label("greedy - random_feasible", 23, m.WHITE),
            label("[+0.023, +0.116], p = 0.004", 22, m.WHITE),
        )
        for text in callouts:
            fit(text, 3.65)
        callouts.arrange(m.DOWN, buff=0.22).move_to([5.0, 0.20, 0])
        callout_frame = panel(3.95, 4.15, m.TEAL).move_to([5.0, 0.20, 0])

        note = caption(
            "Asking creates the feasible supply. Choosing among competent asking rules is the hard part.",
            color=m.TEAL,
        )

        self.play(m.Write(title), run_time=0.8)
        self.play(m.Create(grid), m.FadeIn(tick_labels), m.FadeIn(axis_label), run_time=0.8)
        self.play(
            m.LaggedStart(*[m.FadeIn(g, shift=m.RIGHT) for g in arm_groups], lag_ratio=0.22),
            run_time=1.7,
        )
        self.play(m.Create(callout_frame), run_time=0.55)
        self.play(
            m.LaggedStart(*[m.FadeIn(c, shift=m.UP) for c in callouts], lag_ratio=0.16),
            run_time=1.5,
        )
        self.play(m.FadeIn(note), run_time=0.5)
        self.wait(0.95)
        self.clear()

    # -- 7. why competent policies blur together --------------------------------

    def why_hard(self) -> None:
        title = header("Why competent policies look alike", color=m.PURPLE)

        left_frame = panel(6.45, 4.95, m.YELLOW).move_to([-3.55, 0.05, 0])
        right_frame = panel(6.45, 4.95, m.PURPLE).move_to([3.55, 0.05, 0])
        left_title = label("A  SUPPLY CEILING", 27, m.YELLOW).move_to([-3.55, 2.22, 0])
        right_title = label("B  HIDDEN VARIATION", 27, m.PURPLE).move_to([3.55, 2.22, 0])

        ceiling_track = m.Rectangle(
            width=5.35, height=0.38, color=m.GREY_B,
            fill_opacity=0.08, stroke_width=3,
        ).move_to([-3.55, 1.58, 0])
        ceiling_fill_width = 5.35 * 0.978
        ceiling_fill = m.Rectangle(
            width=ceiling_fill_width, height=0.38, color=m.YELLOW,
            fill_opacity=0.82, stroke_width=2,
        ).move_to([-3.55 - 5.35 / 2 + ceiling_fill_width / 2, 1.58, 0])
        ceiling_text = label("coverage = 97.8% of the structural ceiling", 23, m.YELLOW)
        fit(ceiling_text, 5.7)
        ceiling_text.move_to([-3.55, 1.08, 0])

        # Exactly 200 dots; 67 highlighted, 133 muted, matching the reported
        # average of about 133.3 never introduced per 200.
        dots = member_grid(
            (-3.55, -0.12), colored=67, spacing=0.205, radius=0.05,
            palette=[m.YELLOW],
        )
        dots_text = fit(
            label("about 133 of 200 are never introduced", 23, m.WHITE), 5.6
        ).move_to([-3.55, -1.38, 0])

        # Askable queue sparkline from paper section 5.4(a).
        sx = lambda day: -6.05 + day * 0.25  # noqa: E731
        sy = lambda count: -2.02 + count * 0.0075  # noqa: E731
        ask_points = [[sx(day), sy(count), 0] for day, count in ASKABLE_BY_DAY]
        ask_line = m.VGroup(*[
            m.Line(ask_points[i], ask_points[i + 1], color=m.TEAL, stroke_width=6)
            for i in range(len(ask_points) - 1)
        ])
        ask_dots = m.VGroup(*[m.Dot(p, radius=0.055, color=m.TEAL) for p in ask_points])
        ask_label = fit(
            label("askable members: 45 on day 0 -> 0 by day 20", 20, m.TEAL), 5.5
        ).move_to([-3.55, -2.25, 0])

        # Acceptance-logit variance decomposition, paper section 5.4(b).
        bar_x0, bar_width, bar_y = 0.78, 5.55, 1.42
        segment_data = [
            (0.365, m.TEAL, "observable fit\n36.5%"),
            (0.452, m.PURPLE, "member bias\n45.2%"),
            (0.183, m.GREY_B, "pair term\n18.3%"),
        ]
        segments = m.VGroup()
        segment_labels = m.VGroup()
        cursor = bar_x0
        for share, color, text in segment_data:
            width = bar_width * share
            segments.add(
                m.Rectangle(width=width, height=0.58, color=color, fill_opacity=0.82, stroke_width=2)
                .move_to([cursor + width / 2, bar_y, 0])
            )
            segment_labels.add(
                fit(label(text, 21, color), min(2.25, width + 0.35)).move_to([cursor + width / 2, 0.72, 0])
            )
            cursor += width
        hidden_text = label("hidden share: about 64%", 31, m.PURPLE).move_to([3.55, -0.05, 0])
        oracle_frame = panel(5.45, 1.18, m.PURPLE).move_to([3.55, -1.02, 0])
        oracle = fit(
            label("ORACLE UPPER BOUND\nseeing hidden probabilities adds only about 5%", 22, m.WHITE),
            5.15,
        ).move_to([3.55, -1.02, 0])
        decomposition_note = fit(
            label("acceptance-logit decomposition: 30 worlds, 120,000 pairs", 19, m.GREY_B), 5.6
        ).move_to([3.55, -1.95, 0])

        rare_note = caption(
            "And the score is rare: a 120-episode assessment rests on only about 104 MSMI events.",
            color=m.ORANGE,
        )

        self.play(m.Write(title), run_time=0.8)
        self.play(
            m.Create(left_frame), m.Create(right_frame),
            m.FadeIn(left_title), m.FadeIn(right_title),
            run_time=0.8,
        )
        self.play(m.Create(ceiling_track), m.FadeIn(ceiling_fill), m.FadeIn(ceiling_text), run_time=0.8)
        self.play(
            m.LaggedStart(*[m.FadeIn(d) for d in dots], lag_ratio=0.003),
            run_time=1.25,
        )
        self.play(m.FadeIn(dots_text), m.Create(ask_line), m.FadeIn(ask_dots), m.FadeIn(ask_label), run_time=0.9)
        self.play(m.FadeIn(segments), m.FadeIn(segment_labels), run_time=0.9)
        self.play(m.FadeIn(hidden_text), m.Create(oracle_frame), m.FadeIn(oracle), run_time=0.8)
        self.play(m.FadeIn(decomposition_note), m.FadeIn(rare_note), run_time=0.55)
        self.wait(0.95)
        self.clear()

    # -- 8. a signal too small for the instrument -------------------------------

    def unresolved_signal(self) -> None:
        title = header("One real signal - still too small to call", color=m.GREEN)

        left_heading = fit(
            label("UNKNOWN IS NOT DISAGREEMENT", 25, m.GREEN), 5.8
        ).move_to([-4.05, 2.42, 0])
        context = fit(
            label("0 known agreements, development family", 21, m.GREY_B), 5.6
        ).move_to([-4.05, 2.02, 0])

        baseline = -1.85
        scale = 4.25
        grid = m.VGroup()
        grid_labels = m.VGroup()
        for value in (0.0, 0.25, 0.50):
            y = baseline + value * scale
            grid.add(dashed_line([-6.35, y, 0], [-1.75, y, 0], color=m.GREY_B, dash=0.12, gap=0.10, stroke_width=2))
            grid_labels.add(label(f"{value:.2f}", 19, m.GREY_B).move_to([-6.72, y, 0]))
        axis = m.Line([-6.35, baseline, 0], [-1.75, baseline, 0], color=m.WHITE, stroke_width=4)

        unknown_icons = label("?  ?  ?  ?", 27, m.GREY_B).move_to([-5.35, 1.48, 0])
        disagree_icons = label("X  X  X  X", 27, m.RED).move_to([-3.45, 1.48, 0])
        bar_unknown = vertical_bar(-5.35, baseline, 0.4918, scale, m.BLUE, width=1.15)
        bar_disagree = vertical_bar(-3.45, baseline, 0.2876, scale, m.RED, width=1.15)
        value_unknown = label("0.492", 30, m.BLUE).move_to([-5.35, baseline + 0.4918 * scale + 0.32, 0])
        value_disagree = label("0.288", 30, m.RED).move_to([-3.45, baseline + 0.2876 * scale + 0.32, 0])
        name_unknown = fit(label("0 known\n disagreements\nn=4,370", 19, m.WHITE), 1.55).move_to([-5.35, -2.48, 0])
        name_disagree = fit(label("4 known\n disagreements\nn=386", 19, m.WHITE), 1.55).move_to([-3.45, -2.48, 0])
        score_note = fit(
            label("agreement-only scoring gives both patterns 0", 21, m.YELLOW), 4.9
        ).move_to([-4.05, -3.05, 0])
        drop_arrow = m.Arrow(
            [-2.55, baseline + 0.4918 * scale, 0],
            [-2.55, baseline + 0.2876 * scale, 0],
            color=m.YELLOW, buff=0.05,
        )
        drop_label = label("-20.4 pts", 23, m.YELLOW).move_to([-1.62, -0.15, 0])

        candidate = chip(
            "disagreement_aware: +0.013 [-0.025, +0.051], p=0.524",
            m.GREEN, width=6.15, height=0.68, font_size=21,
        ).move_to([3.45, 2.48, 0])
        candidate_note = fit(
            label("only arm above greedy - seed W/T/L 46 / 29 / 45", 20, m.GREY_B), 5.8
        ).move_to([3.45, 1.86, 0])

        # Power curve plotted against log10(seed blocks).
        axes = m.Axes(
            x_range=[1.0, 3.4, 0.6], y_range=[0, 0.20, 0.05],
            x_length=5.55, y_length=2.75,
            axis_config={"include_numbers": False},
        ).move_to([3.45, -0.55, 0])
        curve = axes.plot(
            lambda lx: MDE_COEFF / (10 ** (lx / 2)),
            x_range=[1.0, 3.4], color=m.BLUE,
        )
        effect_line = m.Line(
            axes.c2p(1.0, 0.0132), axes.c2p(3.4, 0.0132),
            color=m.GREEN, stroke_width=5,
        )
        point_120 = m.Dot(
            axes.c2p(math.log10(120), MDE_COEFF / math.sqrt(120)),
            radius=0.085, color=m.BLUE,
        )
        point_2055 = m.Dot(
            axes.c2p(math.log10(2055), 0.0132),
            radius=0.085, color=m.GREEN,
        )
        point_120_label = fit(label("120 seeds\nMDE 0.055", 20, m.BLUE), 1.55)
        point_120_label.move_to(axes.c2p(2.10, 0.105))
        point_2055_label = fit(label("about 2,055 seeds\nto resolve +0.013", 20, m.GREEN), 2.15)
        point_2055_label.move_to(axes.c2p(3.02, 0.055))
        curve_ticks = m.VGroup(
            label("10", 19, m.GREY_B).move_to(axes.c2p(1.0, 0) + np.array([0, -0.32, 0])),
            label("100", 19, m.GREY_B).move_to(axes.c2p(2.0, 0) + np.array([0, -0.32, 0])),
            label("1,000", 19, m.GREY_B).move_to(axes.c2p(3.0, 0) + np.array([0, -0.32, 0])),
            label("0.20", 19, m.GREY_B).move_to(axes.c2p(1.0, 0.20) + np.array([-0.42, 0, 0])),
            label("0", 19, m.GREY_B).move_to(axes.c2p(1.0, 0) + np.array([-0.32, 0, 0])),
        )
        curve_xlabel = label("seed blocks (log scale)", 20, m.GREY_B).move_to([3.45, -2.48, 0])
        verdict = fit(
            label("Promising - disclosed - NOT ADOPTED", 27, m.GREEN), 5.9
        ).move_to([3.45, -3.02, 0])

        self.play(m.Write(title), run_time=0.8)
        self.play(m.FadeIn(left_heading), m.FadeIn(context), run_time=0.6)
        self.play(m.Create(grid), m.Create(axis), m.FadeIn(grid_labels), run_time=0.7)
        self.play(m.FadeIn(unknown_icons), m.FadeIn(bar_unknown, shift=m.UP), m.FadeIn(value_unknown), m.FadeIn(name_unknown), run_time=0.9)
        self.play(m.FadeIn(disagree_icons), m.FadeIn(bar_disagree, shift=m.UP), m.FadeIn(value_disagree), m.FadeIn(name_disagree), run_time=0.9)
        self.play(m.Create(drop_arrow), m.FadeIn(drop_label), m.FadeIn(score_note), run_time=0.7)
        self.play(m.FadeIn(candidate), m.FadeIn(candidate_note), run_time=0.7)
        self.play(m.Create(axes), m.FadeIn(curve_ticks), m.FadeIn(curve_xlabel), run_time=0.8)
        self.play(m.Create(curve), m.Create(effect_line), run_time=1.1)
        self.play(
            m.FadeIn(point_120), m.FadeIn(point_120_label),
            m.FadeIn(point_2055), m.FadeIn(point_2055_label),
            run_time=0.8,
        )
        self.play(m.FadeIn(verdict), run_time=0.55)
        self.wait(1.0)
        self.clear()

    # -- 9. outro -----------------------------------------------------------------

    def outro(self) -> None:
        line1 = label("Structure replicates.", 48, m.WHITE).move_to([0, 2.75, 0])
        line2 = label("Ranking does not.", 48, m.RED).move_to([0, 2.08, 0])
        lesson = fit(
            label("If a screen cannot resolve the spread among its options, its winner is not a finding.", 27, m.YELLOW),
            12.6,
        ).move_to([0, 1.32, 0])

        cards = m.VGroup(
            chip("ESTIMATE + INTERVAL\nwhat was observed", m.BLUE, width=3.9, height=1.25, font_size=23),
            chip("EVENT COUNT\nwhat the score rests on", m.YELLOW, width=3.9, height=1.25, font_size=23),
            chip("MINIMUM DETECTABLE EFFECT\nwhat could have been seen", m.GREEN, width=4.15, height=1.25, font_size=22),
        ).arrange(m.RIGHT, buff=0.32).move_to([0, 0.25, 0])

        practices = fit(
            label("Recover code, not descriptions. Publish the negative with its power.", 27, m.TEAL),
            12.2,
        ).move_to([0, -0.78, 0])

        credits = m.VGroup(
            label("SEQUENTIAL MATCHMAKING", 30, m.BLUE),
            label("A Reported +0.175 Advantage Does Not Survive Twelve Times the Data", 23, m.WHITE),
            label("Anadi Tripathi - Indian Institute of Technology Madras", 23, m.WHITE),
            label("github.com/Yash-Tripath1/sequential-matching-public-simulator-lab", 20, m.TEAL),
            label("DOI 10.5281/zenodo.23457651", 20, m.GREY_B),
        )
        for text in credits:
            fit(text, 12.3)
        credits.arrange(m.DOWN, buff=0.17).move_to([0, -2.05, 0])

        scope = caption("Synthetic simulator study - not evidence about real members or matching services.")

        self.play(m.Write(line1), run_time=0.8)
        self.play(m.Write(line2), run_time=0.8)
        self.play(m.FadeIn(lesson, shift=m.UP), run_time=0.7)
        self.play(
            m.LaggedStart(*[m.FadeIn(c, shift=m.UP) for c in cards], lag_ratio=0.25),
            run_time=1.3,
        )
        self.play(m.FadeIn(practices), run_time=0.6)
        self.play(
            m.LaggedStart(*[m.FadeIn(c, shift=m.UP) for c in credits], lag_ratio=0.18),
            run_time=1.1,
        )
        self.play(m.FadeIn(scope), run_time=0.5)
        self.wait(2.0)

    # -- film ---------------------------------------------------------------------

    def construct(self) -> None:
        self.next_section("opener")
        self.opener()
        self.next_section("daily-allocation-problem")
        self.daily_problem()
        self.next_section("phase-1-winner")
        self.phase_one()
        self.next_section("selection-traps-and-recovery")
        self.selection_traps()
        self.next_section("fresh-seed-replication")
        self.fresh_test()
        self.next_section("what-replicated")
        self.asking_matters()
        self.next_section("why-policies-blur")
        self.why_hard()
        self.next_section("unresolved-signal")
        self.unresolved_signal()
        self.next_section("outro")
        self.outro()
