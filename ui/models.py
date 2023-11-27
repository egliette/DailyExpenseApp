from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDesktopWidget,
    QHeaderView,
    QMessageBox,    
)
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt, QDate
import pandas as pd
import numpy as np
from pyqtgraph import DateAxisItem, ViewBox, AxisItem
import pyqtgraph as pg

from ui import resources_rc


class OneDayTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(OneDayTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if index.column() == 1 and isinstance(value, np.int64):
                value = "{:,}".format(value).replace(",", ".")

            if str(value) == "nan":
                value = "None"

            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

    def setData(self, index, value, role=Qt.EditRole):
        try:
            if role in (Qt.DisplayRole, Qt.EditRole):
                if not value:
                    return False
                
                if index.column() == 1:
                    value = int(value)

                self._data.iloc[index.row(), index.column()] = value
                self.dataChanged.emit(index, index)
            return True
        except ValueError:
            self.show_error_popup("Price must be an integer.")
            self._data.iloc[index.row(), index.column()] = 0
            self.dataChanged.emit(index, index)
            return True
    
    def flags(self, index):
        return super().flags(index) | Qt.ItemIsEditable
        
    def add_row(self, row_data):
        self._data.loc[len(self._data)] = row_data
        self.layoutChanged.emit()

    def remove_row(self, row_index):
        self._data.drop(row_index, inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()
    
    def save_data(self, fpath, date):
        df = self._data.copy()        
        df["Date"] = date

        old_df = pd.read_csv(fpath)
        filtered_df = old_df[old_df["Date"] != date]

        result_df = pd.concat([filtered_df, df], ignore_index=True)
        result_df = result_df.sort_values(by="Date")
        result_df.to_csv(fpath, index=False)

    def show_error_popup(self, message):
        error_popup = QMessageBox()
        error_popup.setIcon(QMessageBox.Critical)
        error_popup.setWindowTitle("Error")
        error_popup.setText(message)
        error_popup.exec_()

    def get_total_spending(self):
        total = "{:,}".format(self._data["Price"].sum()).replace(",", ".")
        return total

class WeekTableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(WeekTableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            if index.column() == 1 and isinstance(value, np.int64):
                value = "{:,}".format(value).replace(",", ".")

            if str(value) == "nan":
                value = "None"

            return str(value)
    
        if role == Qt.TextAlignmentRole:
            if index.column() == 1:
                return Qt.AlignVCenter + Qt.AlignRight

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]
    
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])
