"""
MIS20070 - Section 2: aggregate all survey responses into one ternary plot.

Usage:
    python analysis/plot_ternary.py responses.xlsx      # real data (Excel export of the Sheet)
    python analysis/plot_ternary.py --demo              # fake data, to test the chart

Output:
    analysis/ternary_aggregated.png   (for the report)
    analysis/summary.csv              (mean shares today vs 2060, for the 250-350 word analysis)

Needs: pip install pandas openpyxl matplotlib
"""
import sys, math
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
VALUES = ["equality", "belonging", "purpose"]
COL = {"equality": "#0a84ff", "belonging": "#ff9f0a", "purpose": "#bf5af2"}
INK, GREY, ACCENT = "#1d1d1f", "#8e8e93", "#0071e3"
H = math.sqrt(3) / 2
# same orientation as the website: Equality top, Belonging bottom-left, Purpose bottom-right
CORNER = {"equality": (0.5, H), "belonging": (0.0, 0.0), "purpose": (1.0, 0.0)}


def to_xy(e, b, p):
    s = e + b + p
    e, b, p = e / s, b / s, p / s
    x = e * CORNER["equality"][0] + b * CORNER["belonging"][0] + p * CORNER["purpose"][0]
    y = e * CORNER["equality"][1] + b * CORNER["belonging"][1] + p * CORNER["purpose"][1]
    return x, y


def load(path):
    df = pd.read_excel(path)
    need = [f"{t}_{v}" for t in ("today", "f2060") for v in VALUES]
    missing = [c for c in need if c not in df.columns]
    if missing:
        sys.exit(f"Missing columns in {path}: {missing}")
    return df[need].dropna().astype(float)


def demo(n=60, seed=7):
    r = np.random.default_rng(seed)
    t = r.dirichlet([3, 2, 5], n) * 100
    f = r.dirichlet([3, 5, 2.5], n) * 100
    cols = [f"today_{v}" for v in VALUES] + [f"f2060_{v}" for v in VALUES]
    return pd.DataFrame(np.hstack([t, f]), columns=cols)


def draw(df):
    fig, ax = plt.subplots(figsize=(8, 7.6), dpi=300)
    ax.set_aspect("equal"); ax.axis("off")
    ax.set_xlim(-0.1, 1.1); ax.set_ylim(-0.12, H + 0.1)

    # frame + 10% gridlines
    tri = np.array([CORNER["belonging"], CORNER["purpose"], CORNER["equality"], CORNER["belonging"]])
    ax.fill(tri[:, 0], tri[:, 1], color="#f5f5f7", zorder=0)
    for i in range(1, 10):
        t = i / 10
        for a, b, c in (("equality", "belonging", "purpose"), ("belonging", "purpose", "equality"),
                        ("purpose", "equality", "belonging")):
            p1 = {a: t, b: 1 - t, c: 0}; p2 = {a: t, c: 1 - t, b: 0}
            x1, y1 = to_xy(p1["equality"], p1["belonging"], p1["purpose"])
            x2, y2 = to_xy(p2["equality"], p2["belonging"], p2["purpose"])
            ax.plot([x1, x2], [y1, y2], color="#d2d2d7", lw=0.6 if i != 5 else 0.9, zorder=1)
    ax.plot(tri[:, 0], tri[:, 1], color="#c7c7cc", lw=1.2, zorder=2)

    # corner labels
    ax.text(0.5, H + 0.045, "Equality", ha="center", fontsize=13, weight="bold", color=COL["equality"])
    ax.text(-0.02, -0.06, "Belonging", ha="left", fontsize=13, weight="bold", color=COL["belonging"])
    ax.text(1.02, -0.06, "Purpose", ha="right", fontsize=13, weight="bold", color=COL["purpose"])

    T = np.array([to_xy(*r) for r in df[[f"today_{v}" for v in VALUES]].values])
    F = np.array([to_xy(*r) for r in df[[f"f2060_{v}" for v in VALUES]].values])

    # each respondent's shift, today -> 2060
    for (x0, y0), (x1, y1) in zip(T, F):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="-|>", lw=0.5, color=INK, alpha=0.18, shrinkA=3, shrinkB=3),
                    zorder=3)
    ax.scatter(T[:, 0], T[:, 1], s=26, color=GREY, alpha=0.6, edgecolor="white", lw=0.5, label="Today", zorder=4)
    ax.scatter(F[:, 0], F[:, 1], s=26, color=ACCENT, alpha=0.75, edgecolor="white", lw=0.5, label="2060", zorder=5)

    # average positions + headline arrow
    mt = to_xy(*df[[f"today_{v}" for v in VALUES]].mean().values)
    mf = to_xy(*df[[f"f2060_{v}" for v in VALUES]].mean().values)
    ax.annotate("", xy=mf, xytext=mt, arrowprops=dict(arrowstyle="-|>", lw=2.6, color=INK, shrinkA=8, shrinkB=9),
                zorder=6)
    ax.scatter(*mt, s=180, color="white", edgecolor=INK, lw=2.2, zorder=7, label="Average today")
    ax.scatter(*mf, s=200, color=ACCENT, edgecolor=INK, lw=2.2, zorder=8, label="Average 2060")

    ax.legend(loc="upper left", frameon=False, fontsize=9.5, bbox_to_anchor=(-0.06, 1.0))
    ax.set_title(f"How society values Equality, Belonging and Purpose: today vs 2060  (n = {len(df)})",
                 fontsize=11.5, color=INK, pad=6)
    fig.tight_layout()
    fig.savefig(OUT / "ternary_aggregated.png", bbox_inches="tight", facecolor="white")
    print(f"Saved {OUT / 'ternary_aggregated.png'}")


def summary(df):
    rows = []
    for v in VALUES:
        t, f = df[f"today_{v}"].mean(), df[f"f2060_{v}"].mean()
        rows.append({"value": v.title(), "today_mean_%": round(t, 1), "2060_mean_%": round(f, 1),
                     "shift_points": round(f - t, 1),
                     "share_who_increased_%": round(100 * (df[f"f2060_{v}"] > df[f"today_{v}"]).mean(), 1)})
    s = pd.DataFrame(rows)
    s.to_csv(OUT / "summary.csv", index=False)
    print(s.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        data = demo()
    elif len(sys.argv) > 1:
        data = load(sys.argv[1])
    else:
        sys.exit(__doc__)
    if len(data) < 50:
        print(f"Note: only {len(data)} responses - the brief requires at least 50.")
    draw(data)
    summary(data)
