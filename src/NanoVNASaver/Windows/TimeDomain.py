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

        self.setWindowTitle("Time Domain Analusis")
        self.setWindowIcon(self.app.icon)
        self.setMinimumWidth(200)
        QtGui.QShortcut(QtCore.Qt.Key.Key_Escape, self, self.hide)

        file_window_layout = QtWidgets.QVBoxLayout()
        make_scrollable(self, file_window_layout)

        TD_control_box = QtWidgets.QGroupBox("Plotting Time Domain")
        TD_control_box.setMaximumWidth(300)
        TD_control_box_layout = QtWidgets.QFormLayout(TD_control_box)

        time_range_label = QtWidgets.QLabel("Time Range:")
        time_range_textfield = QtWidgets.QLineEdit()
        TD_control_box_layout.addRow(time_range_label, time_range_textfield)

        #in future add for s21
        btn_TD_plot = QtWidgets.QPushButton("Plot Time Domain")
        btn_TD_plot.clicked.connect(lambda: self.plotTD(4, time_range_textfield.text()))
        TD_control_box_layout.addRow(btn_TD_plot)


        file_window_layout.addWidget(TD_control_box)

        btn_time = QtWidgets.QPushButton("Time Domain")
        btn_time.setMinimumHeight(20)
        btn_time.clicked.connect(lambda: self.display_window("time"))

    def plotTD(self, nr_params: int = 0, time_range: float = 0):
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
        if time_range == 0:         
            QtWidgets.QMessageBox.warning(
                self, "Time Range Error", "Please enter a time range to plot the time domain."
            )
            return

        ts = Touchstone()
        ts.sdata[0] = self.app.data.s11
        if nr_params > 1:
            ts.sdata[1] = self.app.data.s21
            for dp in self.app.data.s11:
                ts.sdata[2].append(Datapoint(dp.freq, 0, 0))
                ts.sdata[3].append(Datapoint(dp.freq, 0, 0))

        Calculations.plot_time_domain_from_text(Touchstone.saves(ts, nr_params), nr_params, time_range)