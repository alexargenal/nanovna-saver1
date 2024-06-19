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

def calculate_epsilon_r_from_files(reference_file: str, files: list[str], distance: float) -> np.ndarray:
    # Load the data from the reference file
    freq_ref, re_ref, im_ref = load_data(reference_file)
    
    # Convert the reference data to time domain
    time_ref, time_domain_signal_ref = convert_to_time_domain(freq_ref, re_ref, im_ref)
    
    # Initialize an empty list to store the epsilon r values and time/date tuples
    time_date_tuples = []
    peak_ref = np.max(time_domain_signal_ref)
    index_ref = np.argmax(time_domain_signal_ref)

    # Iterate over each file
    for file in files:
        # Load the data from the file
        freq, re, im = load_data(file)
        
        # Convert the data to time domain
        time, time_domain_signal = convert_to_time_domain(freq, re, im)
        
        # Find the time difference between the reference signal and the current signal
        # Find the peak value of each signal
        peak = np.max(time_domain_signal)
    
        # Find the indices of the peak values
        index = np.argmax(time_domain_signal)
    
        # Find the time difference between the peaks
        time_difference = index - index_ref
        
        # Calculate the epsilon r value
        c=3e8
        epsilon_r = (1 + (time_difference * c) / (distance)) ** 2
        
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

def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray, time_range: float) -> np.ndarray:
    # Calculate the number of samples
    num_samples = len(frequencies)
    
    # Initialize an empty array for the time domain signal
    freq_resp = np.zeros(num_samples, dtype=complex)
    
    time_range = float(time_range) * 10 ** -8
    # Iterate over each frequency and corresponding real and imaginary parts
    for i in range(num_samples):
        # Calculate the time domain value using inverse Fourier transform
        freq_resp[i] = real_parts[i] + 1j * imaginary_parts[i]
    time, time_domain_signal = czt.freq2time(frequencies, freq_resp, np.linspace(0, time_range, 1001))
    return time, time_domain_signal


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


def plot_time_domain_from_text(text: str, nr_params: int = 1, time: float = 0):
    # Split the text into lines
    lines = text.strip().split('\n')
    
    # Initialize empty arrays
    freq = []
    re_s11 = []
    im_s11 = []
    re_s21 = []
    im_s21 = []
    
    # Read each line and extract the values
    for line in lines:
        if line.startswith('#'):
            continue

        # Split the line into columns
        columns = line.strip().split()
        
        # Convert the columns to float values
        frequency = float(columns[0])
        real_s11 = float(columns[1])
        imaginary_s11 = float(columns[2])
        freq.append(frequency)
        re_s11.append(real_s11)
        im_s11.append(imaginary_s11)
        

        if nr_params > 1:
            real_s21 = float(columns[3])
            imaginary_s21 = float(columns[4])
            re_s21.append(real_s21)
            im_s21.append(imaginary_s21)
             
    # Convert the arrays to numpy arrays
    freq = np.array(freq)
 
    #plot for S11
    if nr_params == 1:
        re_s11 = np.array(re_s11)
        im_s11 = np.array(im_s11)
        time_s11, time_domain_signal_s11 = convert_to_time_domain(freq, re_s11, im_s11, time)
        plot_time_domain(time_s11, time_domain_signal_s11)

    #plot for S21
    if nr_params > 1:
        re_s21 = np.array(re_s21)
        im_s21 = np.array(im_s21)
        time_s21, time_domain_signal_s21 = convert_to_time_domain(freq, re_s21, im_s21, time)
        plot_time_domain(time_s21, time_domain_signal_s21)


def main():
    # Prompt the user for data input
    reference_file, files, distance = data_input()
    
    # Calculate the epsilon r values from the files
    time_date_epsilon_array = calculate_epsilon_r_from_files(reference_file, files, distance)
    
    # Plot the epsilon r values over time
    plot_epsilon_r_over_time(time_date_epsilon_array)

if __name__ == "__main__":
    main()