import matplotlib.pyplot as plt
import os

def save_plot(fig, filename: str):
    """Save a matplotlib figure to the plots/ folder with high resolution."""
    os.makedirs("plots", exist_ok=True)
    path = f"plots/{filename}"
    fig.savefig(path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"✅ Plot saved: {path}")
    return path
