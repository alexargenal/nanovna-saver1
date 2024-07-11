#This module is used to compute the time domain of sweep data, calculate the relative permittivity of a material,
#and use matplotlib plots to visualize the time domain as well as permittivity calcs over time.

import numpy as np
#need to load filename 
import os
import czt
import datetime
import math


def calculate_epsilon_r(data1: tuple, data2: tuple, distance: float = 0, ref_perm: float = 1) -> float:
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
    
    epsilon_r = ref_perm * (1 + (time_difference * c) / ((distance * 10 ** -3) * (math.sqrt(ref_perm)))) ** 2
    
    return epsilon_r


def calculate_epsilon_r_from_files(reference_file: str, files: list[str], distance: float, ref_perm: float) -> np.ndarray:
    #this function finds epsilon r from the user selected reference file and multiple DUT files

    # Load the data from the reference file
    freq_ref, re_ref, im_ref = load_data(reference_file)
    
    # Convert the reference data to time domain
    time_ref, time_domain_signal_ref = convert_to_time_domain(freq_ref, re_ref, im_ref)
    
    # Initialize an empty list to store the epsilon r values and time/date tuples
    epsilon_r_values_time = []

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
        epsilon_r = ref_perm * (1 + (time_difference * c) / ((distance * 10 ** -3) * (math.sqrt(ref_perm)))) ** 2
        
        # Get the last modified or creation date and time of the file
        file_date = os.path.getmtime(file)
        file_datetime = datetime.datetime.fromtimestamp(file_date).strftime('%Y-%m-%d %H:%M')
        
        # Append the file date and epsilon r value to the list
        epsilon_r_values_time.append((file_datetime, epsilon_r))
        
    
    epsilon_r_values_time.sort(key=lambda x: x[0])
    current_date = [date[0] for date in epsilon_r_values_time]
    epsilon_r_values = [value[1] for value in epsilon_r_values_time]
    epsilon_r_values = [float(value) for value in epsilon_r_values]

    return current_date, epsilon_r_values


def convert_to_time_domain(frequencies: np.ndarray, real_parts: np.ndarray, imaginary_parts: np.ndarray) -> np.ndarray:
    #this function converts the frequency domain data to time domain data using the chirp z transform using 
    #a time winow specified by the user through the software GUI

    # Calculate the number of samples
    num_samples = len(frequencies)
    
    # Initialize an empty array for the time domain signal
    freq_resp = np.zeros(num_samples, dtype=complex)
    time_range = 10

    time_range = float(time_range) * 10 ** -9
    # Iterate over each frequency and corresponding real and imaginary parts
    for i in range(num_samples):
        # Calculate the time domain value using inverse Fourier transform
        freq_resp[i] = real_parts[i] + 1j * imaginary_parts[i]
    time, time_domain_signal = czt.freq2time(frequencies, freq_resp, np.linspace(0, time_range, 100001))
    return time, time_domain_signal




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

