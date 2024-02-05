import os
from datetime import datetime

from PyQt5 import uic, QtGui
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QMainWindow, QHeaderView
import pandas as pd
import pyqtgraph as pg
from pyqtgraph import AxisItem

from ui import resources_rc
from ui.models import WeekTableModel
from ui.record_ui import RecordEditingUI

  
class DashboardUI(QMainWindow):
    def __init__(self, name):
        super().__init__()

        uic.loadUi("ui/dashboard.ui", self)
        self.setWindowTitle("Dashboard")
        self.setWindowIcon(QtGui.QIcon(":/images/icon"))

        self.usernameLabel.setText(name)
        self.calendarWidget.selectionChanged.connect(self.change_date)
        self.dateEdit.setCalendarPopup(True)

        self.change_date()

        self.showMaximized()

        self.record_window = RecordEditingUI(close_func=self.update_week_graph)
        self.modifyButton.clicked.connect(self.open_record)

        self.graphWidget.setBackground((221,242,253))

        self.save_fpath = "data.csv"
        if os.path.exists(self.save_fpath):
            self.update_week_graph()
        else:
            data = pd.DataFrame(columns=["Name", "Price", "Date"])
            data.to_csv(self.save_fpath, index=False)

        current_datetime = datetime.now()

        formatted_date = current_datetime.strftime("%A, %B %d, %Y")
        self.todayLabel.setText(formatted_date)

        self.editPageButton.clicked.connect(self.open_edit_page)
        self.editPageButton.setStyleSheet("background-color : #7F9DA7")
        self.stackedWidget.setCurrentWidget(self.addingPage)
        self.viewPageButton.clicked.connect(self.open_view_page)

        self.fullGraphWidget.setBackground((221,242,253))
        
        self.set_from_to_dates = False

        df = pd.read_csv(self.save_fpath, parse_dates=["Date"], dayfirst=True)

        if len(df) > 0:
            min_date = self.date2qdate(df['Date'].min())
            max_date = self.date2qdate(df['Date'].max())
        else:
            current_date = QDate.currentDate()
            day_of_week = current_date.dayOfWeek()
            min_date = current_date.addDays(1 - day_of_week)
            max_date = current_date.addDays(7 - day_of_week)

        self.fromDateEdit.setDate(min_date)
        self.toDateEdit.setDate(max_date)


        self.update_full_graph()

        self.fromDateEdit.dateChanged.connect(self.update_full_graph) 
        self.toDateEdit.dateChanged.connect(self.update_full_graph)

        self.comboBox.currentIndexChanged.connect(self.update_full_graph)

    def open_edit_page(self):
        self.stackedWidget.setCurrentWidget(self.addingPage)
        self.editPageButton.setStyleSheet("background-color : #7F9DA7")
        self.viewPageButton.setStyleSheet("background-color : #427D9D")

    def open_view_page(self):
        self.stackedWidget.setCurrentWidget(self.viewPage)
        self.viewPageButton.setStyleSheet("background-color : #7F9DA7")
        self.editPageButton.setStyleSheet("background-color : #427D9D")

    def update_full_graph(self):
        self.fullGraphWidget.clear()

        pen = pg.mkPen(color=(155,190,200), width=3)
        tickpen = pg.mkPen(color=(22,72,99), width=3)

        bottom_ax = AxisItem("bottom", pen=pen, tickpen=tickpen)
        left_ax = AxisItem("left", pen=pen, tickpen=tickpen)
        bottom_ax.setTextPen((22,72,99))
        left_ax.setLabel("k VND", color=(22,72,99))
        left_ax.setTextPen((22,72,99))
        left_ax.setScale(0.001)  
        
        self.fullGraphWidget.setTitle("Spendings of this week", color=(22,72,99))
        self.fullGraphWidget.setAxisItems({"bottom": bottom_ax, "left": left_ax})

        df = pd.read_csv(self.save_fpath, parse_dates=["Date"], dayfirst=True)
        if len(df) == 0:
            return

        start_date = pd.to_datetime(self.fromDateEdit.date().toPyDate())
        end_date = pd.to_datetime(self.toDateEdit.date().toPyDate())
    
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

        new_df = df.groupby("Date")["Price"].sum().reset_index()
        new_df = new_df.rename(columns={"Price": "Spending"})

        unit = self.comboBox.currentText()

        if unit == "Week":
            new_df = new_df.set_index('Date').resample('W-Mon').agg({'Spending': 'sum'}).reset_index()
        elif unit == "Month":
            new_df = new_df.set_index('Date').resample('M').agg({'Spending': 'sum'}).reset_index()

        new_df["Timestamp"] = new_df["Date"].apply(lambda x: x.timestamp())

        date_list = new_df["Date"].tolist()
        labels = [(new_df["Timestamp"].iloc[i], new_df["Date"].iloc[i].strftime("%d-%m-%Y")) for i in range(len(date_list))]

        bottom_ax.setTicks([labels]) 
        self.fullGraphWidget.plot(
            new_df["Timestamp"], 
            new_df["Spending"], 
            labels=labels, 
            pen=pen,
            symbol="o",
            symbolBrush=(22,72,99),
        )

    def date2qdate(self, date):
        year = date.year
        month = date.month
        day = date.day

        return QDate(year, month, day)

    def update_week_graph(self):
        self.graphWidget.clear()

        df = pd.read_csv(self.save_fpath)
        if len(df) == 0:
            return

        df = pd.read_csv(self.save_fpath, parse_dates=["Date"], dayfirst=True)

        current_week = datetime.now().isocalendar()[1]
        current_year = datetime.now().year

        df = df[(df['Date'].dt.isocalendar().week == current_week) & (df['Date'].dt.year == current_year)]

        new_df = df.groupby("Date")["Price"].sum().reset_index()
        new_df = new_df.rename(columns={"Price": "Spending"})
        new_df["Timestamp"] = new_df["Date"].apply(lambda x: x.timestamp())

        date_list = new_df["Date"].tolist()
        labels = [(new_df["Timestamp"].iloc[i], new_df["Date"].iloc[i].strftime("%A")) for i in range(len(date_list))]

        self.graphWidget.setDefaultPadding(padding=0.1)
        pen = pg.mkPen(color=(155,190,200), width=3)
        tickpen = pg.mkPen(color=(22,72,99), width=3)

        bottom_ax = AxisItem("bottom", pen=pen, tickpen=tickpen)
        left_ax = AxisItem("left", pen=pen, tickpen=tickpen)
        bottom_ax.setTextPen((22,72,99))
        bottom_ax.setTicks([labels]) 
        left_ax.setLabel("k VND", color=(22,72,99))
        left_ax.setTextPen((22,72,99))
        left_ax.setScale(0.001)  
        
        self.graphWidget.setTitle("Spendings of this week", color=(22,72,99))
        self.graphWidget.setAxisItems({"bottom": bottom_ax, "left": left_ax})

        self.graphWidget.plot(
            new_df["Timestamp"], 
            new_df["Spending"], 
            labels=labels, 
            pen=pen,
            symbol="o",
            symbolBrush=(22,72,99),
        )

        new_df = new_df.drop(columns=['Timestamp'])
        new_df['Date'] = new_df['Date'].dt.day_name()
  
        model = WeekTableModel(new_df)
        self.totalSpendingTableView.setModel(model)
        header = self.totalSpendingTableView.horizontalHeader()       
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        total_spending = int(new_df['Spending'].sum())
        total_spending = "{:,}".format(total_spending).replace(",", ".")
        self.totalSpendingLabel.setText(f"Total spending: {total_spending}")

        self.update_full_graph()

    def open_record(self):
        self.record_window.show_window(self.dateEdit.date())

    def change_date(self):
        date = self.calendarWidget.selectedDate()
        self.dateEdit.setDate(date)

    def closeEvent(self, event):
        if self.record_window:
            self.record_window.close()
