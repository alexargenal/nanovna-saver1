#  NanoVNASaver
#
#  A python program to view and export Touchstone data from a NanoVNA
#  Copyright (C) 2019, 2020  Rune B. Broberg
#  Copyright (C) 2020,2021 NanoVNA-Saver Authors
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

#This module is responsible for managing the time domain in the GUI, including plotting the time domain, 
#comparing the time domain of the reference and current sweep data, and calculating the relative permittivity of a material.

from PyQt6 import QtWidgets, QtCore, QtGui
from NanoVNASaver.Windows.Defaults import make_scrollable
from NanoVNASaver.RFTools import Datapoint
from NanoVNASaver import Calculations
from NanoVNASaver.Touchstone import Touchstone


class TDWindow(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QWidget):
        super().__init__()
        self.app = app
        self.reference: list[Datapoint] = []
        

        self.setWindowTitle("Time Domain Analysis")
        self.setWindowIcon(self.app.icon)
        self.setMinimumWidth(200)
        QtGui.QShortcut(QtCore.Qt.Key.Key_Escape, self, self.hide)

        file_window_layout = QtWidgets.QVBoxLayout()
        make_scrollable(self, file_window_layout)

        User_in_control_box = QtWidgets.QGroupBox("Enter Distance between Antennas")
        User_in_control_box.setMaximumWidth(350)
        User_in_control_box_layout = QtWidgets.QFormLayout(User_in_control_box)

        #enter distance between antennas
        distance_label = QtWidgets.QLabel("Distance (mm):")
        distance_textfield = QtWidgets.QLineEdit()
        self.distance = distance_textfield.text()
        distance_textfield.textChanged.connect(lambda: setattr(self, 'distance', distance_textfield.text()))
        User_in_control_box_layout.addRow(distance_label, distance_textfield)

        file_window_layout.addWidget(User_in_control_box)

        TD_control_box = QtWidgets.QGroupBox("Plotting Time Domain")
        TD_control_box.setMaximumWidth(350)
        TD_control_box_layout = QtWidgets.QFormLayout(TD_control_box)

        #in future add for s11, plots time domain for S21
        btn_TD_plot = QtWidgets.QPushButton("Plot Time Domain Current Sweep")
        btn_TD_plot.clicked.connect(lambda: self.plotTDCurrentSweep(4))
        TD_control_box_layout.addRow(btn_TD_plot)

        #compares plots for set reference and sweep data
        btn_TD_plot_compare = QtWidgets.QPushButton("Compare Ref and DUT Plots") 
        btn_TD_plot_compare.clicked.connect(lambda: self.plotTDCompare(4))
        TD_control_box_layout.addRow(btn_TD_plot_compare)

        file_window_layout.addWidget(TD_control_box)

        #create separate box for calculating current permittivity
        permittivity_control_box = QtWidgets.QGroupBox("Calculate Permittivity Based on Current Sweep and Reference")
        permittivity_control_box.setMaximumWidth(350)
        permittivity_control_box_layout = QtWidgets.QFormLayout(permittivity_control_box)

        #s21 calculate permittivity
        btn_calc_perm_inst = QtWidgets.QPushButton("Estimate Relative Permitivity")
        btn_calc_perm_inst.clicked.connect(lambda: self.calculateinstantPermittivity(4))
        permittivity_control_box_layout.addRow(btn_calc_perm_inst)

        file_window_layout.addWidget(permittivity_control_box)

        # create separate box for calculating permittivity over time
        permittivity_over_time_control_box = QtWidgets.QGroupBox("Select Files to Plot Permittivity Over Time")
        permittivity_over_time_control_box.setMaximumWidth(350)
        permittivity_over_time_control_box_layout = QtWidgets.QFormLayout(permittivity_over_time_control_box)
        
        # calculate permittivities based on selected files over time
        btn_load_perm_files = QtWidgets.QPushButton("Load Files")
        btn_load_perm_files.clicked.connect(self.calcPermittivityOverTime)
        permittivity_over_time_control_box_layout.addRow(btn_load_perm_files)

        file_window_layout.addWidget(permittivity_over_time_control_box)

        btn_time = QtWidgets.QPushButton("Time Domain")
        btn_time.setMinimumHeight(20)
        btn_time.clicked.connect(lambda: self.display_window("time"))

    def currentSweepData(self, nr_params: int = 0):
        #this function accesses the current sweep data, either loaded by user or currently swept

        #check if the data is available
        if len(self.app.data.s11) == 0:
            QtWidgets.QMessageBox.warning(
                self, "No data to save", "There is no data to save."
            )
            return
        if nr_params > 2 and len(self.app.data.s21) == 0:
            QtWidgets.QMessageBox.warning(
                self, "No S21 data to save", "There is no S21 data to save."
            )
            return

        #populate touchstone instance with current data
        ts = Touchstone()
        ts.sdata[0] = self.app.data.s11
        if nr_params > 1:
            ts.sdata[1] = self.app.data.s21
            for dp in self.app.data.s11:
                ts.sdata[2].append(Datapoint(dp.freq, 0, 0))
                ts.sdata[3].append(Datapoint(dp.freq, 0, 0))
        freq = []
        real = []
        imaginary = []

        for dp in ts.s21:
            freq.append(dp.freq)
            real.append(dp.re)
            imaginary.append(dp.im)
            
        return freq, real, imaginary
        
    def currentRefData(self, nr_params: int = 0):
        #this function accesses the current set reference data set by the user

        #check if there is reference data to load
        if len(self.app.ref_data.s11) == 0:
            QtWidgets.QMessageBox.warning(
                self, "No reference data", "There is no reference data to loaded."
            )
            return
        if nr_params > 2 and len(self.app.ref_data.s21) == 0:
            QtWidgets.QMessageBox.warning(
                self, "No S21 reference data", "There is no S21 reference data loaded."
            )
            return

        #populate touchstone instance with reference data
        ts = Touchstone()
        ts.sdata[0] = self.app.ref_data.s11
        if nr_params > 1:
            ts.sdata[1] = self.app.ref_data.s21
            for dp in self.app.ref_data.s11:
                ts.sdata[2].append(Datapoint(dp.freq, 0, 0))
                ts.sdata[3].append(Datapoint(dp.freq, 0, 0))
        freq = []
        real = []
        imaginary = []

        for dp in ts.s21:
            freq.append(dp.freq)
            real.append(dp.re)
            imaginary.append(dp.im)
            
        return freq, real, imaginary

    def plotTDCurrentSweep(self, nr_params: int = 0):
        #this function plots the time domain data for the current sweep

        #get data from current sweep
        current_data = self.currentSweepData(nr_params)
        Calculations.plot_time_domain(current_data)

    def plotTDCompare(self, nr_params: int = 0):
        #this function compares the time domain plots of the reference and current sweep data
        
        current_data = self.currentSweepData(nr_params)
        ref_data = self.currentRefData(nr_params)
        Calculations.plot_time_domain_compare(current_data, ref_data)

    
    def calculateinstantPermittivity(self, nr_params: int = 0):
        #this function calculates and displays the relative permittivity based on the current sweep and reference data


        distance = self.distance

        if distance == '':         
            QtWidgets.QMessageBox.warning(
                self, "Distance Error", "Please enter a distance between the antennas to calculate the permittivity."
            )
            return
        
        current_data = self.currentSweepData(nr_params)
        ref_data = self.currentRefData(nr_params)
        eps_r = Calculations.calculate_epsilon_r(current_data, ref_data, float(distance))
        QtWidgets.QMessageBox.information(
            self, "Permittivity Calculation", f"The estimated relative permittivity (εᵣ) is: {eps_r:.3f}"
        )


    def calcPermittivityOverTime(self):
        #this function calculates and plots multiple epsilon r values from loaded files over time

        distance = self.distance

        
        if distance == '':         
            QtWidgets.QMessageBox.warning(
                self, "Distance Error", "Please enter a distance between the antennas to calculate the permittivity."
            )
            return

        # Prompt the user to select a reference file
        reference_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Reference File")

        # Prompt the user to select multiple device under test files
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Device Under Test Files")
        time_date, epsilon_r_vals = Calculations.calculate_epsilon_r_from_files(reference_file, files, float(distance))
        
        # Plot the epsilon r values over time
        Calculations.plot_epsilon_r_over_time(time_date, epsilon_r_vals)
