#!/usr/bin/env python3
"""
Project Volusia — Local Chart Generator
Creates visualization charts for use in reports and FLUX 3 video generation.
"""

__version__ = "1.0.0"

import sqlite3
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "Tools" / "volusia_data" / "volusia.db"
OUTPUT_DIR = Path(__file__).parent / "Media"


def setup_output():
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR


def get_indicators():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT name, value, unit, source, vintage, fetched_at 
            FROM indicators 
            ORDER BY fetched_at DESC
        """).fetchall()
    return [
        {"name": r[0], "value": r[1], "unit": r[2], "source": r[3], "vintage": r[4], "fetched_at": r[5]} for r in rows
    ]


def create_population_chart():
    """Create population trend chart for Volusia County."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT name, value, vintage 
            FROM indicators 
            WHERE name LIKE 'total_population_pep_%'
            ORDER BY vintage
        """).fetchall()

    if not rows:
        return None

    years = [int(r[2]) for r in rows]
    values = [int(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    ax.plot(years, values, marker="o", linewidth=3, color="#e94560", markersize=10)
    ax.fill_between(years, values, alpha=0.3, color="#e94560")

    ax.set_title("Volusia County Population\n(2022-2024)", fontsize=16, color="white", pad=20)
    ax.set_xlabel("Year", fontsize=12, color="white")
    ax.set_ylabel("Population", fontsize=12, color="white")

    for i, (year, val) in enumerate(zip(years, values)):
        ax.annotate(
            f"{val:,}", (year, val), textcoords="offset points", xytext=(0, 10), ha="center", color="white", fontsize=10
        )

    ax.set_ylim(min(values) * 0.98, max(values) * 1.02)
    ax.grid(True, alpha=0.2, color="white")
    ax.tick_params(colors="white")

    plt.tight_layout()
    return fig


def create_unemployment_chart():
    """Create unemployment rate chart."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT name, value, vintage, source
            FROM indicators 
            WHERE name LIKE '%unemployment%'
        """).fetchall()

    if not rows:
        return None

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    rates = [float(r[1]) for r in rows if r[1]]
    labels = [f"{r[0].replace('_', ' ').title()}" for r in rows if r[1]]

    bars = ax.barh(labels, rates, color="#e94560", alpha=0.8)
    ax.set_xlabel("Rate (%)", fontsize=12, color="white")
    ax.set_title("Unemployment Rates", fontsize=16, color="white", pad=20)

    for bar, rate in zip(bars, rates):
        ax.annotate(
            f"{rate}%",
            (bar.get_width(), bar.get_y() + bar.get_height() / 2),
            va="center",
            color="white",
            fontsize=10,
            xytext=(5, 0),
        )

    ax.tick_params(colors="white")
    plt.tight_layout()
    return fig


def create_time_series_animation():
    """Create animated population time series."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT name, value, vintage
            FROM indicators 
            WHERE name LIKE 'total_population_pep_%'
            ORDER BY vintage
        """).fetchall()

    if len(rows) < 2:
        return None

    years = [int(r[2]) for r in rows]
    values = [int(r[1]) for r in rows]

    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    ax.set_xlim(min(years) - 1, max(years) + 1)
    ax.set_ylim(min(values) * 0.98, max(values) * 1.02)
    ax.set_title("Volusia County Population Growth", fontsize=16, color="white")
    ax.set_xlabel("Year", fontsize=12, color="white")
    ax.set_ylabel("Population", fontsize=12, color="white")

    (line,) = ax.plot([], [], color="#e94560", linewidth=3, marker="o", markersize=8)

    def init():
        line.set_data([], [])
        return (line,)

    def animate(i):
        line.set_data(years[: i + 1], values[: i + 1])
        if i == len(years) - 1:
            ax.annotate(
                f"{values[i]:,}",
                (years[i], values[i]),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                color="white",
                fontsize=12,
                fontweight="bold",
            )
        return (line,)

    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(years), interval=1000, blit=True)
    return anim


def main():
    setup_output()

    print("Generating Project Volusia visualizations...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    indicators = get_indicators()
    print(f"Found {len(indicators)} indicators in database")
    print()

    # Create population chart
    print("Creating population trend chart...")
    fig = create_population_chart()
    if fig:
        path = OUTPUT_DIR / "population_trend.png"
        fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
        print(f"  Saved: {path}")
        plt.close(fig)

    # Create unemployment chart
    print("Creating unemployment chart...")
    fig = create_unemployment_chart()
    if fig:
        path = OUTPUT_DIR / "unemployment_rates.png"
        fig.savefig(path, dpi=150, facecolor=fig.get_facecolor())
        print(f"  Saved: {path}")
        plt.close(fig)

    # Generate metadata
    metadata = {
        "generated_at": datetime.now().astimezone().isoformat(),
        "total_indicators": len(indicators),
        "charts": [
            {"name": "population_trend.png", "description": "Volusia County population 2022-2024"},
            {"name": "unemployment_rates.png", "description": "Unemployment rate indicators"},
        ],
        "sources": list(set(i["source"] for i in indicators)),
    }

    meta_path = OUTPUT_DIR / "charts_metadata.json"
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Saved: {meta_path}")

    print()
    print("✓ Chart generation complete")
    print()
    print("For video generation (when FLUX 3 API available):")
    print("  1. Use image-to-video to animate population_trend.png")
    print(
        "  2. Prompt: 'Data dashboard animation: Volusia population chart, gentle camera push-in, ambient office sound'"
    )
    print()

    return metadata


if __name__ == "__main__":
    main()
