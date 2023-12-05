import os

import pandas as pd
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QMainWindow, QHeaderView

from ui import resources_rc
from ui.models import OneDayTableModel


class RecordEditingUI(QMainWindow):
    def __init__(self, close_func=None):
        super().__init__()

        uic.loadUi("ui/record.ui", self)
        self.setWindowTitle("Record Editing")
        self.setWindowIcon(QtGui.QIcon(":/images/icon"))
        self.model = None
        self.close_func = close_func
        self.save_fpath = "data.csv"
        self.addButton.clicked.connect(self.add_row)
        self.deleteButton.clicked.connect(self.delete_row)

    def show_window(self, date):
        self.show()
        self.set_date(date)
        self.load_data()

    def set_date(self, date):
        self.selected_date = date.toString("dd-MM-yyyy")
        self.dateLabel.setText(self.selected_date)

    def load_data(self):
        if os.path.exists(self.save_fpath):
            df = pd.read_csv(self.save_fpath)
            data = df[df["Date"] == self.selected_date][["Name", "Price"]]
        else:
            data = pd.DataFrame(columns=["Name", "Price", "Date"])
            data.to_csv(self.save_fpath, index=False)
            data = data.drop("Date", axis=1)

        data = data.reset_index(drop=True)

        self.model = OneDayTableModel(data)
        self.tableView.setModel(self.model)
        header = self.tableView.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

        self.model.dataChanged.connect(self.on_data_changed)
        self.on_data_changed()
    
    def on_data_changed(self):
        self.totalLabel.setText(f"Total spending: {self.model.get_total_spending()}")

    def closeEvent(self, event):
        if self.model:
            self.model.save_data(self.save_fpath, self.selected_date)
        
        if self.close_func:
            self.close_func()

    def add_row(self):
        self.model.add_row({"Name": None, "Price": 0})

    def delete_row(self):
        selected_indexes = self.tableView.selectedIndexes()
        if selected_indexes:
            row_to_remove = selected_indexes[0].row()
            print(row_to_remove)
            self.model.remove_row(row_to_remove)
            self.tableView.clearSelection()
