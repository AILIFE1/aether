import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve2d

def double_slit_simulation():
    # Simple 2D wave interference simulation
    x = np.linspace(-10, 10, 400)
    y = np.linspace(-10, 10, 400)
    X, Y = np.meshgrid(x, y)
    
    # Single slit wave
    single = np.exp(-((X**2 + Y**2)/2)) * np.cos(2 * np.pi * 5 * X)
    
    # Double slit
    slit1 = np.exp(-(((X-2)**2 + Y**2)/2)) * np.cos(2 * np.pi * 5 * X)
    slit2 = np.exp(-(((X+2)**2 + Y**2)/2)) * np.cos(2 * np.pi * 5 * X)
    double = slit1 + slit2
    
    # Interference
    interference = convolve2d(double, single, mode='same')
    
    plt.figure(figsize=(10, 6))
    plt.imshow(interference, extent=[-10,10,-10,10], cmap='viridis')
    plt.title('Double-Slit Interference Pattern')
    plt.xlabel('Position')
    plt.ylabel('Position')
    plt.colorbar(label='Intensity')
    plt.savefig('double_slit.png')
    plt.close()
    
    return 'Double-slit interference pattern generated. Classic quantum mystery reproduced in simulation.'

if __name__ == '__main__':
    print(double_slit_simulation())
