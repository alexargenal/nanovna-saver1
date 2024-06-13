import itertools as it
import math
import matplotlib.pyplot as plt
from typing import Callable

import numpy as np
#need to load filename 
import os
import czt
#need to do computations on data

def load_data(filename: str) -> tuple:
    # Check if the file exists
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"File '{filename}' not found.")
    
    # Initialize empty arrays
    freq = []
    re = []
    im = []
    
    # Read the file line by line
    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('#'):
                continue
            

            # Split the line into columns
            columns = line.strip().split()
            
            # Convert the columns to float values
            frequency = float(columns[0])
            real = float(columns[2])
            imaginary = float(columns[3])
            
            # Append the values to the arrays
            freq.append(frequency)
            re.append(real)
            im.append(imaginary)
    
    # Convert the arrays to numpy arrays
    freq = np.array(freq)
    re = np.array(re)
    im = np.array(im)
    
    return freq, re, im

def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray) -> np.ndarray:
    # Calculate the number of samples
    num_samples = len(frequencies)
    
    # Initialize an empty array for the time domain signal
    freq_resp = np.zeros(num_samples, dtype=complex)
    
    # Iterate over each frequency and corresponding real and imaginary parts
    for i in range(num_samples):
        # Calculate the time domain value using inverse Fourier transform
        freq_resp[i] = real_parts[i] + 1j * imaginary_parts[i]
    time, time_domain_signal = czt.freq2time(frequencies, freq_resp, np.linspace(0, 0.4e-8, 1001))
    return time, time_domain_signal

# def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray) -> np.ndarray:
#     # Calculate the number of samples
#     num_samples = len(frequencies)
#     fs = (frequencies[1] - frequencies[0]) * num_samples
#     T = 1/fs
#     # Initialize an empty array for the time domain signal
#     time_domain_signal = np.zeros(num_samples, dtype=complex)
    
#     # Iterate over each frequency and corresponding real and imaginary parts
#     for n in range(num_samples):
#         # Calculate the time domain value using inverse Fourier transform
#         for k in range(num_samples):
#             mag = math.sqrt(real_parts[k]**2 + imaginary_parts[k]**2)
#             phase = math.atan2(imaginary_parts[k], real_parts[k])
#             time_domain_signal[n] += mag * math.exp(T * 1j * phase * k)
    
#     return time_domain_signal
   

def plot_time_domain(time, time_domain_signal: np.ndarray):
    # Generate the time axis
    #time = np.arange(len(time_domain_signal))
    
    # Plot the time domain signal
    plt.plot(time, np.abs(time_domain_signal))
    plt.xlabel('Time')
    plt.ylabel('Amplitude')
    plt.title('Time Domain Wave')
    plt.show()


def plot_time_domain_from_file(filename: str):
    # Load the data from the file
    freq, re, im = load_data(filename)
    
    # Convert the data to time domain
    time, time_domain_signal = convert_to_time_domain(freq, re, im)
    
    # Plot the time domain signal
    plot_time_domain(time, time_domain_signal)
    