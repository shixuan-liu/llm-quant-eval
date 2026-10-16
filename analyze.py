"""Summarise the GSM8K and contamination-probe runs: tables with confidence intervals,
paired significance tests, and the charts used in the README.

Reads results/gsm8k_raw.csv and results/fresh_raw.csv; writes results/summary.md and charts/*.png.

Statistics, all standard-library:
- Wilson 95% interval for each accuracy (better than ±1.96·SE at n=100 and at extreme rates).
- Exact McNemar test for two models on the same items. It uses only the items where the two
  disagree, so it is far more sensitive than comparing two accuracies as if they were independent.
- Cluster bootstrap over templates for the contamination probe: the 5 variants of one template
  are correlated, so we resample whole templates, not individual items.
"""
from math import comb, sqrt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODELS = pd.DataFrame([
    # model,                           family,     label,   bits, size_gb
    ("llama3.2:1b-instruct-q3_K_M",   "Llama 3.2 1B", "q3_K_M", 3,  0.69),
    ("llama3.2:1b-instruct-q4_K_M",   "Llama 3.2 1B", "q4_K_M", 4,  0.81),
    ("llama3.2:1b-instruct-q6_K",     "Llama 3.2 1B", "q6_K",   6,  1.0),
    ("llama3.2:1b-instruct-q8_0",     "Llama 3.2 1B", "q8_0",   8,  1.3),
    ("llama3.2:1b-instruct-fp16",     "Llama 3.2 1B", "fp16",   16, 2.5),
    ("gemma3:1b-it-qat",              "Gemma 3 1B",   "QAT q4", 4,  1.0),
    ("gemma3:1b-it-q4_K_M",           "Gemma 3 1B",   "q4_K_M", 4,  0.81),
    ("gemma3:1b-it-fp16",             "Gemma 3 1B",   "fp16",   16, 2.0),
    ("qwen3.5:2b-q4_K_M",             "Qwen 3.5 2B",  "q4_K_M", 4,  1.9),
    ("qwen3.5:2b-q8_0",               "Qwen 3.5 2B",  "q8_0",   8,  2.7),
], columns=["model", "family", "label", "bits", "size_gb"])

PAIRS = [  # (A, B, question)
    ("llama3.2:1b-instruct-q3_K_M", "llama3.2:1b-instruct-fp16", "Q1"),
    ("llama3.2:1b-instruct-q4_K_M", "llama3.2:1b-instruct-fp16", "Q1"),
    ("llama3.2:1b-instruct-q6_K",   "llama3.2:1b-instruct-fp16", "Q1"),
    ("llama3.2:1b-instruct-q8_0",   "llama3.2:1b-instruct-fp16", "Q1"),
    ("llama3.2:1b-instruct-q3_K_M", "llama3.2:1b-instruct-q4_K_M", "Q1"),
    ("gemma3:1b-it-qat",            "gemma3:1b-it-q4_K_M",       "Q2"),
    ("gemma3:1b-it-qat",            "gemma3:1b-it-fp16",         "Q2"),
    ("gemma3:1b-it-q4_K_M",         "gemma3:1b-it-fp16",         "Q2"),
    ("qwen3.5:2b-q4_K_M",           "llama3.2:1b-instruct-fp16", "Q3"),
    ("qwen3.5:2b-q4_K_M",           "gemma3:1b-it-fp16",         "Q3"),
    ("qwen3.5:2b-q4_K_M",           "qwen3.5:2b-q8_0",           "Q3"),
]

FAMILY_COLOR = {"Llama 3.2 1B": "#2a78d6", "Gemma 3 1B": "#eb6834", "Qwen 3.5 2B": "#1baf7a"}
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
BOOT, SEED = 10_000, 42


# ── statistics ─────────────────────────────────────────────────────────────────────────
def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def mcnemar_exact(a: pd.Series, b: pd.Series) -> tuple[int, int, float]:
    """a, b: correct/incorrect on the same items. Returns (#a only, #b only, two-sided p)."""
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    n = only_a + only_b
    if n == 0:
        return only_a, only_b, 1.0
    tail = sum(comb(n, k) for k in range(min(only_a, only_b) + 1)) / 2 ** n
    return only_a, only_b, min(1.0, 2 * tail)


def cluster_bootstrap(diffs: pd.DataFrame, rng: np.random.Generator) -> tuple[float, float, float]:
    """diffs: one row per (model, template) with column d. Resample templates, keeping every
    model's row for a drawn template together."""
    by_template = diffs.groupby("source_id")["d"].apply(np.array)
    templates = by_template.index.to_numpy()
    means = []
    for _ in range(BOOT):
        draw = rng.choice(templates, size=len(templates), replace=True)
        means.append(np.concatenate([by_template[t] for t in draw]).mean())
    lo, hi = np.percentile(means, [2.5, 97.5])
    return diffs["d"].mean(), lo, hi


# ── tables ─────────────────────────────────────────────────────────────────────────────
def accuracy_table(g: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for m in MODELS.itertuples():
        d = g[g.model == m.model]
        k, n = int(d.correct.sum()), len(d)
        lo, hi = wilson(k, n)
        rows.append({
            "model": m.model, "family": m.family, "label": m.label, "bits": m.bits, "size_gb": m.size_gb,
            "n": n, "acc": k / n, "ci_lo": lo, "ci_hi": hi,
            "strict_acc": (d.correct & d.formatted).mean(),
            "format_rate": d.formatted.mean(),
            "tok_s": d.token_per_s.median(),
            "tokens": d.eval_count.median(),
            "truncated": (d.eval_count >= 512).mean(),
        })
    return pd.DataFrame(rows)


def mcnemar_table(g: pd.DataFrame) -> pd.DataFrame:
    wide = g.pivot(index="item_id", columns="model", values="correct").astype(bool)
    label = MODELS.set_index("model").apply(lambda r: f"{r.family.split()[0]} {r.label}", axis=1)
    rows = []
    for a, b, q in PAIRS:
        only_a, only_b, p = mcnemar_exact(wide[a], wide[b])
        rows.append({"question": q, "A": label[a], "B": label[b],
                     "acc_A": wide[a].mean(), "acc_B": wide[b].mean(),
                     "A_only": only_a, "B_only": only_b, "p": p})
    return pd.DataFrame(rows)


def contamination(g: pd.DataFrame, f: pd.DataFrame) -> tuple[pd.DataFrame, tuple]:
    """Per (model, template): original correct (0/1) minus share of its 5 variants correct."""
    orig = g[g.item_id < 20][["model", "item_id", "correct"]].rename(
        columns={"item_id": "source_id", "correct": "orig"})
    var = f.groupby(["model", "source_id"], as_index=False).correct.mean().rename(columns={"correct": "var"})
    diffs = orig.merge(var, on=["model", "source_id"])
    diffs["d"] = diffs["orig"].astype(float) - diffs["var"]

    rng = np.random.default_rng(SEED)
    per_model = []
    for m in MODELS.itertuples():
        d = diffs[diffs.model == m.model]
        mean, lo, hi = cluster_bootstrap(d, rng)
        per_model.append({"model": m.model, "family": m.family, "label": m.label,
                          "orig_acc": d.orig.mean(), "variant_acc": d["var"].mean(),
                          "gap": mean, "gap_lo": lo, "gap_hi": hi})
    pooled = cluster_bootstrap(diffs, rng)
    return pd.DataFrame(per_model), pooled


# ── charts ─────────────────────────────────────────────────────────────────────────────
def style(ax, title):
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def pct(ax):
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))


def chart_llama(acc: pd.DataFrame):
    d = acc[acc.family == "Llama 3.2 1B"].sort_values("bits")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(9, 3.6))
    c = FAMILY_COLOR["Llama 3.2 1B"]
    x = range(len(d))
    a1.errorbar(x, d.acc, yerr=[d.acc - d.ci_lo, d.ci_hi - d.acc], color=c, lw=2, marker="o", ms=6,
                capsize=0, elinewidth=1.2, ecolor=c)
    a1.set_ylim(0, 0.7); pct(a1)
    style(a1, "GSM8K accuracy (95% CI)")
    a2.plot(x, d.tok_s, color=c, lw=2, marker="o", ms=6)
    a2.set_ylim(0, d.tok_s.max() * 1.2)
    style(a2, "Generation speed (median tokens/s)")
    for ax in (a1, a2):
        ax.set_xticks(list(x), d.label)
    fig.suptitle("Llama 3.2 1B: accuracy holds to 4-bit, drops at 3-bit; speed doubles",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig("charts/llama_bits.png", dpi=200)


def chart_gemma(acc: pd.DataFrame):
    d = acc[acc.family == "Gemma 3 1B"].set_index("label").loc[["QAT q4", "q4_K_M", "fp16"]]
    fig, ax = plt.subplots(figsize=(5, 3.6))
    c = FAMILY_COLOR["Gemma 3 1B"]
    x = range(len(d))
    ax.errorbar(x, d.acc, yerr=[d.acc - d.ci_lo, d.ci_hi - d.acc], fmt="o", color=c, ms=7,
                capsize=0, elinewidth=1.2)
    for i, v in zip(x, d.acc):
        ax.annotate(f"{v:.0%}", (i, v), xytext=(10, 0), textcoords="offset points",
                    va="center", fontsize=9, color=MUTED)
    ax.set_xticks(list(x), d.index); ax.set_xlim(-0.5, 2.5); ax.set_ylim(0, 0.7); pct(ax)
    style(ax, "Gemma 3 1B: QAT vs post-training 4-bit vs fp16")
    fig.tight_layout()
    fig.savefig("charts/gemma_qat.png", dpi=200)


# Llama q4 and Gemma q4 have the same size and accuracy; nudge them apart so both are visible.
X_NUDGE = {"llama3.2:1b-instruct-q4_K_M": -0.03, "gemma3:1b-it-q4_K_M": 0.03,
           "llama3.2:1b-instruct-q6_K": -0.03, "gemma3:1b-it-qat": 0.03}
LABEL_AT = {"llama3.2:1b-instruct-q4_K_M": (-8, 0, "right"), "llama3.2:1b-instruct-q6_K": (6, 12, "left"),
            "gemma3:1b-it-q4_K_M": (6, -16, "left"), "gemma3:1b-it-qat": (8, -4, "left")}


def chart_size(acc: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(7, 4.2))
    for fam, d in acc.groupby("family", sort=False):
        c = FAMILY_COLOR[fam]
        x = d.size_gb + d.model.map(X_NUDGE).fillna(0)
        ax.errorbar(x, d.acc, yerr=[d.acc - d.ci_lo, d.ci_hi - d.acc], fmt="o", color=c,
                    ms=7, capsize=0, elinewidth=1, label=fam,
                    markeredgecolor="white", markeredgewidth=1.5)
        for xi, r in zip(x, d.itertuples()):
            dx, dy, ha = LABEL_AT.get(r.model, (8, -3, "left"))
            ax.annotate(r.label, (xi, r.acc), xytext=(dx, dy), textcoords="offset points",
                        fontsize=8, color=MUTED, ha=ha)
    ax.set_xlabel("Model file size (GB)", fontsize=9, color=MUTED)
    ax.set_xlim(0.4, 3.0); ax.set_ylim(0, 0.9); pct(ax)
    ax.legend(frameon=False, fontsize=9, loc="upper left")
    style(ax, "Same memory budget: a 2B model at 4-bit beats 1B models at full precision")
    fig.tight_layout()
    fig.savefig("charts/size_vs_accuracy.png", dpi=200)


def chart_contamination(cont: pd.DataFrame, pooled):
    d = cont.iloc[::-1].reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.6))
    y = np.arange(len(d))
    ax.errorbar(d.gap, y, xerr=[d.gap - d.gap_lo, d.gap_hi - d.gap], fmt="o", ms=6, capsize=0,
                elinewidth=1.2, color="#2a78d6", ecolor="#2a78d6")
    ax.axvline(0, color=MUTED, lw=1)
    mean, lo, hi = pooled
    ax.axvspan(lo, hi, color=GRID, alpha=0.6, lw=0)
    ax.set_yticks(y, [f"{r.family.split()[0]} {r.label}" for r in d.itertuples()])
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:+.0%}"))
    ax.set_xlabel("Original minus variant accuracy (positive = better on the published problem)",
                  fontsize=9, color=MUTED)
    style(ax, "Contamination probe: no model does better on the published problems")
    ax.set_title(ax.get_title(loc="left"), loc="left", fontsize=11, color=INK, pad=22)
    ax.text(0, 1.01, f"Dots: per model, 95% cluster-bootstrap CI.  Shaded: all models pooled, "
            f"{mean:+.1%} [{lo:+.1%}, {hi:+.1%}]", transform=ax.transAxes, fontsize=8, color=MUTED, va="bottom")
    ax.grid(axis="x", color=GRID, linewidth=0.8); ax.grid(axis="y", visible=False)
    fig.tight_layout()
    fig.savefig("charts/contamination.png", dpi=200)


# ── report ─────────────────────────────────────────────────────────────────────────────
def md(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(lines)


if __name__ == "__main__":
    g = pd.read_csv("results/gsm8k_raw.csv")
    f = pd.read_csv("results/fresh_raw.csv")

    acc = accuracy_table(g)
    mc = mcnemar_table(g)
    cont, pooled = contamination(g, f)

    chart_llama(acc); chart_gemma(acc); chart_size(acc); chart_contamination(cont, pooled)

    a = acc.assign(
        model=acc.family + " " + acc.label,
        accuracy=[f"{r.acc:.0%} [{r.ci_lo:.0%}–{r.ci_hi:.0%}]" for r in acc.itertuples()],
        strict=acc.strict_acc.map("{:.0%}".format),
        format=acc.format_rate.map("{:.0%}".format),
        tok_s=acc.tok_s.round(0).astype(int),
        size=acc.size_gb.map("{:.1f} GB".format),
        truncated=acc.truncated.map("{:.0%}".format),
    )[["model", "size", "accuracy", "strict", "format", "tok_s", "truncated"]]
    m = mc.assign(acc_A=mc.acc_A.map("{:.0%}".format), acc_B=mc.acc_B.map("{:.0%}".format),
                  p=mc.p.map("{:.3f}".format))
    c = cont.assign(
        model=cont.family + " " + cont.label,
        original=cont.orig_acc.map("{:.0%}".format),
        variants=cont.variant_acc.map("{:.0%}".format),
        gap=[f"{r.gap:+.0%} [{r.gap_lo:+.0%}, {r.gap_hi:+.0%}]" for r in cont.itertuples()],
    )[["model", "original", "variants", "gap"]]

    with open("results/summary.md", "w") as out:
        out.write("## Accuracy on GSM8K (n=100)\n\n" + md(a) + "\n\n")
        out.write("## Paired comparisons (exact McNemar)\n\n" + md(m) + "\n\n")
        out.write("## Contamination probe (20 originals × 5 variants)\n\n" + md(c) + "\n\n")
        out.write(f"Pooled gap: {pooled[0]:+.1%} [{pooled[1]:+.1%}, {pooled[2]:+.1%}]\n")
    print(open("results/summary.md").read())
