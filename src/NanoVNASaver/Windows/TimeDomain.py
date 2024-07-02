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
import logging

from PyQt6 import QtWidgets, QtCore, QtGui
# from NanoVNASaver.Touchstone import Touchstone
# from NanoVNASaver.RFTools import Datapoint
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

        TD_control_box = QtWidgets.QGroupBox("Plotting Time Domain")
        TD_control_box.setMaximumWidth(300)
        TD_control_box_layout = QtWidgets.QFormLayout(TD_control_box)

        #enter time range for time domain plot
        time_range_label = QtWidgets.QLabel("Time Range (ns):")
        time_range_textfield = QtWidgets.QLineEdit()
        time_range_textfield.textChanged.connect(lambda: time_range_textfield.setText(time_range_textfield.text()))
        TD_control_box_layout.addRow(time_range_label, time_range_textfield)

        #in future add for s11, plots time domain for S21
        btn_TD_plot = QtWidgets.QPushButton("Plot Time Domain Current Sweep")
        btn_TD_plot.clicked.connect(lambda: self.plotTDCurrentSweep(4, time_range_textfield.text()))
        TD_control_box_layout.addRow(btn_TD_plot)

        #compares plots for set reference and sweep data
        btn_TD_plot_compare = QtWidgets.QPushButton("Compare Ref and DUT Plots") 
        btn_TD_plot_compare.clicked.connect(lambda: self.plotTDCompare(4, time_range_textfield.text()))
        TD_control_box_layout.addRow(btn_TD_plot_compare)

        file_window_layout.addWidget(TD_control_box)

        #create separate box for calculating permittivity
        permittivity_control_box = QtWidgets.QGroupBox("Calculate Permittivity")
        permittivity_control_box.setMaximumWidth(300)
        permittivity_control_box_layout = QtWidgets.QFormLayout(permittivity_control_box)

        #enter distance between antennas
        distance_label = QtWidgets.QLabel("Distance (mm):")
        distance_textfield = QtWidgets.QLineEdit()
        time_range_textfield = QtWidgets.QLineEdit()
        distance_textfield.textChanged.connect(lambda: distance_textfield.setText(distance_textfield.text()))
        permittivity_control_box_layout.addRow(distance_label, distance_textfield)

        #s21 calculate permittivity
        btn_calc_perm_inst = QtWidgets.QPushButton("Calculate DUT Permittivity based on Reference")
        btn_calc_perm_inst.clicked.connect(lambda: self.calculateinstantPermittivity(4, distance_textfield.text(), time_range_textfield.text()))
        permittivity_control_box_layout.addRow(btn_calc_perm_inst)

        #s21 calculate permittivities based on selected files over time
        btn_load_perm_files = QtWidgets.QPushButton("Permittivity over Time")
        btn_load_perm_files.clicked.connect(self.calcPermittivityOverTime)
        permittivity_control_box_layout.addRow(btn_load_perm_files)

        file_window_layout.addWidget(permittivity_control_box)

        btn_time = QtWidgets.QPushButton("Time Domain")
        btn_time.setMinimumHeight(20)
        btn_time.clicked.connect(lambda: self.display_window("time"))

    def currentSweepData(self, nr_params: int = 0):
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

    def plotTDCurrentSweep(self, nr_params: int = 0, time_range: float = 0):
        if str(time_range) == '':         
            QtWidgets.QMessageBox.warning(
                self, "Time Range Error", "Please enter a time range to plot the time domain."
            )
            return
        #get data from current sweep
        current_data = self.currentSweepData(nr_params)
        Calculations.plot_time_domain(current_data, time_range)

    def plotTDCompare(self, nr_params: int = 0, time_range: str = ''):
        if time_range == '':         
            QtWidgets.QMessageBox.warning(
                self, "Time Range Error", "Please enter a time range to plot the time domain."
            )
            return
        current_data = self.currentSweepData(nr_params)
        ref_data = self.currentRefData(nr_params)
        Calculations.plot_time_domain_compare(current_data, ref_data, time_range)

    
    def calculateinstantPermittivity(self, nr_params: int = 0, distance: str = '', time_range: str = ''):
        if distance == '':         
            QtWidgets.QMessageBox.warning(
                self, "Distance Error", "Please enter a distance between the antennas to calculate the permittivity."
            )
            return
        if time_range == '':         
            QtWidgets.QMessageBox.warning(
                self, "Time Range Error", "Please enter a time range to plot the time domain."
            )
            return
        current_data = self.currentSweepData(nr_params)
        ref_data = self.currentRefData(nr_params)
        eps_r = Calculations.calculate_epsilon_r(current_data, ref_data, float(distance), float(time_range))
        file_window_layout = QtWidgets.QVBoxLayout()
        eps_r_widget = QtWidgets.QWidget()
        eps_r_layout = QtWidgets.QVBoxLayout(eps_r_widget)
        eps_r_label = QtWidgets.QLabel("Permittivity (εᵣ):")
        eps_r_value = QtWidgets.QLabel(str(eps_r))
        eps_r_layout.addWidget(eps_r_label)
        eps_r_layout.addWidget(eps_r_value)
        file_window_layout.addWidget(eps_r_widget)


    def calcPermittivityOverTime(self, distance: str = '', time_range: str = ''):
        if distance == '':         
            QtWidgets.QMessageBox.warning(
                self, "Distance Error", "Please enter a distance between the antennas to calculate the permittivity."
            )
            return
        if time_range == '':         
            QtWidgets.QMessageBox.warning(
                self, "Time Range Error", "Please enter a time range to plot the time domain."
            )
            return
        # Prompt the user to select a reference file
        reference_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Reference File")

        # Prompt the user to select multiple device under test files
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Device Under Test Files")
        time_date_epsilon_array = Calculations.calculate_epsilon_r_from_files(reference_file, files, distance, time_range)
        
        # Plot the epsilon r values over time
        Calculations.plot_epsilon_r_over_time(time_date_epsilon_array)
