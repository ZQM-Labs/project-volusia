#!/usr/bin/env python3
"""
Project Volusia — Video Generation Script
Produces simple data visualization videos using matplotlib + imageio.

Works as fallback when FLUX 3 API is unavailable.
"""

__version__ = "1.0.0"

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

MEDIA_DIR = Path(__file__).parent / "Media"


def create_data_card_video():
    """Create a simple data card video from existing charts."""
    try:
        import imageio
        from PIL import Image
    except ImportError:
        print("imageio not installed, skipping video generation")
        return None

    # Load existing charts
    charts = []
    for chart_name in ["population_trend.png", "unemployment_rates.png"]:
        chart_path = MEDIA_DIR / chart_name
        if chart_path.exists():
            img = Image.open(chart_path)
            # Convert to RGB if needed
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            charts.append(np.array(img))

    if not charts:
        print("No charts found for video generation")
        return None

    # Create simple pan/zoom animation by scaling images
    frames = []
    n_frames = 30  # 1 second at 30fps

    for chart_idx, chart in enumerate(charts):
        for i in range(n_frames):
            scale = 1 + 0.1 * np.sin(i * 2 * np.pi / n_frames)
            zoomed = np.array(
                Image.fromarray(chart).resize((int(chart.shape[1] * scale), int(chart.shape[0] * scale)), Image.LANCZOS)
            )
            # Black border
            h, w = zoomed.shape[:2]
            canvas = np.zeros((h + 80, w + 80, 3), dtype=np.uint8)
            canvas[40 : 40 + h, 40 : 40 + w] = zoomed
            frames.append(canvas)

        # Hold frame for 1 second
        for _ in range(15):
            frames.append(canvas)

    # Save as MP4
    output_path = MEDIA_DIR / "volusia_data_summary.mp4"
    imageio.mimwrite(output_path, frames, fps=15)
    print(f"Created video: {output_path}")
    return output_path


def create_simple_animated_chart():
    """Create a simple animated line chart."""
    try:
        import imageio
    except ImportError:
        print("imageio not installed")
        return None

    # Create matplotlib animation frames
    fig, ax = plt.subplots(figsize=(10, 6), facecolor="#1a1a2e")
    ax.set_facecolor("#16213e")

    # Sample population data
    years = [2022, 2023, 2024]
    values = [580529, 591936, 601107]

    frames = []
    for i in range(1, len(years) + 1):
        ax.clear()
        ax.set_facecolor("#16213e")
        ax.set_xlim(2021, 2025)
        ax.set_ylim(min(values) * 0.98, max(values) * 1.02)
        ax.set_title("Volusia County Population\nData as of 2024 Q3", fontsize=16, color="white")
        ax.set_xlabel("Year", fontsize=12, color="white")
        ax.set_ylabel("Population", fontsize=12, color="white")
        ax.plot(years[:i], values[:i], marker="o", linewidth=3, color="#e94560", markersize=10)
        ax.grid(True, alpha=0.2, color="white")
        ax.tick_params(colors="white")

        # Add count
        for x, y in zip(years[:i], values[:i]):
            ax.annotate(
                f"{y:,}", (x, y), xytext=(0, 10), textcoords="offset points", ha="center", color="white", fontsize=10
            )

        fig.canvas.draw()
        frame = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        frame = frame.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(frame)

        # Hold each frame
        for _ in range(10):
            frames.append(frame)

    plt.close()

    output_path = MEDIA_DIR / "population_growth_animation.mp4"
    imageio.mimwrite(output_path, frames, fps=10)
    print(f"Created animation: {output_path}")
    return output_path


def main():
    print("Creating Project Volusia video content...")
    print()

    # Try to create videos
    video1 = create_data_card_video()
    video2 = create_simple_animated_chart()

    print()
    print("✓ Video generation attempts complete")
    if video1 or video2:
        print(f"  Generated files in: {MEDIA_DIR}")
    else:
        print()
        print("To generate videos, install imageio:")
        print("  python -m pip install imageio pillow")


if __name__ == "__main__":
    main()
