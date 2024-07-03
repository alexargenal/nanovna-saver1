#This module is used to compute the time domain of sweep data, calculate the relative permittivity of a material,
#and use matplotlib plots to visualize the time domain as well as permittivity calcs over time.

import matplotlib.pyplot as plt


import numpy as np
#need to load filename 
import os
import czt
import tkinter as tk
import datetime
from tkinter import filedialog


def calculate_epsilon_r(data1: tuple, data2: tuple, distance: float = 0) -> float:
    #this function finds permittivity from the current sweep and set reference through the software

    # Convert the data to time domain for the first set
    time1, time_domain_signal1 = convert_to_time_domain(data1[0], data1[1], data1[2])
    
    # Convert the data to time domain for the second set
    time2, time_domain_signal2 = convert_to_time_domain(data2[0], data2[1], data2[2])
    
    # Find the indices of the peak values
    index1 = np.argmax(abs(time_domain_signal1))
    index2 = np.argmax(abs(time_domain_signal2))
    
    # Find the time difference between the peaks
    time_difference = time1[index1] - time2[index2]
    # Calculate the epsilon r value
    c = 3e8
    
    epsilon_r = (1 + (time_difference * c) / (distance * 10 ** -3)) ** 2
    
    return epsilon_r


def calculate_epsilon_r_from_files(reference_file: str, files: list[str], distance: float) -> np.ndarray:
    #this function finds epsilon r from the user selected reference file and multiple DUT files

    # Load the data from the reference file
    freq_ref, re_ref, im_ref = load_data(reference_file)
    
    # Convert the reference data to time domain
    time_ref, time_domain_signal_ref = convert_to_time_domain(freq_ref, re_ref, im_ref)
    
    # Initialize an empty list to store the epsilon r values and time/date tuples
    time_date = []
    epsilon_r_values = []

    index_ref = np.argmax(abs(time_domain_signal_ref))

    # Iterate over each file
    for file in files:
        # Load the data from the file
        freq, re, im = load_data(file)
        
        # Convert the data to time domain
        time, time_domain_signal = convert_to_time_domain(freq, re, im)
        
        # Find the time difference between the reference signal and the current signal
        # Find the peak value of each signal
    
        # Find the indices of the peak values
        index = np.argmax(abs(time_domain_signal))
    
        # Find the time difference between the peaks
        time_difference = time[index] - time_ref[index_ref]
    
        # Calculate the epsilon r value
        c=3e8
        epsilon_r = (1 + (time_difference * c) / (distance * 10 ** -3)) ** 2
        
        # Extract the creation or last modified date of the file
        file_stats = os.stat(file)
        timestamp = max(file_stats.st_ctime, file_stats.st_mtime)
        current_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')

        
        # Append the data to the arrays
        time_date.append(current_date)
        epsilon_r_values.append(epsilon_r)

    return time_date, epsilon_r_values

def plot_epsilon_r_over_time(time_date, epsilon_r_values):
    #this function plots epsilon r over time or measurements taken based on the date stamp of the saved touchstone files

    time, epsilon_r = np.array(time_date), np.array(epsilon_r_values)
    
    # Plot the epsilon r values over time with markers
    plt.plot(range(len(time)), np.round(epsilon_r, 3), marker='o', linestyle='-')
    plt.xticks(range(len(time)), time, rotation=45)
    plt.xlabel('Time')
    plt.ylabel('εᵣ')
    plt.title('Relative Permittivity Over Time')
    
    # Display epsilon r values beside the data points
    for i in range(len(time)):
        plt.text(i, epsilon_r[i], f'{epsilon_r[i]:.3f}', ha='center', va='bottom')
    
    plt.show()


def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray) -> np.ndarray:
    #this function converts the frequency domain data to time domain data using the chirp z transform using 
    #a time winow specified by the user through the software GUI

    # Calculate the number of samples
    num_samples = len(frequencies)
    
    # Initialize an empty array for the time domain signal
    freq_resp = np.zeros(num_samples, dtype=complex)
    time_range = 50

    time_range = float(time_range) * 10 ** -9
    # Iterate over each frequency and corresponding real and imaginary parts
    for i in range(num_samples):
        # Calculate the time domain value using inverse Fourier transform
        freq_resp[i] = real_parts[i] + 1j * imaginary_parts[i]
    time, time_domain_signal = czt.freq2time(frequencies, freq_resp, np.linspace(0, time_range, 100001))
    return time, time_domain_signal


def plot_time_domain(data):
    #this function plots the time domain data

    # Generate the time axis
    #time = np.arange(len(time_domain_signal))
    time, time_domain_signal = convert_to_time_domain(data[0], data[1], data[2])
    # Plot the time domain signal
    plt.plot(time * 10 ** 9, np.abs(time_domain_signal))
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude')
    plt.title('Time Domain Wave')
    plt.show()

def plot_time_domain_compare(data1, data2):
    #this function is used to plot the reference data against the DUT data in the time domain.
    #data1 is the DUT and data2 is the reference data

    # Convert the data to time domain for the first set
    time1, time_domain_signal1 = convert_to_time_domain(data1[0], data1[1], data1[2])
    
    # Convert the data to time domain for the second set
    time2, time_domain_signal2 = convert_to_time_domain(data2[0], data2[1], data2[2])
    
    # Plot the time domain signals
    plt.plot(time1 * 10 ** 9, np.abs(time_domain_signal1), label='DUT')
    plt.plot(time2 * 10 ** 9, np.abs(time_domain_signal2), label='Reference')
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude')
    plt.title('Time Domain Reference vs DUT')
    plt.legend()
    plt.show()

def load_data(file: str) -> tuple:
    #this function loads the data from a touchstone file and returns the frequency, real, and imaginary parts
    freq = []
    re = []
    im = []
    
    with open(file, 'r') as f:
        for line in f:
            if line.startswith('!') or line.startswith('#'):
                continue
            parts = line.split()
            freq.append(float(parts[0]))
            re.append(float(parts[3]))
            im.append(float(parts[4]))
    
    return np.array(freq), np.array(re), np.array(im)

def main():
    #this is the main function that executes the program for testing
    # Ask the user to select the reference file
    root = tk.Tk()
    root.withdraw()
    reference_file = filedialog.askopenfilename(title='Select Reference File')
    
    # Ask the user to select the DUT files
    files = filedialog.askopenfilenames(title='Select DUT Files')
    
    # Ask the user for the distance and time range
    distance = float(input('Enter the distance between the reference and DUT (in mm): '))
    time_range = float(input('Enter the time range for the time domain conversion (in ns): '))
    
    # Calculate the epsilon r values
    time_date_epsilon_array = calculate_epsilon_r_from_files(reference_file, files, distance)
    
    # Plot the epsilon r values over time
    plot_epsilon_r_over_time(time_date_epsilon_array)

if __name__ == '__main__':
    main()