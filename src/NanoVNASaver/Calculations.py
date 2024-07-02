import itertools as it
import math
import matplotlib.pyplot as plt
from typing import Callable

import numpy as np
#need to load filename 
import os
import czt
import tkinter as tk
import datetime
from tkinter import filedialog

def data_input() -> tuple:
    # Create a Tkinter root window
    root = tk.Tk()
    root.withdraw()
    
    # Open file dialog for the first file
    reference = filedialog.askopenfilename(title="Select the reference file")
    
    # Open file dialog for the second file
      # Open file dialog for multiple files
    files = filedialog.askopenfilenames(title="Select files")
    
    # Convert the files to a list
    file_list = list(files)
    # Prompt the user to enter a distance value
    distance = float(tk.simpledialog.askstring("Enter Distance", "Enter the distance value in cm:"))
    
    return reference, file_list, distance

def calculate_epsilon_r(data1: tuple, data2: tuple, distance: float = 0, time_range: float = 0) -> float:
    # Convert the data to time domain for the first set
    time1, time_domain_signal1 = convert_to_time_domain(data1[0], data1[1], data1[2], float(time_range))
    
    # Convert the data to time domain for the second set
    time2, time_domain_signal2 = convert_to_time_domain(data2[0], data2[1], data2[2], float(time_range))
    
    # Find the peak value of each signal
    peak1 = np.max(abs(time_domain_signal1))
    peak2 = np.max(abs(time_domain_signal2))
    
    # Find the indices of the peak values
    index1 = np.argmax(abs(time_domain_signal1))
    index2 = np.argmax(abs(time_domain_signal2))
    
    # Find the time difference between the peaks
    time_difference = time1[index1] - time2[index2]
    print(time_difference, distance,time_range)
    # Calculate the epsilon r value
    c = 3e8

    epsilon_r = (1 + (time_difference * c) / (distance * 10 ** -3)) ** 2
    # Create a Tkinter window to display the epsilon r value
    window = tk.Tk()
    window.title("Permittivity (εᵣ):")
    window.geometry("200x100")

    # Create a label to display the epsilon r value
    epsilon_r_label = tk.Label(window, text=f"Permittivity (εᵣ): {epsilon_r}")
    epsilon_r_label.pack()

    # Run the Tkinter event loop
    window.mainloop()


def calculate_epsilon_r_from_files(reference_file: str, files: list[str], distance: float, time_range: float) -> np.ndarray:
    # Load the data from the reference file
    freq_ref, re_ref, im_ref = load_data(reference_file)
    
    # Convert the reference data to time domain
    time_ref, time_domain_signal_ref = convert_to_time_domain(freq_ref, re_ref, im_ref, time_range)
    
    # Initialize an empty list to store the epsilon r values and time/date tuples
    time_date_tuples = []
    peak_ref = np.max(abs(time_domain_signal_ref))
    index_ref = np.argmax(abs(time_domain_signal_ref))
    print(index_ref)
    # Iterate over each file
    for file in files:
        # Load the data from the file
        freq, re, im = load_data(file)
        
        # Convert the data to time domain
        time, time_domain_signal = convert_to_time_domain(freq, re, im, time_range)
        
        # Find the time difference between the reference signal and the current signal
        # Find the peak value of each signal
        peak = np.max(abs(time_domain_signal))
    
        # Find the indices of the peak values
        index = np.argmax(abs(time_domain_signal))
    
        # Find the time difference between the peaks
        time_difference = time[index] - time_ref[index_ref]
        print(time_difference, distance)
        # Calculate the epsilon r value
        c=3e8
        epsilon_r = (1 + (time_difference * c) / (distance * 10 ** -3)) ** 2
        
        # Extract the creation or last modified date of the file
        file_stats = os.stat(file)
        timestamp = max(file_stats.st_ctime, file_stats.st_mtime)
        current_date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
        
        # Create a tuple with the time, date, and epsilon r value
        time_date_epsilon_tuple = (current_date, epsilon_r)
        
        # Append the tuple to the list
        time_date_tuples.append(time_date_epsilon_tuple)
    
    # Convert the list of tuples to a 2D numpy array
    time_date_epsilon_array = np.array(time_date_tuples)
    
    return time_date_epsilon_array

def plot_epsilon_r_over_time(time_date_epsilon_array: np.ndarray):
    # Extract the time and epsilon r values from the array
    time = time_date_epsilon_array[:, 0]
    epsilon_r = time_date_epsilon_array[:, 1]
    
    # Plot the epsilon r values over time with markers
    plt.plot(range(len(time)), epsilon_r, marker='o')
    plt.xticks(range(len(time)), time, rotation=45)
    plt.xlabel('Time')
    plt.ylabel('Epsilon r')
    plt.title('Epsilon r Over Time')
    
    # Display epsilon r values beside the data points
    for i in range(len(time)):
        plt.text(i, epsilon_r[i], f'{epsilon_r[i]}', ha='center', va='bottom')
    
    plt.show()

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
            real = float(columns[3])
            imaginary = float(columns[4])
            
            # Append the values to the arrays
            freq.append(frequency)
            re.append(real)
            im.append(imaginary)
    
    # Convert the arrays to numpy arrays
    freq = np.array(freq)
    re = np.array(re)
    im = np.array(im)
    
    return freq, re, im

def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray, time_range: float) -> np.ndarray:
    # Calculate the number of samples
    num_samples = len(frequencies)
    
    # Initialize an empty array for the time domain signal
    freq_resp = np.zeros(num_samples, dtype=complex)
    
    time_range = float(time_range) * 10 ** -9
    # Iterate over each frequency and corresponding real and imaginary parts
    for i in range(num_samples):
        # Calculate the time domain value using inverse Fourier transform
        freq_resp[i] = real_parts[i] + 1j * imaginary_parts[i]
    time, time_domain_signal = czt.freq2time(frequencies, freq_resp, np.linspace(0, time_range, 1001))
    return time, time_domain_signal


def plot_time_domain(data, time_range: float = 0):
    # Generate the time axis
    #time = np.arange(len(time_domain_signal))
    time, time_domain_signal = convert_to_time_domain(data[0], data[1], data[2], time_range)
    # Plot the time domain signal
    plt.plot(time * 10 ** 9, np.abs(time_domain_signal))
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude')
    plt.title('Time Domain Wave')
    plt.show()

def plot_time_domain_compare(data1, data2, time_range: float = 0):
    # Convert the data to time domain for the first set
    time1, time_domain_signal1 = convert_to_time_domain(data1[0], data1[1], data1[2], time_range)
    
    # Convert the data to time domain for the second set
    time2, time_domain_signal2 = convert_to_time_domain(data2[0], data2[1], data2[2], time_range)
    
    # Plot the time domain signals
    plt.plot(time1 * 10 ** 9, np.abs(time_domain_signal1), label='Set 1')
    plt.plot(time2 * 10 ** 9, np.abs(time_domain_signal2), label='Set 2')
    plt.xlabel('Time (ns)')
    plt.ylabel('Amplitude')
    plt.title('Time Domain Wave')
    plt.legend()
    plt.show()

def main():
    # Prompt the user for data input
    reference_file, files, distance = data_input()
    
    # Calculate the epsilon r values from the files
    time_date_epsilon_array = calculate_epsilon_r_from_files(reference_file, files, distance)
    
    # Plot the epsilon r values over time
    plot_epsilon_r_over_time(time_date_epsilon_array)

if __name__ == "__main__":
    main()