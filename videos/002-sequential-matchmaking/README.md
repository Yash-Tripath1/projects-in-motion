# 002 — Sequential Matchmaking

Part of [**Projects in Motion**](../../README.md) — animated explainers published with their source code.

**When a winning policy meets twelve times the data, does the win survive?**

A 75-second animated film about Anadi Tripathi's sequential reciprocal-matching
study and its paper, [*A Reported +0.175 Advantage Does Not Survive Twelve
Times the Data*](https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab/blob/main/PAPER.md).
The paper asks whether a clarification policy that appeared to beat a supplied
greedy baseline in a ten-seed screen still wins on 120 fresh, paired simulator
worlds. It does not.

▶️ **Watch: [`SequentialMatchmaking_slow_0.5x.mp4`](SequentialMatchmaking_slow_0.5x.mp4)** —
the readable cut: 150.93 s (half speed), 1920×1080, constant 60 fps.
The original render is [`SequentialMatchmaking.mp4`](SequentialMatchmaking.mp4):
75.47 s, 1920×1080, on a 60 fps timeline. Both files contain the same scenes,
visuals, wording and order. The readable cut doubles the original timestamps
and restores the final end-card hold, which would otherwise be shortened by
the source file's variable frame timing.

> **Scope:** every member, preference, introduction and outcome in the study is
> synthetic simulator data. The film is about evaluation design in that public
> simulator; it is not evidence about real people or real matching services.

## The story in 9 scenes

Times below are shown for the original render and the half-speed readable cut.

| Original | Slow cut | Scene | What you see |
|---:|---:|---|---|
| 0:00 | 0:00 | **A winner under suspicion** | A synthetic member network and the Phase 1 headline: **+0.175**. The opening question is whether that is a real policy edge or the maximum of a noisy screen. |
| 0:07 | 0:14 | **The daily allocation problem** | In each 200-member world, a policy observes the current pool, spends up to 12 clarification units, refreshes the answers, then proposes pairs. A hard-constraint bundle costs 3 units and a soft field costs 1. Missing hard information blocks an introduction; reciprocal hard rules must pass in both directions. |
| 0:17 | 0:34 | **Phase 1 found a clear winner** | Across 17 configurations, 10 seeds and 60 episodes per arm, the incumbent scored **0.525** against greedy's **0.350** MSMI/100: **+0.175 [+0.092, +0.258], p = 0.016**. |
| 0:25 | 0:49 | **Three reasons not to trust the trophy yet** | The estimate was the maximum of 17 configurations; pilot seeds **101, 102 and 303** were reused inside the measurement set; and a 60-episode design resolved only about **0.234**, coarser than the reported gap. Before retesting, the rebuilt configuration reproduced the stored record on **60/60 episodes**. A prose-based signed variant scored **0.367**, not 0.525. |
| 0:33 | 1:05 | **120 fresh seeds** | On seeds 1101–1220, paired world-for-world, greedy scored **0.402** and the incumbent **0.369**. Their difference was **−0.033 [−0.090, +0.025], p = 0.356**. The Phase 1 and Phase 2 estimates are **7.09 standard errors apart**. Each tile in the film is one paired seed. |
| 0:42 | 1:24 | **What replicated** | Removing clarification is the large effect: **greedy − no_ask = +0.304 [+0.261, +0.349]**. Greedy also beats random feasible pairing by **+0.070 [+0.023, +0.116]**. The structure replicates even though the incumbent's ranking does not. |
| 0:49 | 1:39 | **Why competent policies look alike** | Coverage reaches **97.8% of its structural ceiling**, about **133 of 200** members are never introduced, and roughly **64%** of acceptance-logit variation is hidden by construction. Even an oracle using the hidden probabilities would add only about **5%**. |
| 0:58 | 1:55 | **One signal too small to call** | Unknown is not disagreement: with zero known agreements, observed acceptance falls from **0.492** to **0.288** when four known disagreements are present. The resulting `disagreement_aware` arm is **+0.013 [−0.025, +0.051], p = 0.524** — promising, disclosed, and deliberately not adopted. Resolving it would require about **2,055 seeds**. |
| 1:08 | 2:15 | **The reporting standard** | **Structure replicates. Ranking does not.** Report an estimate with its interval, the event count behind it, and the minimum detectable effect. Recover code rather than descriptions, and publish a negative result with its power. |

## Sign convention

Every paired difference in the film is labelled explicitly. The headline forest
plot uses

```text
potential_ask − greedy
```

so Phase 1 is **+0.175** and Phase 2 is **−0.033**. This follows the paper's
Figure 1 and `results/analysis_120seeds_four_arm.json`. Where another contrast
is used — for example, greedy − no_ask — the film prints that order beside the
number.

## Source code and production notes

`scene.py` contains the complete Python source used to generate the film. It
is organised into nine named sections — `opener`, `daily_problem`,
`phase_one`, `selection_traps`, `fresh_test`, `asking_matters`, `why_hard`,
`unresolved_signal` and `outro` — so the mechanism, result and caveats can be
inspected independently.

The shared Python dependency is pinned in the repository-root
[`requirements.txt`](../../requirements.txt). This entry uses Python 3.13
or 3.14.

```bash
python -m pip install -r ../../requirements.txt
```

Production checks completed for this entry:

- Layout inspection passed all **90 sampled moments** with no reported
  overlaps or clipped text.
- The original was rendered at 1920×1080 in **453.5 seconds** on a headless
  CPU system.
- The readable cut was decoded and checked at **9,056 frames** and
  **150.93 seconds**.
- `poster.jpg` is a real frame from the 120-seed forest-plot scene at about
  41.3 seconds in the original render.
- Temporary storyboard sheets are not retained in the repository.

## Data included with the film

### `data/per_seed_primary_120.csv`

One row for each fresh seed from 1101 to 1220, extracted from the project
repository's `results/analysis_120seeds_four_arm.json`. Columns contain the
per-seed primary MSMI/100 scores for `greedy`, `potential_ask`,
`disagreement_aware` and `potential_ask_greedy`, plus two paired differences
against greedy. The 120 coloured tiles in the replication scene are derived
from these rows in seed-ID order.

The column means reproduce the published totals:

| Arm | Mean MSMI/100 | Events implied by the per-seed scores |
|---|---:|---:|
| greedy | 0.4021 | 579 |
| potential_ask | 0.3694 | 532 |
| disagreement_aware | 0.4153 | 598 |
| potential_ask_greedy | 0.3611 | 520 |

### `data/film_numbers.csv`

A claim-by-claim index of the quantitative statements visible in the film:
scene, claim, value, qualifying detail, and the paper section or repository
result file behind it.

## Where the main claims come from

The film uses the attached paper as its narrative source and the public
project repository for executable definitions and result tables. The attached
PDF is byte-identical to the repository's `PAPER.pdf` (SHA-256
`8e6207ba408c11d1e17d927cc2249b9dc8ebfc8b0686e119c0745bfd37e432d9`).

| Film material | Project source |
|---|---|
| Daily observe–ask–refresh–match loop, 12-unit budget, hard-bundle cost 3, soft-field cost 1 | `docs/DATA_CONTRACT.md`, `docs/POLICY_INTERFACE.md`, paper §2 |
| Reciprocal feasibility, unknown hard fields, declined fields and no repeated introductions | `docs/DATA_CONTRACT.md`; executable semantics in `kit.py` |
| Six scenario families and MSMI/100 definition | Paper §§2.2–2.3 |
| Phase 1 design, +0.175 result, selection mechanisms and 0.234 resolution | Paper §§3.1–3.4 |
| 60/60 reconstruction and the signed/unsigned 0.158 coding gap | Paper §4.1 and Appendix A.4 |
| Fresh-seed design and seed-block inference | Paper §4.2 |
| Phase 2 incumbent contrast, seed wins/ties/losses and 7.09-SE separation | Paper §5.1; `results/analysis_120seeds_four_arm.json`; `results/greedy_vs_potential_120seeds.json` |
| Four-arm scores, intervals, events and asking contrasts | Paper §5.2; `results/primary_120seeds.csv`; `results/contrasts_120seeds.csv` |
| Ceiling, unserved members, askable queue, hidden variance and oracle bound | Paper §5.4 |
| 0.492 versus 0.288 acceptance comparison | `results/calibration_report.json`, `unknown_vs_disagreement`, development family with zero known agreements |
| `disagreement_aware`, 0.055 MDE and approximately 2,055 seeds | Paper §5.3; Figure 3 calculation in `code/analysis/make_figures.py` |
| “Structure replicates; ranking does not” and evaluation recommendations | Paper §§6.1–6.3 |

Repository snapshot read for this film: commit
`7e00189b9b98715ac7db860b1a10b392c14a2052` (20 Oct 2026). The paper itself
pins commit `e9515580aac62e818113f5aa17c4de1780697eca`.

## What is schematic, honestly

- The member network, profile cards and coloured member grids are illustrations.
  The two 200-dot grids each contain exactly 200 dots, but dot position and
  colour do not encode attributes of particular simulated members.
- The profile cards show three short labels — age, zones and times — as a
  readable subset. The simulator checks the complete reciprocal hard-field
  set, declined status, availability and whether the pair is new.
- In the “max of 17” card, the heights of the 17 anonymous bars are schematic.
  The count, the fact that the reported estimate was the screen maximum, and
  all printed statistics are from the paper.
- In the supply-ceiling panel, 67 gold dots and 133 muted dots visualise the
  rounded average of about 133.3 never introduced per 200. They are not one
  particular episode.
- The power curve is the paper's normal-approximation calculation for the
  `disagreement_aware` contrast: paired SD 0.2136 and
  \((1.95996+0.84162)\times0.2136/\sqrt n\). Its 0.055 MDE at 120 seeds is
  contrast-specific; the headline incumbent contrast has paired SD 0.3211,
  for which the same formula gives about 0.082.
- The code-recovery result is described as a reconstruction check, not proof
  that the rebuilt code is character-for-character the lost original. That is
  also the paper's stated limitation.

## Credits & licences

- **Research, simulator work and paper:** Anadi Tripathi
  ([@Yash-Tripath1](https://github.com/Yash-Tripath1)), Indian Institute of Technology Madras —
  [sequential-matching-public-simulator-lab](https://github.com/Yash-Tripath1/sequential-matching-public-simulator-lab).
- **Archived concept DOI:** [10.5281/zenodo.23457651](https://doi.org/10.5281/zenodo.23457651).
- **This film's code and notes:** MIT (see the repository-root
  [`LICENSE`](../../LICENSE)). Project data and paper material retain the
  terms stated in their source repository.

## Files

```text
002-sequential-matchmaking/
├── SequentialMatchmaking_slow_0.5x.mp4  # readable cut, 2:31 (recommended)
├── SequentialMatchmaking.mp4            # original render, 1:15
├── scene.py                             # complete film source
├── poster.jpg                           # still from the 120-seed result scene
├── data/
│   ├── film_numbers.csv                 # claim-by-claim source index
│   └── per_seed_primary_120.csv         # 120-seed scores and paired differences
└── README.md                            # this file
```

## Use it in the project repository

Link the readable cut from the research repository's README beside the paper
headline, or attach `SequentialMatchmaking_slow_0.5x.mp4` to a release. The
poster also works as the still above the paper's “headline finding” section:
it carries the design, both intervals, event counts and seed-level outcome in
one frame.
