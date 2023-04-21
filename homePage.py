import asyncio
import os
import threading
from datetime import date, datetime

import PyQt5
import mysql.connector
from PyQt5 import QtWidgets
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter, A4

from hijri_converter import Hijri, Gregorian
from num2words import num2words
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
import sys
from PyQt5.QtWidgets import (QApplication,
                             QCheckBox,
                             QComboBox,
                             QDateEdit,
                             QDateTimeEdit,
                             QDial,
                             QDoubleSpinBox,
                             QFontComboBox,
                             QLabel,
                             QLCDNumber,
                             QLineEdit,
                             QMainWindow,
                             QProgressBar,
                             QPushButton,
                             QRadioButton,
                             QSlider,
                             QSpinBox,
                             QTimeEdit,
                             QVBoxLayout,
                             QWidget,
                             QHBoxLayout,
                             QGridLayout,
                             QTableWidget,
                             QHeaderView, QMenu, QAction, QInputDialog, QTableWidgetItem, QFormLayout, QScrollArea,
                             QGroupBox
                             )
from PyQt5.QtGui import (QPalette,
                         QColor,
                         QFont,
                         )

import sys
from random import choice

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="*****",
    auth_plugin='mysql_native_password'

)

mycursor = mydb.cursor()
mycursor.execute("CREATE DATABASE IF NOT EXISTS Expenses")
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="*****",
    auth_plugin='mysql_native_password',
    database='Expenses'
)
mycursor = mydb.cursor(buffered=True)

stmt = "SHOW TABLES LIKE 'Items'"
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    pass
else:
    mycursor.execute("CREATE TABLE Items (Item_No INTEGER(10), Item_Name VARCHAR(255))")
    itemsreq = ["Building Rent", "Iqama Visa", "Tools", "India Tools", "Mes", "Electric Bill", "Electric Maintenance",
                "Building Maintenance", "Water", "Salary", "Petrol", "Car Maintenance", "Zakat", "Extra"]
    sqlFormula = "INSERT INTO Items (Item_No,Item_Name) VALUES (%s,%s) "
    for i in range(14):
        details = [i, itemsreq[i]]
        mycursor.execute(sqlFormula, details)
        mydb.commit()

stmt = "SHOW TABLES LIKE 'expenseBalance'"
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    pass
else:
    mycursor.execute(
        "CREATE TABLE expenseBalance (Date VARCHAR(255), Item_Name VARCHAR(255), Amount FLOAT(20), Notes VARCHAR(255))")

stmt = "SHOW TABLES LIKE 'Debit_Credit'"
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    pass
else:
    mycursor.execute(
        "CREATE TABLE Debit_Credit (Date VARCHAR(255), Debit FLOAT(20), Credit FLOAT(20))")

# Make a table which records changes opens only on authourization
stmt = "SHOW TABLES LIKE 'Changes'"
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    pass
else:
    mycursor.execute(
        "CREATE TABLE Changes (Date VARCHAR(255), TableChanged VARCHAR(255), ItemName VARCHAR(255), ChangeType VARCHAR(255), OldVal VARCHAR(255), NewVal VARCHAR(255))")

stmt = "SHOW TABLES LIKE 'deletedEntries'"
mycursor.execute(stmt)
result = mycursor.fetchone()
if result:
    pass
else:
    mycursor.execute(
        "CREATE TABLE deletedEntries (dateDeleted VARCHAR(255), oldID VARCHAR(255) ,Date VARCHAR(255), Item_Name VARCHAR(255), Amount FLOAT(20), Notes VARCHAR(255))")

sqlFormula = "INSERT INTO Items (Item_Name, Locked) VALUES (%s,%s) "
sqlFormula1 = "INSERT INTO expenseBalance (Date,Item_Name, Amount, Notes) VALUES (%s,%s,%s,%s) "
sqlFormula2 = "INSERT INTO Debit_Credit (Date,Debit, Credit, Notes) VALUES (%s,%s,%s,%s) "
sqlFormula3 = "INSERT INTO Changes (Date, TableChanged, ItemName, ChangeType, OldVal, NewVal) VALUES (%s,%s,%s,%s,%s," \
              "%s) "
sqlFormula4 = "INSERT INTO deletedEntries (dateDeleted, oldID, Date, Item_Name, Amount, Notes) VALUES (%s,%s,%s,%s,%s,%s) "

# addition of id column in expense table
queryC = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
         "AND TABLE_NAME=" + "'" + "expenseBalance" + "' AND COLUMN_NAME = " + "'" + "id" + "'"
mycursor.execute(queryC)
editor = mycursor.fetchone()

if editor[0] == 0:
    query1 = "ALTER TABLE expenseBalance ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
    mycursor.execute(query1)

# addition of id column in debit_credit table
queryC1 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "debit_credit" + "' AND COLUMN_NAME = " + "'" + "id" + "'"
mycursor.execute(queryC1)
editor1 = mycursor.fetchone()

if editor1[0] == 0:
    query1 = "ALTER TABLE debit_credit ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
    mycursor.execute(query1)

# addition of notes column in debit_credit table
queryC2 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "debit_credit" + "' AND COLUMN_NAME = " + "'" + "Notes" + "'"
mycursor.execute(queryC2)
editor2 = mycursor.fetchone()

if editor2[0] == 0:
    query1 = "ALTER TABLE debit_credit ADD COLUMN Notes VARCHAR(255)"
    mycursor.execute(query1)

# addition of id column in changes table
queryC3 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "changes" + "' AND COLUMN_NAME = " + "'" + "id" + "'"
mycursor.execute(queryC3)
editor3 = mycursor.fetchone()

if editor3[0] == 0:
    query1 = "ALTER TABLE changes ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
    mycursor.execute(query1)

# addition of Locked column in items table
queryC4 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "items" + "' AND COLUMN_NAME = " + "'" + "Locked" + "'"
mycursor.execute(queryC4)
editor4 = mycursor.fetchone()

if editor4[0] == 0:
    query1 = "ALTER TABLE items ADD COLUMN Locked VARCHAR(255)"
    mycursor.execute(query1)

# removal of Item No. column in items table
queryC5 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "items" + "' AND COLUMN_NAME = " + "'" + "Item_No" + "'"
mycursor.execute(queryC5)
editor5 = mycursor.fetchone()
print(editor5[0])

if editor5[0] == 1:
    query = "ALTER TABLE Items DROP COLUMN Item_No"
    mycursor.execute(query)
    query1 = "ALTER TABLE items ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
    mycursor.execute(query1)


# addition of id column in deletedEntries table
queryC6 = "SELECT count(*) FROM information_schema.columns WHERE TABLE_SCHEMA=" + "'" + "Expenses" + "'" + \
          "AND TABLE_NAME=" + "'" + "deletedEntries" + "' AND COLUMN_NAME = " + "'" + "id" + "'"
mycursor.execute(queryC6)
editor6 = mycursor.fetchone()

if editor6[0] == 0:
    query1 = "ALTER TABLE deletedEntries ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST"
    mycursor.execute(query1)

queryU = "select id, Locked from items where Locked IS Null"
mycursor.execute(queryU)
updateRes = mycursor.fetchall()
queryR = "select COUNT(id) from items where Locked IS Null"
mycursor.execute(queryR)
rows = mycursor.fetchone()
for i in range(rows[0]):
    query = "UPDATE Items SET Locked = 'False' WHERE id = " + str(updateRes[i][0])
    mycursor.execute(query)
    mydb.commit()


class Box(QWidget):

    def __init__(self, color):
        super(Box, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(color))
        self.setPalette(palette)


class MyTable(QTableWidget):
    def __init__(self, r, c):
        super().__init__(r, c)
        self.init_ui()

    def init_ui(self):
        self.show()


class BalanceSheet(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expenses Manager")

        self.setFixedWidth(1400)
        self.setFixedHeight(700)

        self.makedir()

        header = QHBoxLayout()
        header_label = QLabel("Expenses Manager")
        header_label.setFixedSize(600, 40)
        header_label.setFont(QFont('Arial', 20))

        header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.addWidget(header_label)

        iconBox = QGridLayout()
        iconBox_wid1 = Box("white")
        button_row1 = QHBoxLayout(iconBox_wid1)

        saveBtn = QPushButton("Save")
        clearBtn = QPushButton("Clear")
        checkChangesBtn = QPushButton("Changes")
        additions = QPushButton("Additions")
        totals = QPushButton("Totals")

        saveBtn.clicked.connect(self.save)
        clearBtn.clicked.connect(self.clear)
        additions.clicked.connect(self.openAdds)
        totals.clicked.connect(self.openTotals)
        checkChangesBtn.clicked.connect(self.openChanges)

        button_row1.addWidget(saveBtn)
        button_row1.addWidget(clearBtn)
        button_row1.addWidget(additions)
        button_row1.addWidget(totals)
        button_row1.addWidget(checkChangesBtn)

        iconBox_wid1.setFixedHeight(50)
        iconBox_wid2 = Box("white")
        iconBox_wid2.setFixedHeight(50)
        iconBox_wid3 = Box("white")
        iconBox_wid3.setFixedHeight(50)
        iconBox.addWidget(iconBox_wid1, 0, 0)

        sheet_box = Box("White")
        sheetV = QVBoxLayout(sheet_box)
        sheet_box.setMaximumHeight(400)
        self.sheet = MyTable(100, 4)
        col_headers = ["Item Name", "Date", 'Amount', 'Notes']
        sheetV.setSpacing(0)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.sheet.setColumnWidth(0, 300)
        self.sheet.setColumnWidth(1, 300)
        self.sheet.setColumnWidth(2, 300)

        mycursor.execute("SELECT Item_Name FROM Items")
        result1 = mycursor.fetchall()

        for index in range(100):
            combo = QComboBox()
            combo.setStyleSheet("QComboBox"
                                "{"
                                "background-color: white"
                                "}")
            for row in result1:
                combo.addItem(str(row[0]))
            combo.setProperty('row', index)
            combo.setCurrentIndex(-1)
            if index != 0:
                combo.setEnabled(False)
            combo.currentIndexChanged.connect(lambda: self.setLabour())
            self.sheet.setCellWidget(index, 0, combo)

        sheetV.addWidget(self.sheet)

        total_box = Box("White")
        totalV = QVBoxLayout(total_box)
        total_box.setMaximumHeight(130)
        totalV.setSpacing(0)
        totalV.setContentsMargins(0, 0, 0, 0)
        self.total_sheet = MyTable(1, 7)
        horiz_header = self.total_sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.total_sheet.setColumnWidth(0, 320)
        self.total_sheet.setColumnWidth(1, 300)
        self.total_sheet.setColumnWidth(2, 300)
        self.total_sheet.verticalHeader().setVisible(False)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        totalV.addWidget(self.total_sheet)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(header)
        mainLayout.addLayout(iconBox)
        mainLayout.addWidget(sheet_box)
        mainLayout.addWidget(total_box)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

        self.itemName = []
        self.date = []
        self.amount = []
        self.notes = []

        for i in range(1, 4):
            for j in range(100):
                boi = QTableWidgetItem(None)
                boi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
                self.sheet.setItem(j, i, boi)

        self.sheet.itemChanged.connect(self.addValues)
        self.sheet.itemChanged.connect(self.total)
        self.clearManager = 0

    # add the method to see changes but can be only checked by papa so set a passcode

    def parentDir(self):
        pass

    def makedir(self):
        import os
        totalDir = "/TotalBills"
        specDir = "/Spec"

        if not os.path.isdir(totalDir):
            os.makedirs(totalDir)

        if not os.path.isdir(specDir):
            os.makedirs(specDir)

    def setLabour(self):

        combo = self.sender()
        row = combo.property('row')
        value = combo.currentText()
        self.clearManager = 0

        nextCombo = self.sheet.cellWidget(row + 1, 0)

        if nextCombo.isEnabled() == False:
            nextCombo.setEnabled(True)

        if row != 0 and self.sheet.item(row - 1, 2) is None:
            self.dialog = popup()
            self.dialog.show()
            combo.setCurrentIndex(-1)


        else:
            Date = str(date.today())
            dateItem = QTableWidgetItem(Date)
            self.sheet.setItem(row, 1, dateItem)
            item2 = QTableWidgetItem(str(0.00))
            self.sheet.setItem(row, 2, item2)
            item3 = QTableWidgetItem("")
            self.sheet.setItem(row, 3, item3)
            if (row == len(self.itemName)):
                self.itemName.append(value)
            if (row < len(self.itemName)):
                self.itemName[row] = value

    def addValues(self, item):

        if self.sheet.item(item.row(), item.column()).text() is not None and item.column() == 2:
            Amount = self.sheet.item(item.row(), 2).text()

            if (item.row() == len(self.amount)):
                self.amount.append(Amount)
            if (item.row() < len(self.amount)):
                self.amount[item.row()] = Amount

        if item.column() == 3 and self.sheet.item(item.row(), 3).text is not None:

            Notes = self.sheet.item(item.row(), 3).text()

            if len(Notes) <= 60:

                if (item.row() == len(self.notes)):
                    self.notes.append(Notes)
                if (item.row() < len(self.notes)):
                    self.notes[item.row()] = Notes

            else:
                self.dialog = popup()
                self.dialog.label.setText(
                    "Number of characters in Notes column should be less than 60\n"
                    "Error in row: " + str(item.row() + 1))
                self.dialog.show()
                self.sheet.item(item.row(), 3).setText("")

        if item.column() == 1 and self.sheet.item(item.row(), 1).text is not None:

            Date = self.sheet.item(item.row(), 1).text()

            if self.clearManager == 0:
                try:
                    datetime.strptime(Date, '%Y-%m-%d')
                except ValueError:
                    self.dialog = popup()
                    self.dialog.label.setText(
                        "Values in the Date column should be in the format YYYY-MM-DD\n"
                        "Error in row: " + str(item.row() + 1))
                    self.dialog.show()
                    self.sheet.item(item.row(), 1).setText(str(date.today()))
                if (item.row() == len(self.date)):
                    self.date.append(Date)
                if (item.row() < len(self.date)):
                    self.date[item.row()] = Date

    def total(self, item):

        if (item.column() == 2 and self.sheet.item(item.row() - 1, 2) is not None and self.sheet.item(item.row(),
                                                                                                      2).text() != '') or (
                item.column() == 2 and item.row() == 0 and self.sheet.item(item.row(), 2).text() != ''):

            row = 0
            try:
                totalWeight = 0.0
                for i in range(item.row() + 1):
                    weight = float(self.sheet.item(i, 2).text())
                    totalWeight += weight
                    row += 1
                item1 = QTableWidgetItem(str(round(totalWeight, 2)))
                self.total_sheet.setItem(0, 2, item1)
            except ValueError:
                self.dialog = popup()
                self.dialog.label.setText(
                    "Values in the Amount column cannot be alphabetical and should not contain\n"
                    "special characters like : ,  -   _  !  @   $   %   & etc\n"
                    "Error in row: " + str(row + 1))
                self.dialog.show()
                self.sheet.item(row, 2).setText("0.0")

    def save(self):
        self.setFocus()
        d_c = 0
        length = len(self.itemName)
        for i in range(length):
            values = []

            if self.itemName[i] != "":
                if self.date[i] != "":
                    if self.amount[i] != "":
                        if self.notes[i] is not None:
                            values.append(self.date[i])
                            values.append(self.itemName[i])
                            values.append(self.amount[i])
                            values.append(self.notes[i])

                            # for i in range(31):
                            mycursor.execute(sqlFormula1, values)
                            mydb.commit()

                            if d_c == 0:
                                dc = [str(date.today()), 0, float(self.total_sheet.item(0, 2).text()), "Money out"]
                                mycursor.execute(sqlFormula2, dc)
                                mydb.commit()
                                d_c = 1

                            if i == length - 1:
                                self.clear()
                                self.date = []
                                self.itemName = []
                                self.amount = []
                                self.notes = []
            else:
                self.dialog = popup()
                self.dialog.label.setText(
                    "Some cell is empty please fill it.\nFor Date column please fill appropriate date in the format dd-mm-yyyy.\n"
                    "For Amount column please "
                    "fill in an amount for the empty cell.\n"
                    "For Notes column either fill the note cell or fill the cell with just a space")
                self.dialog.show()

    def clear(self):
        self.sheet.clear()

        col_headers = ["Item Name", "Date", 'Amount', 'Notes']
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)

        self.sheet.setColumnWidth(0, 300)
        self.sheet.setColumnWidth(1, 300)
        self.sheet.setColumnWidth(2, 300)

        mycursor.execute("SELECT * FROM Items")
        result1 = mycursor.fetchall()

        for index in range(100):
            combo = QComboBox()
            combo.setStyleSheet("QComboBox"
                                "{"
                                "background-color: white"
                                "}")
            for row in result1:
                combo.addItem(str(row[1]))
            combo.setProperty('row', index)
            combo.setCurrentIndex(-1)
            if index != 0:
                combo.setEnabled(False)
            combo.currentIndexChanged.connect(lambda: self.setLabour())
            self.sheet.setCellWidget(index, 0, combo)

        self.total_sheet.clear()
        horiz_header = self.total_sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.total_sheet.setColumnWidth(0, 320)
        self.total_sheet.setColumnWidth(1, 300)
        self.total_sheet.setColumnWidth(2, 300)
        self.total_sheet.verticalHeader().setVisible(False)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.clearManager = 1
        for i in range(1, 4):
            for j in range(100):
                boi = QTableWidgetItem(None)
                boi.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable)
                self.sheet.setItem(j, i, boi)

        self.date = []
        self.itemName = []
        self.amount = []
        self.notes = []

    def openItemPage(self):
        self.w = ItemsPage()
        self.w.show()

    def openTotals(self):
        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Choose the option")
        button = QPushButton(self.dialog)
        button.setText("Yearly total")
        button1 = QPushButton(self.dialog)
        button1.setText("Specific total")
        button2 = QPushButton(self.dialog)
        button2.setText("Debit/Credit")
        self.dialog.layout.addWidget(button)
        self.dialog.layout.addWidget(button1)
        self.dialog.layout.addWidget(button2)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(self.openTotalPage)
        button1.clicked.connect(self.openSpecPage)

        button2.clicked.connect(self.openDC)

    def openAdds(self):
        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Choose the option")
        button = QPushButton(self.dialog)
        button.setText("Add Items")
        button1 = QPushButton(self.dialog)
        button1.setText("Add Debit")
        button2 = QPushButton(self.dialog)
        button2.setText("Manage Items")
        self.dialog.layout.addWidget(button)
        self.dialog.layout.addWidget(button1)
        self.dialog.layout.addWidget(button2)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(self.openItemPage)
        button1.clicked.connect(self.openAddDebit)
        button2.clicked.connect(self.openLock)

    def openTotalPage(self):
        self.w = totalWindow()
        self.w.show()

    def openSpecPage(self):
        self.w = specBalance()
        self.w.show()

    def openAddDebit(self):
        self.w = DebitPage()
        self.w.show()

    def openDC(self):
        self.w = debitCredit()
        self.w.show()

    def openChanges(self):

        self.dialog = popup()
        self.dialog.show()

        def openChange(code):
            if code == "Wardah":
                self.dialog.close()
                self.w = changes()
                self.w.show()

        self.dialog.label.setText("Get Authorization")
        form = QFormLayout(self.dialog)
        code = QLineEdit()
        form.addRow("Code: ", code)
        self.dialog.layout.addLayout(form)
        button = QPushButton(self.dialog)
        button.setText("OK")
        self.dialog.layout.addWidget(button)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(lambda: openChange(code.text()))

    def openLock(self):
        self.dialog = popup()
        self.dialog.show()
        query = "SELECT Item_Name, Locked, id from Items"
        mycursor.execute(query)
        res = mycursor.fetchall()
        queryRow = "Select COUNT(Item_Name) from Items"
        mycursor.execute(queryRow)
        rows = mycursor.fetchone()
        sheetV = MyTable(rows[0], 4)
        self.dialog.setFixedWidth(600)
        self.dialog.setFixedHeight(400)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.dialog.layout.addWidget(sheetV)
        self.dialog.okBtn.setVisible(False)
        self.dialog.label.setText("Click the button which you want to be locked")


        def edit():
            sender = self.sender()
            id = sender.property("id")
            name = sender.property("name")
            self.editPop = popup()
            self.editPop.show()
            self.editPop.okBtn.setVisible(False)
            self.editPop.label.setText("Change the name in the given space.\n Restart the application to see changes.")

            form = QFormLayout(self.editPop)
            label = QLabel("New Name: ")
            line = QLineEdit()
            line.setText(name)
            form.addRow(label, line)
            def editS():
                query = "UPDATE Items Set Item_Name = '" + line.text() + "' Where id = " + id
                mycursor.execute(query)
                mydb.commit()
                query1 = "UPDATE expenseBalance Set Item_Name = '" + line.text() +"' WHERE Item_Name ='" + name + "'"
                mycursor.execute(query1)
                mydb.commit()
                change = [str(date.today()), "Items", "Item Name", "edit", name, line.text()]
                mycursor.execute(sqlFormula3, change)
                mydb.commit()
                self.editPop.close()
            button1 = QPushButton(self.editPop)
            button1.setText("Save")
            button1.clicked.connect(editS)
            self.editPop.layout.addLayout(form)
            self.editPop.layout.addWidget(button1)


        def delete():
            sender = self.sender()
            id = sender.property("id")
            name = sender.property("name")
            self.delPop = popup()
            self.delPop.show()
            self.delPop.okBtn.setVisible(False)
            self.delPop.label.setText("Are you sure you want tot delete this item.\n Restart the application to see changes.")

            form = QFormLayout(self.delPop)
            label = QLabel("Name: ")
            line = QLineEdit()
            line.setText(name)
            line.setFixedWidth(100)
            form.addRow(label, line)
            label1 = QLabel("Tick this option to delete all the entries under this name. \n Make sure there is not an exact duplicate of the intended to delete item. \n Else it will result in deletion of all the entries (the original as well as the duplicate. \n If the duplicate exists then change the name first of this item and delete it with the entries.")
            tick = QCheckBox()
            form.addRow(label1, tick)
            def delS():
                queryd = "DELETE FROM Items WHERE id = " + id + " AND item_name = " + "'" + name + "'"
                mycursor.execute(queryd)
                mydb.commit()
                change = [str(date.today()), "Items", "Item Name", "delete", name, "nothing"]
                mycursor.execute(sqlFormula3, change)
                mydb.commit()
                if tick.isChecked():
                    query = "SELECT * FROM expenseBalance WHERE item_name = '" + name + "'"
                    mycursor.execute(query)
                    entries = mycursor.fetchall()
                    rowQuery = "SELECT COUNT(*) FROM expenseBalance WHERE item_name = '" + name + "'"
                    mycursor.execute(rowQuery)
                    rows1 = mycursor.fetchone()
                    backDebit = 0.0
                    for i in range(rows1[0]):
                        entry = []
                        entry.append(str(date.today()))
                        entry.append(str(entries[i][0]))
                        entry.append(entries[i][1])
                        entry.append(entries[i][2])
                        entry.append(entries[i][3])
                        entry.append(entries[i][4])
                        backDebit += entries[i][3]
                        mycursor.execute(sqlFormula4, entry)
                        mydb.commit()

                    dc = []
                    dc.append(str(date.today()))
                    dc.append(backDebit)
                    dc.append(0.0)
                    dc.append("Money back from deletion of" + name)
                    mycursor.execute(sqlFormula2, dc)
                    mydb.commit()
                    query1 = "DELETE FROM expenseBalance WHERE item_name = '" + name + "'"
                    mycursor.execute(query1)
                    mydb.commit()
                self.delPop.close()
            button1 = QPushButton(self.delPop)
            button1.setText("Delete")
            button1.clicked.connect(delS)
            self.delPop.layout.addLayout(form)
            self.delPop.layout.addWidget(button1)


        def save():
            sender = self.sender()
            id = sender.property("id")

            if sender.text() == "Unlocked":
                sender.setText("Locked")
                sender.setStyleSheet("background-color: red; color: white")
                query = "UPDATE Items Set Locked = 'True' Where id = " + id
                mycursor.execute(query)
                mydb.commit()

            else:
                sender.setText("Unlocked")
                sender.setStyleSheet("background-color: green; color: white")
                query = "UPDATE Items Set Locked = 'False' Where id = " + id
                mycursor.execute(query)
                mydb.commit()

        for i in range(rows[0]):
            item = QPushButton("Unlocked")
            item.setStyleSheet("background-color: green; color: white")
            item.setProperty("id", str(res[i][2]))
            item.clicked.connect(save)

            if res[i][1] == "True":
                item.setText("Locked")
                item.setStyleSheet("background-color: red; color: white")

            item1 = QPushButton("Edit")
            item1.setStyleSheet("background-color: green; color: white")
            item1.setProperty("id", str(res[i][2]))
            item1.setProperty("name", res[i][0])
            item1.clicked.connect(edit)

            item2 = QPushButton("Delete")
            item2.setStyleSheet("background-color: red; color: white")
            item2.setProperty("id", str(res[i][2]))
            item2.setProperty("name", res[i][0])
            item2.clicked.connect(delete)

            cell1 = QTableWidgetItem(res[i][0])

            sheetV.setItem(i, 0, cell1)
            sheetV.setCellWidget(i, 1, item)
            sheetV.setCellWidget(i, 2, item1)
            sheetV.setCellWidget(i, 3, item2)


        def close():
            self.dialog.close()

        button1 = QPushButton(self.dialog)
        button1.setText("Close")
        button1.clicked.connect(close)
        self.dialog.layout.addWidget(button1)


class popup(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.label = QLabel("Please fill the above row first.")

        self.okBtn = QPushButton("Ok")

        self.okBtn.clicked.connect(self.wrapper)

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.okBtn)
        self.setLayout(self.layout)

    def wrapper(self):
        self.close()

    def change(self, str):
        self.label.setText(str)


class funcPopup(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        self.label = QLabel("")

        self.okBtn = QPushButton("Ok")

        self.cancel = QPushButton("Cancel")

        layout.addWidget(self.label)
        layout.addWidget(self.okBtn)
        self.setLayout(layout)

    def text(self, str):
        self.label.setText(str)

    def wrapper(self):
        self.close()


class ItemsPage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Item")

        self.setFixedWidth(200)
        self.setFixedHeight(200)

        form = QFormLayout()

        self.accNo = self.accNum()
        form.addRow("Item No", QLabel(self.accNo))
        self.name = QLineEdit()
        form.addRow("Item Name", self.name)

        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.pushed)
        changeLabel = QLabel("Changes will show up on\nrestarting the application")

        screen = QVBoxLayout()
        screen.addLayout(form)
        screen.addWidget(saveBtn)

        widget = QWidget()
        widget.setLayout(screen)
        self.setCentralWidget(widget)

    def accNum(self):
        file_exists = os.path.exists('itemNo.txt')
        if file_exists == False:
            open("itemNo.txt", "w")
        f = open("itemNo.txt", "r+")
        filesize = os.path.getsize("itemNo.txt")
        if (filesize == 0):
            f.write("1")
        accNo = str(f.read())
        f.close()

        return accNo

    def pushed(self):
        self.dialog = popup1(self.name.text(), self)
        self.dialog.show()


class DebitPage(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Debit")

        self.setFixedWidth(200)
        self.setFixedHeight(200)

        form = QFormLayout()

        self.accNo = str(date.today())
        form.addRow("Date", QLabel(self.accNo))
        self.name = QLineEdit()
        form.addRow("Debit Amount", self.name)

        saveBtn = QPushButton("Save")
        saveBtn.clicked.connect(self.pushed)
        changeLabel = QLabel("Changes will show up on\nrestarting the application")

        screen = QVBoxLayout()
        screen.addLayout(form)
        screen.addWidget(saveBtn)

        widget = QWidget()
        widget.setLayout(screen)
        self.setCentralWidget(widget)

    def pushed(self):
        self.dialog = popup2(self.accNo, self.name.text(), self)
        self.dialog.show()


class popup1(QWidget):
    def __init__(self,name, parentWindow):
        super().__init__()
        self.parent = parentWindow
        self.name = name
        layout = QVBoxLayout()
        self.label = QLabel("Please check details.")
        form = QFormLayout()
        form.addRow("Item Name:", QLabel(name))

        okBtn = QPushButton("Ok")
        cancelBtn = QPushButton("Cancel")

        okBtn.clicked.connect(self.pushed)
        cancelBtn.clicked.connect(self.wrapper2)

        form.addRow(okBtn, cancelBtn)

        layout.addWidget(self.label)
        layout.addLayout(form)
        self.setLayout(layout)

    def wrapper1(self):
        self.pushed()

    def wrapper2(self):
        self.close()

    def pushed(self):
        details = []
        details.append(self.name)
        details.append("False")
        mycursor.execute(sqlFormula, details)
        mydb.commit()
        f = open("itemNo.txt", "r+")
        billNo = int(self.accNo) + 1
        f.write(str(billNo))
        f.close()
        self.close()
        self.parent.close()


class popup2(QWidget):
    def __init__(self, accNo, name, parentWindow):
        super().__init__()
        self.parent = parentWindow
        self.name = name
        self.accNo = accNo
        layout = QVBoxLayout()
        self.label = QLabel("Please check details.")
        form = QFormLayout()
        form.addRow("Date:", QLabel(accNo))
        form.addRow("Debit Amount:", QLabel(name))

        okBtn = QPushButton("Ok")
        cancelBtn = QPushButton("Cancel")

        okBtn.clicked.connect(self.pushed)
        cancelBtn.clicked.connect(self.wrapper2)

        form.addRow(okBtn, cancelBtn)

        layout.addWidget(self.label)
        layout.addLayout(form)
        self.setLayout(layout)

    def wrapper1(self):
        self.pushed()

    def wrapper2(self):
        self.close()

    def pushed(self):
        details = []

        details.append(self.accNo)
        details.append(self.name)
        details.append(0)
        details.append("Money in")
        mycursor.execute(sqlFormula2, details)
        mydb.commit()
        self.close()
        self.parent.close()


class totalWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Total Expenses")

        self.setFixedWidth(1400)
        self.setFixedHeight(600)

        header = QHBoxLayout()
        self.header_label = QLabel("Total Expenses Clubbed")
        self.header_label.setFixedSize(600, 40)
        self.header_label.setFont(QFont('Arial', 20))

        self.header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.addWidget(self.header_label)

        iconBox = QGridLayout()
        iconBox_wid1 = Box("red")
        button_row1 = QHBoxLayout(iconBox_wid1)
        self.yearCombo = QComboBox()
        for i in range(2022, 2050):
            self.yearCombo.addItem(str(i))
            self.yearCombo.currentIndexChanged.connect(lambda: self.updateBalance())

        self.pdfBtn = QPushButton("PDF")
        self.pdfBtn.clicked.connect(self.pdf)

        self.modeBtn = QPushButton("Break-down")
        self.modeBtn.clicked.connect(self.modeSwitch)
        button_row1.addWidget(self.yearCombo)
        button_row1.addWidget(self.pdfBtn)
        button_row1.addWidget(self.modeBtn)
        iconBox_wid1.setFixedHeight(50)
        iconBox.addWidget(iconBox_wid1, 0, 0)

        sheet_box = Box("White")
        sheetV = QVBoxLayout(sheet_box)
        rowQuery = "SELECT COUNT(*) from Items"
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        sheet_box.setMaximumHeight(400)
        self.sheet = MyTable(total_rows, 2)
        col_headers = ["Expense Name", "Total Amount"]
        sheetV.setSpacing(0)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.sheet.setColumnWidth(0, 400)
        mycursor.execute("SELECT * FROM Items")
        expName = mycursor.fetchall()
        for i in range(total_rows):
            item = QTableWidgetItem(expName[i][1])
            self.sheet.setItem(i, 0, item)
        year = self.yearCombo.currentText()
        for i in range(total_rows):
            query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + expName[i][1] + "'" + \
                    " and year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            sum = mycursor.fetchone()
            if sum[0] == None:
                item = QTableWidgetItem(str(0))
                self.sheet.setItem(i, 1, item)
            else:
                item = QTableWidgetItem(str(sum[0]))
                self.sheet.setItem(i, 1, item)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        sheetV.addWidget(self.sheet)

        total_sheet_box = Box("White")
        total_sheetV = QVBoxLayout(total_sheet_box)
        total_sheet_box.setMaximumHeight(40)
        self.total_sheet = MyTable(1, 2)
        total_sheetV.setSpacing(0)
        total_sheetV.setContentsMargins(0, 0, 0, 0)
        self.total_sheet.setColumnWidth(0, 400)
        self.total_sheet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)

        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                "year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()

        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        else:
            item1 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        total_sheetV.addWidget(self.total_sheet)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(header)
        mainLayout.addLayout(iconBox)
        mainLayout.addWidget(sheet_box)
        mainLayout.addWidget(total_sheet_box)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def modeSwitch(self):
        self.sheet.clear()
        currentMode = self.modeBtn.text()
        if currentMode == "Break-down":
            self.header_label.setText("Total Expenses Break-Down")
            self.pdfBtn.clicked.connect(self.breakPdf)
            self.modeBtn.setText("Clubbed")
            self.sheet.setColumnCount(self.sheet.horizontalHeader().count() + 2)
            col_headers = ["Date", "Expense Name", "Amount", "Notes"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            self.sheet.setColumnWidth(0, 250)
            self.sheet.setColumnWidth(1, 300)
            self.sheet.setColumnWidth(2, 250)
            self.sheet.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            year = self.yearCombo.currentText()
            rowQuery = "SELECT COUNT(*) FROM expenseBalance WHERE" + \
                       " year(Date) = " + "'" + year + "'"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                query = "SELECT Date, Item_Name, Amount, Notes FROM expenseBalance WHERE" + \
                        " year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchall()

                item = QTableWidgetItem(sum[i][0])
                self.sheet.setItem(i, 0, item)

                item1 = QTableWidgetItem(sum[i][1])
                self.sheet.setItem(i, 1, item1)

                if sum[i][2] == None:
                    item = QTableWidgetItem(str(0))
                    self.sheet.setItem(i, 2, item)
                else:
                    item = QTableWidgetItem(str(sum[i][2]))
                    self.sheet.setItem(i, 2, item)

                item2 = QTableWidgetItem(sum[i][3])
                self.sheet.setItem(i, 3, item2)

            self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        if currentMode == "Clubbed":
            self.pdfBtn.clicked.connect(self.pdf)
            self.header_label.setText("Total Expenses Clubbed")
            self.modeBtn.setText("Break-down")
            self.sheet.setColumnCount(self.sheet.horizontalHeader().count() - 2)
            col_headers = ["Expense Name", "Total Amount"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            self.sheet.setColumnWidth(0, 400)
            self.sheet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
            rowQuery = "SELECT COUNT(*) from Items"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]
            mycursor.execute("SELECT * FROM Items")
            expName = mycursor.fetchall()
            year = self.yearCombo.currentText()

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1
            if rowPosition > total_rows:
                rowsSub = rowPosition - total_rows
                for i in range(rowsSub):
                    self.sheet.removeRow(self.sheet.rowCount() - 1)

            for i in range(total_rows):
                item = QTableWidgetItem(expName[i][1])
                self.sheet.setItem(i, 0, item)
            for i in range(total_rows):
                query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + expName[i][1] + "'" + \
                        " and year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchone()
                if sum[0] == None:
                    item = QTableWidgetItem(str(0))
                    self.sheet.setItem(i, 1, item)
                else:
                    item = QTableWidgetItem(str(sum[0]))
                    self.sheet.setItem(i, 1, item)

            self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def updateBalance(self):
        self.sheet.clear()
        if self.modeBtn.text() == "Break-down":
            col_headers = ["Expense Name", "Total Amount"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            rowQuery = "SELECT COUNT(*) from Items"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]
            mycursor.execute("SELECT * FROM Items")
            expName = mycursor.fetchall()

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                item = QTableWidgetItem(expName[i][1])
                self.sheet.setItem(i, 0, item)
            year = self.yearCombo.currentText()
            for i in range(total_rows):
                query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + expName[i][1] + "'" + \
                        " and year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchone()
                if sum[0] == None:
                    item = QTableWidgetItem(str(0))
                    self.sheet.setItem(i, 1, item)
                else:
                    item = QTableWidgetItem(str(sum[0]))
                    self.sheet.setItem(i, 1, item)

            self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        if self.modeBtn.text() == "Clubbed":
            col_headers = ["Date", "Expense Name", "Amount", "Notes"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            year = self.yearCombo.currentText()
            rowQuery = "SELECT COUNT(*) FROM expenseBalance WHERE" + \
                       " year(Date) = " + "'" + year + "'"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                query = "SELECT Date, Item_Name, Amount, Notes FROM expenseBalance WHERE" + \
                        " year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchall()

                item = QTableWidgetItem(sum[i][0])
                self.sheet.setItem(i, 0, item)

                item1 = QTableWidgetItem(sum[i][1])
                self.sheet.setItem(i, 1, item1)

                if sum[i][2] == None:
                    item = QTableWidgetItem(str(0))
                    self.sheet.setItem(i, 2, item)
                else:
                    item = QTableWidgetItem(str(sum[i][2]))
                    self.sheet.setItem(i, 2, item)

                item2 = QTableWidgetItem(sum[i][3])
                self.sheet.setItem(i, 3, item2)

            self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.total_sheet.clear()
        self.total_sheet.setColumnWidth(0, 400)
        self.total_sheet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)

        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                "year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()
        (result)
        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        else:
            item1 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

# For the break-down version
    def breakPdf(self):
        Date = str(date.today())
        year = self.yearCombo.currentText()
        dayOne = "01/01/" + year
        prevYr = int(year) - 2022

        my_path = "Total-Break/" + str(year) + "--" + Date

        c = canvas.Canvas(my_path + ".pdf", bottomup=1, pagesize=A4)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFont('Helvetica', 25)
        c.drawString(230, 800, "Total Balance")
        c.setFont('Helvetica', 12)
        c.drawString(240, 770, dayOne + " - " + Date)

        # prerequisites
        rowQuery = "SELECT COUNT(*) from expenseBalance WHERE" + \
                       " year(Date) = " + "'" + year + "'"
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        mycursor.execute("SELECT * FROM Items")
        expName = mycursor.fetchall()
        prevBals = 0.0

        query = "SELECT Date, Item_Name, Amount, Notes FROM expenseBalance WHERE year(Date) = " + "'" + str(year) + "'"

        mycursor.execute(query)
        expDetails = mycursor.fetchall()

        currentMode = self.modeBtn.text()  # switches the type of pdf according to the mode

        if currentMode == "Clubbed":

            #For heading

            # mainbox
            c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 2), 20.1 * cm, .8 * cm, fill=0)
            # seperator1
            c.line(100, 689 + (22.65 * 2), 100, 712 + (22.65 * 2))

            # seperator2
            c.line(250, 689 + (22.65 * 2), 250, 712 + (22.65 * 2))

            # seperator3
            c.line(400, 689 + (22.65 * 2), 400, 712 + (22.65 * 2))

            c.drawString(15, 696 + (22.65 * 2), "Date")

            c.drawString(115, 696 + (22.65 * 2), "Expense Name")

            c.drawString(265, 696 + (22.65 * 2), "Amount")

            c.drawString(415, 696 + (22.65 * 2), "Notes")

            # For the previous balance

            # mainbox
            c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 1), 20.1 * cm, .8 * cm, fill=0)
            # seperator1
            c.line(100, 689 + (22.65 * 1), 100, 712 + (22.65 * 1))

            # seperator2
            c.line(250, 689 + (22.65 * 1), 250, 712 + (22.65 * 1))

            # seperator3
            c.line(400, 689 + (22.65 * 1), 400, 712 + (22.65 * 1))

            c.drawString(115, 696 + (22.65 * 1), "Previous Balance")

            if prevYr == 0:
                c.drawString(265, 696 + (22.65 * 1), "SAR 0")

            else:

                for i in range(prevYr):

                    queryPrev = "Select Sum(Amount) From expenseBalance WHERE year(Date) = " + str(2022 + i)
                    mycursor.execute(queryPrev)
                    prevBal = mycursor.fetchone()
                    prevBals += float(prevBal[0])

                c.drawString(265, 696 + (22.65 * 1), "SAR " + str(prevBals))

            for i in range(total_rows):
                if i == 0:
                    min1 = i

                if (i == 30):
                    reqTimes = total_rows - i
                    self.addNewPage(c, reqTimes, 30)
                    break

                # mainbox
                c.rect(.40 * cm, 24.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

                # seperator1
                c.line(100, 689 - (22.65 * i), 100, 712 - (22.65 * i))

                # seperator2
                c.line(250, 689 - (22.65 * i), 250, 712 - (22.65 * i))

                # seperator3
                c.line(400, 689 - (22.65 * i), 400, 712 - (22.65 * i))

                # Expense Date
                c.drawString(15, 696 - (22.65 * i), expDetails[i][0])

                # Expense Name
                if expDetails[i][1] == None:
                    # Expense Name
                    c.drawString(115, 696 - (22.65 * i), "")
                else:
                    # Expense Name
                    c.drawString(115, 696 - (22.65 * i), str(expDetails[i][1]))

                if expDetails[i][2] == None:
                    # Expense Amount
                    c.drawString(265, 696 - (22.65 * i), "SAR " + str(0))
                else:
                    # Expense Amount
                    c.drawString(265, 696 - (22.65 * i), "SAR " + str(expDetails[i][2]))

                if expDetails[i][3] == None:
                    # Expense Note
                    c.drawString(415, 696 - (22.65 * i), "")
                else:
                    # Expense Note
                    c.drawString(415, 696 - (22.65 * i), str(expDetails[i][3]))

                # for the total bar
                if i == total_rows - 1 and i < 30:
                    # mainbox
                    c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(250, 689 - (22.65 * (i + 1)), 250, 712 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15, 696 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                            "year(Date) = " + "'" + str(year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevBals
                    except:
                        value = prevBals
                    if value == None:
                        # Expense Amount
                        c.drawString(265, 696 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Expense Amount
                        c.drawString(265, 696 - (22.65 * (i + 1)), "SAR " + str(value))

        c.showPage()  # saves current page
        c.save()

# For the clubbed version
    def pdf(self):

        Date = str(date.today())
        year = self.yearCombo.currentText()
        dayOne = "01/01/" + year
        prevYr = int(year) - 2022

        my_path = "TotalBills/" + str(year) + "--" + Date

        c = canvas.Canvas(my_path + ".pdf", bottomup=1, pagesize=A4)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFont('Helvetica', 25)
        c.drawString(230, 800, "Total Balance")
        c.setFont('Helvetica', 12)
        c.drawString(240, 770, dayOne + " - " + Date)

        # prerequisites
        rowQuery = "SELECT COUNT(*) from Items"
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        mycursor.execute("SELECT * FROM Items")
        expName = mycursor.fetchall()
        currentMode = self.modeBtn.text()  # switches the type of pdf according to the mode
        prevBals = 0.0

        if currentMode == "Break-down":

            # For Heading

            # mainbox
            c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 2), 20.1 * cm, .8 * cm, fill=0)

            # seperator
            c.line(220, 689 + (22.65 * 2), 220, 712 + (22.65 * 2))

            # Expense Name
            c.drawString(15, 696 + (22.65 * 2), "Expense Name")

            c.drawString(235, 696 + (22.65 * 2), "Amount")

            # For previous balance

            # mainbox
            c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 1), 20.1 * cm, .8 * cm, fill=0)

            # seperator
            c.line(220, 689 + (22.65 * 1), 220, 712 + (22.65 * 1))

            if prevYr == 0:

                # Expense Name
                c.drawString(15, 696 + (22.65 * 1), "Previous Balance")

                c.drawString(235, 696 + (22.65 * 1), "SAR 0")

            else:

                for i in range(prevYr):

                    queryPrev = "Select Sum(Amount) From expenseBalance WHERE year(Date) = " + str(2022 + i)
                    mycursor.execute(queryPrev)
                    prevBal = mycursor.fetchone()
                    prevBals += float(prevBal[0])

                # Expense Name
                c.drawString(15, 696 + (22.65 * 1), "Previous Balance")

                c.drawString(235, 696 + (22.65 * 1), "SAR " + str(prevBals))


            for i in range(total_rows):

                if (i == 30):
                    reqTimes = total_rows - i
                    self.addNewPage(c, reqTimes, 30)
                    break

                # mainbox
                c.rect(.40 * cm, 24.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

                # seperator
                c.line(220, 689 - (22.65 * i), 220, 712 - (22.65 * i))

                # Expense Name
                c.drawString(15, 696 - (22.65 * i), expName[i][1])

                query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + expName[i][1] + "'" + \
                        " and year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchone()
                if sum[0] == None:
                    # Expense Amount
                    c.drawString(235, 696 - (22.65 * i), "SAR " + str(0))
                else:
                    # Expense Amount
                    c.drawString(235, 696 - (22.65 * i), "SAR " + str(sum[0]))

                # for the total bar
                if i == total_rows - 1 and i < 30:
                    # mainbox
                    c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(220, 689 - (22.65 * (i + 1)), 220, 712 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15, 696 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                            "year(Date) = " + "'" + str(year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevBals
                    except:
                        value = prevBals
                    if value == None:
                        # Expense Amount
                        c.drawString(265, 696 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Expense Amount
                        c.drawString(265, 696 - (22.65 * (i + 1)), "SAR " + str(value))

        c.showPage()  # saves current page
        c.save()

    def addNewPage(self, c, reqTimes, timesBeen):
        # this method is to add rows and values to excess pages
        c.showPage()
        c.setPageSize(A4)

        # prerequisites
        year = self.yearCombo.currentText()
        currentMode = self.modeBtn.text()
        prevYr = int(year) - 2022
        prevBals = 0.0

        if prevYr != 0:
            for i in range(prevYr):
                queryPrev = "Select Sum(Amount) From expenseBalance WHERE year(Date) = " + str(2022 + i)
                mycursor.execute(queryPrev)
                prevBal = mycursor.fetchone()
                prevBals += float(prevBal[0])

        if currentMode == "Break-down":

            mycursor.execute("SELECT * FROM Items")
            expName = mycursor.fetchall()

            for i in range(reqTimes):

                if (i == 35):
                    self.addNewPage(c, (reqTimes - i), (timesBeen + i))
                    break
                # mainbox
                c.rect(.40 * cm, 28.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

                # seperator
                c.line(220, 801 - (22.65 * i), 220, 825 - (22.65 * i))

                # Expense Name
                c.drawString(15, 809 - (22.65 * i), expName[timesBeen + i][1])

                query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + expName[timesBeen + i][
                    1] + "'" + \
                        " and year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                sum = mycursor.fetchone()
                if sum[0] == None:
                    # Expense Amount
                    c.drawString(235, 809 - (22.65 * i), "SAR " + str(0))
                else:
                    # Expense Amount
                    c.drawString(235, 809 - (22.65 * i), "SAR " + str(sum[0]))

                # for the total bar
                if reqTimes - i - 1 == 0 and i < 35:
                    if i != 34:
                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(220, 825 - (22.65 * (i + 1)), 220, 802 - (22.65 * (i + 1)))

                        # Total
                        c.drawString(15, 809 - (22.65 * (i + 1)), "Total")

                        # total query
                        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                                "year(Date) = " + "'" + str(year) + "'"
                        mycursor.execute(query)
                        result = mycursor.fetchall()
                        try:
                            value = float(result[0][0]) + prevBals
                        except:
                            value = prevBals
                        if value == None:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                        else:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(value))
                    # creates a new page for total line
                    else:
                        c.showPage()
                        c.setPageSize(A4)
                        i = 0

                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(220, 825 - (22.65 * (i + 1)), 220, 802 - (22.65 * (i + 1)))

                        # Total
                        c.drawString(15, 809 - (22.65 * (i + 1)), "Total")

                        # total query
                        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                                "year(Date) = " + "'" + str(year) + "'"
                        mycursor.execute(query)
                        result = mycursor.fetchall()
                        try:
                            value = float(result[0][0]) + prevBals
                        except:
                            value = prevBals
                        if value == None:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                        else:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(value))

        if currentMode == "Clubbed":
            query = "SELECT Date, Item_Name, Amount, Notes FROM expenseBalance WHERE year(Date) = " + "'" + str(
                year) + "'"

            mycursor.execute(query)
            expDetails = mycursor.fetchall()

            for i in range(reqTimes):

                if (i == 35):
                    self.addNewPage(c, (reqTimes - i), (timesBeen + i))
                    break

                # mainbox
                c.rect(.40 * cm, 28.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

                # seperator1
                c.line(100, 825 - (22.65 * i), 100, 802 - (22.65 * i))

                # seperator2
                c.line(250, 825 - (22.65 * i), 250, 802 - (22.65 * i))

                # seperator3
                c.line(400, 825 - (22.65 * i), 400, 802 - (22.65 * i))

                # Expense Date
                c.drawString(15, 809 - (22.65 * i), expDetails[timesBeen + i][0])

                # Expense Name
                if expDetails[i][1] == None:
                    # Expense Name
                    c.drawString(115, 809 - (22.65 * i), "")
                else:
                    # Expense Name
                    c.drawString(115, 809 - (22.65 * i), str(expDetails[timesBeen + i][1]))

                if expDetails[i][2] == None:
                    # Expense Amount
                    c.drawString(265, 809 - (22.65 * i), "SAR " + str(0))
                else:
                    # Expense Amount
                    c.drawString(265, 809 - (22.65 * i), "SAR " + str(expDetails[timesBeen + i][2]))

                if expDetails[i][3] == None:
                    # Expense Note
                    c.drawString(415, 809 - (22.65 * i), "")
                else:
                    # Expense Note
                    c.drawString(415, 809 - (22.65 * i), str(expDetails[timesBeen + i][3]))

                # for the total bar
                if reqTimes - i - 1 == 0 and i < 35:
                    if i != 34:
                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(250, 825 - (22.65 * (i + 1)), 250, 802 - (22.65 * (i + 1)))

                        # Total
                        c.drawString(15, 809 - (22.65 * (i + 1)), "Total")

                        # total query
                        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                                "year(Date) = " + "'" + str(year) + "'"
                        mycursor.execute(query)
                        result = mycursor.fetchall()
                        value = float(result[0][0]) + prevBals
                        if value == None:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                        else:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(value))
                    # creates a new page for total line
                    else:
                        c.showPage()
                        c.setPageSize(A4)
                        i = 0
                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(250, 825 - (22.65 * (i + 1)), 250, 802 - (22.65 * (i + 1)))

                        # Total
                        c.drawString(15, 809 - (22.65 * (i + 1)), "Total")

                        # total query
                        query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE " + \
                                "year(Date) = " + "'" + str(year) + "'"
                        mycursor.execute(query)
                        result = mycursor.fetchall()
                        value = float(result[0][0]) + prevBals
                        if value == None:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                        else:
                            # Expense Amount
                            c.drawString(265, 809 - (22.65 * (i + 1)), "SAR " + str(value))


class specBalance(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Specific Expense Total")

        self.setFixedWidth(1400)
        self.setFixedHeight(600)

        header = QHBoxLayout()
        header_label = QLabel("Specific Expense Total")
        header_label.setFixedSize(600, 40)
        header_label.setFont(QFont('Arial', 20))

        header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.addWidget(header_label)

        iconBox = QGridLayout()
        iconBox_wid1 = Box("red")
        button_row1 = QHBoxLayout(iconBox_wid1)
        self.yearCombo = QComboBox()
        self.itemCombo = QComboBox()
        rowQuery = "SELECT COUNT(*) from Items"
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]

        mycursor.execute("SELECT * FROM Items")
        result1 = mycursor.fetchall()
        self.itemCombo.addItem("-")
        for row in result1:
            self.itemCombo.addItem(str(row[1]))


        self.itemCombo.currentIndexChanged.connect(lambda: self.lockCheck())


        for i in range(2022, 2050):
            self.yearCombo.addItem(str(i))
            self.yearCombo.currentIndexChanged.connect(lambda: self.updateBalance())

        self.pdfBtn = QPushButton("PDF")
        self.pdfBtn.clicked.connect(self.pdf)

        button_row1.addWidget(self.yearCombo)
        button_row1.addWidget(self.itemCombo)
        button_row1.addWidget(self.pdfBtn)
        iconBox_wid1.setFixedHeight(50)
        iconBox.addWidget(iconBox_wid1, 0, 0)

        year = self.yearCombo.currentText()
        expense = self.itemCombo.currentText()
        if expense != "-":
            rowQuery = "SELECT COUNT(Date) FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                       " and year(Date) = " + "'" + year + "'"
        else:
            rowQuery = "SELECT COUNT(Date) FROM expenseBalance WHERE" + \
                       " year(Date) = " + "'" + year + "'"
        sheet_box = Box("White")
        sheetV = QVBoxLayout(sheet_box)
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        sheet_box.setMaximumHeight(400)
        self.sheet = MyTable(total_rows, 6)
        col_headers = ["id", "Date", "Total Amount", "Notes", "Update", "Delete"]
        sheetV.setSpacing(0)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.sheet.setColumnWidth(0, 100)
        self.sheet.setColumnWidth(1, 300)
        self.sheet.setColumnWidth(2, 300)
        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]

        for i in range(total_rows):
            if expense != "-":
                query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                        " and year(Date) = " + "'" + year + "'"
            else:
                query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE" + \
                        " year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            values = mycursor.fetchall()
            item = QTableWidgetItem(str(values[i][0]))
            item1 = QTableWidgetItem(str(values[i][1]))
            item2 = QTableWidgetItem(str(values[i][2]))
            item3 = QTableWidgetItem(str(values[i][3]))
            self.sheet.setItem(i, 0, item)
            self.sheet.setItem(i, 1, item1)
            self.sheet.setItem(i, 2, item2)
            self.sheet.setItem(i, 3, item3)
            btn1 = QPushButton(self.sheet)
            btn1.setText("Edit")
            btn1.setStyleSheet("background-color: green; color: white")
            btn1.setProperty('row', i)
            btn1.clicked.connect(self.edit)
            self.sheet.setCellWidget(i, 4, btn1)
            btn = QPushButton(self.sheet)
            btn.setText("Delete")
            btn.setStyleSheet("background-color: red; color: white")
            btn.setProperty('row', i)
            btn.clicked.connect(self.delete)
            self.sheet.setCellWidget(i, 5, btn)

        sheetV.addWidget(self.sheet)

        total_sheet_box = Box("White")
        total_sheetV = QVBoxLayout(total_sheet_box)
        total_sheet_box.setMaximumHeight(40)
        self.total_sheet = MyTable(1, 2)
        total_sheetV.setSpacing(0)
        total_sheetV.setContentsMargins(0, 0, 0, 0)
        self.total_sheet.setColumnWidth(0, 300)
        self.total_sheet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)

        if expense != "All":
            query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                    " and year(Date) = " + "'" + year + "'"
        else:
            query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE" + \
                    " year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()

        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        else:
            item1 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        total_sheetV.addWidget(self.total_sheet)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(header)
        mainLayout.addLayout(iconBox)
        mainLayout.addWidget(sheet_box)
        mainLayout.addWidget(total_sheet_box)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def lockCheck(self):
        expense = self.itemCombo.currentText()
        lockQuery = "Select Locked From Items Where Item_Name = '" + expense + "'"
        mycursor.execute(lockQuery)
        lockRes = mycursor.fetchone()
        print(lockRes[0])

        def kbtnClick(code):
            if code == "13/12":
                self.updateBalance()
                self.dialog.close()

        if lockRes[0] == "True":
            self.dialog = popup()
            self.dialog.show()
            self.dialog.label.setText("Get Authorization")
            form = QFormLayout(self.dialog)
            code = QLineEdit()
            form.addRow("Code: ", code)
            self.dialog.layout.addLayout(form)
            button = QPushButton(self.dialog)
            button.setText("OK")
            self.dialog.layout.addWidget(button)
            self.dialog.okBtn.setVisible(False)
            button.clicked.connect(lambda: kbtnClick(code.text()))

        else:
            self.updateBalance()

    def updateBalance(self):
        self.sheet.clear()

        year = self.yearCombo.currentText()
        expense = self.itemCombo.currentText()

        if expense != "All":
            rowQuery = "SELECT COUNT(Date) FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                       " and year(Date) = " + "'" + year + "'"
        else:
            rowQuery = "SELECT COUNT(Date) FROM expenseBalance WHERE" + \
                       " year(Date) = " + "'" + year + "'"

        col_headers = ["id", "Date", "Total Amount", "Notes", "Update", "Delete"]
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.sheet.setColumnWidth(0, 100)
        self.sheet.setColumnWidth(1, 300)
        self.sheet.setColumnWidth(2, 300)

        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]

        rowPosition = self.sheet.rowCount()
        rowsAdd = total_rows - rowPosition
        if rowPosition < total_rows:
            for i in range(rowsAdd):
                self.sheet.insertRow(rowPosition)
                rowPosition += 1

        for i in range(total_rows):
            if expense != "All":
                query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                        " and year(Date) = " + "'" + year + "'"
            else:
                query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE" + \
                        " year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            values = mycursor.fetchall()
            item = QTableWidgetItem(str(values[i][0]))
            item1 = QTableWidgetItem(str(values[i][1]))
            item2 = QTableWidgetItem(str(values[i][2]))
            item3 = QTableWidgetItem(str(values[i][3]))
            self.sheet.setItem(i, 0, item)
            self.sheet.setItem(i, 1, item1)
            self.sheet.setItem(i, 2, item2)
            self.sheet.setItem(i, 3, item3)
            btn1 = QPushButton(self.sheet)
            btn1.setText("Edit")
            btn1.setStyleSheet("background-color: green; color: white")
            btn1.setProperty('row', i)
            btn1.clicked.connect(self.edit)
            self.sheet.setCellWidget(i, 4, btn1)
            btn = QPushButton(self.sheet)
            btn.setText("Delete")
            btn.setStyleSheet("background-color: red; color: white")
            btn.setProperty('row', i)
            btn.clicked.connect(self.delete)
            self.sheet.setCellWidget(i, 5, btn)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.total_sheet.clear()

        self.total_sheet.setColumnWidth(0, 300)
        self.total_sheet.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)

        if expense != "All":
            query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE Item_Name = " + "'" + expense + "'" + \
                    " and year(Date) = " + "'" + year + "'"
        else:
            query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE" + \
                    " year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()

        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        else:
            item1 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def edit(self):
        buttn = self.sender()
        row = buttn.property('row')

        self.bool = "False"

        def kbtnClick(code):

            if code == "Wardah":

                self.dialog.close()
                self.change = popup()
                self.change.show()
                idd = self.sheet.item(row, 0).text()
                dayte = self.sheet.item(row, 1).text()

                total = self.sheet.item(row, 2).text()
                notes = self.sheet.item(row, 3).text()
                itemName = self.itemCombo.currentText()
                form = QFormLayout(self.change)
                line1 = QLineEdit()
                line1.setText(dayte)
                form.addRow("Date: ", line1)
                line4 = QLineEdit()
                line4.setText(itemName)
                form.addRow("Item Name: ", line4)
                line2 = QLineEdit()
                line2.setText(total)
                form.addRow("Total: ", line2)
                line3 = QLineEdit()
                line3.setText(notes)
                form.addRow("Notes: ", line3)
                self.change.layout.addLayout(form)

                self.change.label.setText("Change to new details")
                button = QPushButton(self.change)
                button.setText("OK")
                self.change.layout.addWidget(button)
                self.change.okBtn.setVisible(False)
                button.clicked.connect(lambda: kbtnclick2())

                def kbtnclick2():
                    datee = line1.text()
                    totall = line2.text()
                    notess = line3.text()
                    if notess == "":
                        notess = " "
                    itemNamee = line4.text()
                    query = "UPDATE expenseBalance SET Date = " + "'" + datee + "'" + ", Item_Name = " + "'" + itemNamee + "'" + ", Amount = " + totall + \
                            ", Notes = " + "'" + notess + "'" + " WHERE id = " + "'" + idd + "'" + " AND Date = " + "'" + dayte + "'" + " AND Item_Name = " + "'" + itemName + "'" + \
                            " AND Amount = " + total + " AND Notes = " + "'" + notes + "'"

                    mycursor.execute(query)
                    mydb.commit()
                    diff = float(totall) - float(total)
                    if diff > 0:
                        dc = []
                        dc.append(date.today())
                        dc.append(0.0)
                        dc.append(diff)
                        dc.append("For id: " + idd + " , Changes in: " + itemNamee)
                        mycursor.execute(sqlFormula2, dc)
                        mydb.commit()
                    if diff < 0:
                        dc = []
                        dc.append(date.today())
                        dc.append(diff * (-1.0))
                        dc.append(0.0)
                        dc.append("For id: " + idd + " , Changes in: " + itemNamee)
                        mycursor.execute(sqlFormula2, dc)
                        mydb.commit()

                    if dayte != datee:
                        change = [str(date.today()), "Specific balance", "date", "edit", dayte, datee]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    if total != totall:
                        change = [str(date.today()), "Specific balance", "Amount", "edit", total, totall]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    if notes != notess and notess != " ":
                        change = [str(date.today()), "Specific balance", "notes", "edit", notes, notess]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    if itemName != itemNamee:
                        change = [str(date.today()), "Specific balance", "Item Name", "edit", itemName, itemNamee]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    self.change.close()
                    self.updateBalance()

        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Get Authorization")
        form = QFormLayout(self.dialog)
        code = QLineEdit()
        form.addRow("Code: ", code)
        self.dialog.layout.addLayout(form)
        button = QPushButton(self.dialog)
        button.setText("OK")
        self.dialog.layout.addWidget(button)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(lambda: kbtnClick(code.text()))

    def delete(self):
        buttn = self.sender()
        row = buttn.property('row')

        def kbtnClick(code):

            if code == "Wardah":

                self.dialog.close()
                self.change = popup()
                self.change.show()
                dayte = self.sheet.item(row, 1).text()
                idd = self.sheet.item(row, 0).text()
                total = self.sheet.item(row, 2).text()
                notes = self.sheet.item(row, 3).text()
                itemName = self.itemCombo.currentText()
                query = "SELECT id, date, item_name, amount, notes FROM expenseBalance WHERE item_name = " + "'" + itemName + "'" + " AND date = " + "'" + dayte + "'" + " AND Amount = '" + total + "' AND Notes = '" + notes + "'"
                mycursor.execute(query)
                values = mycursor.fetchall()
                rowQuery = "SELECT COUNT(id) FROM expenseBalance WHERE item_name = " + "'" + itemName + "'" + " AND date = " + "'" + dayte + "'" + " AND Amount = '" + total + "' AND Notes = '" + notes + "'"
                mycursor.execute(rowQuery)
                rowCount = mycursor.fetchone()

                if rowCount[0] > 1:
                    for i in range(rowCount[0]):
                        btn = QPushButton(self.change)
                        btn.setText(str(values[i][0]) + " : " + str(values[i][1]) + " : " + values[i][2] + " : " + str(
                            values[i][3]) + " : " + values[i][4])
                        self.change.layout.addWidget(btn)
                        btn.clicked.connect(lambda: kbtnclick2())
                        btn.setProperty("name", "btn")
                        btn.setProperty("values",
                                        str(values[i][0]) + " : " + str(values[i][1]) + " : " + values[i][
                                            2] + " : " + str(values[i][3]) + " : " + values[i][4])

                    self.change.label.setText(
                        "Select the record you want to delete \n (Click on the record you want to delete)")
                if rowCount[0] == 1:
                    self.change.label.setText(
                        "Check the details of the record you want to delete \n (Click on the record you want to delete)")
                    recBtn = QPushButton(self.change)
                    recBtn.setText(idd + " : " + dayte + " : " + itemName + " : " + total + " : " + notes)
                    self.change.layout.addWidget(recBtn)
                    recBtn.clicked.connect(lambda: kbtnclick2())
                    recBtn.setProperty("name", "rec")
                    recBtn.setProperty("values", idd + " : " + dayte + " : " + itemName + " : " + total + " : " + notes)

                self.change.okBtn.hide()

                def kbtnclick2():
                    pass
                    sender = self.sender()
                    name = sender.property("name")
                    iidd = ""
                    datee = ""
                    totall = ""
                    notess = ""
                    itemNamee = ""
                    if name == "rec":
                        value = sender.property("values")
                        splitted = value.split(" : ")
                        iidd = splitted[0]
                        datee = splitted[1]
                        totall = splitted[3]
                        notess = splitted[4]

                        itemNamee = splitted[2]
                    if name == "btn":
                        value = sender.property("values")
                        splitted = value.split(" : ")
                        iidd = splitted[0]
                        datee = splitted[1]
                        totall = splitted[3]
                        notess = splitted[4]

                        itemNamee = splitted[2]

                    query = "DELETE FROM expenseBalance WHERE id = '" + iidd + "' AND item_name = " + "'" + itemNamee + "'" + " AND date = " + "'" + datee + "'" + " AND Amount = '" + totall + "' AND Notes = '" + notess + "'"
                    #
                    mycursor.execute(query)
                    mydb.commit()
                    dc = []
                    dc.append(date.today())
                    dc.append(totall)
                    dc.append(0.0)
                    dc.append("For id: " + iidd + " , Deletion in: " + itemNamee)
                    mycursor.execute(sqlFormula2, dc)
                    mydb.commit()
                    delete = [str(date.today()), "Specific balance", "Row", "delete",
                              datee + " : " + itemNamee + " : " + totall + " : " + notess, "nothing"]
                    mycursor.execute(sqlFormula3, delete)
                    mydb.commit()

                    self.change.close()
                    self.updateBalance()

        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Get Authorization")
        form = QFormLayout(self.dialog)
        code = QLineEdit()
        form.addRow("Code: ", code)
        self.dialog.layout.addLayout(form)
        button = QPushButton(self.dialog)
        button.setText("OK")
        self.dialog.layout.addWidget(button)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(lambda: kbtnClick(code.text()))

    def pdf(self):
        Date = str(date.today())
        year = self.yearCombo.currentText()
        value = self.itemCombo.currentText()
        dayOne = str(year) + "-01-01"
        my_path = 'Spec/' + value + "--" + Date + '.pdf'
        c = canvas.Canvas(my_path, bottomup=1, pagesize=A4)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFont('Helvetica', 25)
        c.drawString(230, 800, value)
        c.setFont('Helvetica', 12)
        c.drawString(240, 770, dayOne + " - " + Date)

        # prerequisites
        rowQuery = "SELECT COUNT(Date) FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                   " and year(Date) = " + "'" + str(year) + "'"

        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                " and year(Date) = " + "'" + str(year) + "'"

        mycursor.execute(query)
        expDetails = mycursor.fetchall()

        c.setFont('Helvetica', 9)
        prevYr = int(year) - 2022
        prevBals = 0.0
        val = 24.30 * cm  # start point for the rect
        min1 = 0

        # For Header

        # mainbox
        c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 2), 20.1 * cm, .8 * cm, fill=0)

        # seperator1
        c.line(100 + 50, 689 + (22.65 * 2), 100 + 50, 712 + (22.65 * 2))

        # seperator2
        c.line(250 + 50, 689 + (22.65 * 2), 250 + 50, 712 + (22.65 * 2))

        # seperator for id
        c.line(50, 689 + (22.65 * 2), 50, 712 + (22.65 * 2))

        # Expense id
        c.drawString(15, 696 + (22.65 * 2), "id")

        # Expense Date
        c.drawString(15 + 50, 696 + (22.65 * 2), "Date")

        # Expense Amount
        c.drawString(115 + 50, 696 + (22.65 * 2), "Amount")

        # Expense Note
        c.drawString(265 + 50, 696 + (22.65 * 2), "Notes")

        # For previous balance

        # mainbox
        c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 1), 20.1 * cm, .8 * cm, fill=0)

        # seperator1
        c.line(100 + 50, 689 + (22.65 * 1), 100 + 50, 712 + (22.65 * 1))

        # seperator2
        c.line(250 + 50, 689 + (22.65 * 1), 250 + 50, 712 + (22.65 * 1))

        # seperator for id
        c.line(50, 689 + (22.65 * 1), 50, 712 + (22.65 * 1))


        # Expense Date
        c.drawString(15 + 50, 696 + (22.65 * 1), "Previous Balance")


        if prevYr == 0:
            # Expense Amount
            c.drawString(115 + 50, 696 + (22.65 * 1), "SAR 0")

        else:
            for i in range(prevYr):
                query = "SELECT SUM(Amount) FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                        " and year(Date) = " + "'" + str(2022 + i) + "'"
                mycursor.execute(query)
                prevBal = mycursor.fetchone()
                prevBals += float(prevBal[0])

            c.drawString(115 + 50, 696 + (22.65 * 1), "SAR " + str(prevBals))


        for i in range(total_rows):
            if i == 0:
                min1 = i

            if (i == 30):
                reqTimes = total_rows - i
                self.addNewPage(c, reqTimes, 30)
                break


            # mainbox
            c.rect(.40 * cm, 24.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

            # seperator1
            c.line(100 + 50, 689 - (22.65 * i), 100 + 50, 712 - (22.65 * i))

            # seperator2
            c.line(250 + 50, 689 - (22.65 * i), 250 + 50, 712 - (22.65 * i))

            # seperator for id
            c.line(50, 689 - (22.65 * i), 50, 712 - (22.65 * i))

            # Expense id
            c.drawString(15, 696 - (22.65 * i), str(expDetails[i][0]))

            # Expense Date
            c.drawString(15 + 50, 696 - (22.65 * i), expDetails[i][1])

            if expDetails[i][2] == None:
                # Expense Amount
                c.drawString(115 + 50, 696 - (22.65 * i), "SAR " + str(0))
            else:
                # Expense Amount
                c.drawString(115 + 50, 696 - (22.65 * i), "SAR " + str(expDetails[i][2]))

            if expDetails[i][3] == None:
                # Expense Note
                c.drawString(265 + 50, 696 - (22.65 * i), "")
            else:
                # Expense Note
                c.drawString(265 + 50, 696 - (22.65 * i), str(expDetails[i][3]))

            # for the total bar
            if i == total_rows - 1 and i < 30:
                # mainbox
                c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                # seperator1
                c.line(100 + 50, 689 - (22.65 * (i + 1)), 100 + 50, 712 - (22.65 * (i + 1)))

                # Total
                c.drawString(15 + 50, 696 - (22.65 * (i + 1)), "Total")

                # total query
                query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                        " and year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                result = mycursor.fetchall()
                try:
                    value = float(result[0][0]) + prevBals
                except:
                    value = prevBals
                if value == None:
                    # Expense Amount total
                    c.drawString(115 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(0))
                else:
                    # Expense Amount total
                    c.drawString(115 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(value))




        c.showPage()  # saves current page
        c.save()

    def addNewPage(self, c, reqTimes, timesBeen):
        # this method is to add rows and values to excess pages
        c.showPage()
        c.setPageSize(A4)

        # prerequisites
        year = self.yearCombo.currentText()
        value = self.itemCombo.currentText()
        query = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                " and year(Date) = " + "'" + str(year) + "'"

        mycursor.execute(query)
        expDetails = mycursor.fetchall()
        c.setFont('Helvetica', 9)
        prevYr = int(year) - 2022
        prevBals = 0.0

        if prevYr != 0:
            for i in range(prevYr):
                queryPrev = "SELECT id, Date, Amount, Notes FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                " and year(Date) = " + "'" + str(2022 + i) + "'"
                mycursor.execute(queryPrev)
                prevBal = mycursor.fetchone()
                prevBals += float(prevBal[0])


        for i in range(reqTimes):

            if (i == 35):
                self.addNewPage(c, (reqTimes - i), (timesBeen + i))
                break
            # mainbox
            c.rect(.40 * cm, 28.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

            # seperator1
            c.line(100 + 50, 801 - (22.65 * i), 100 + 50, 825 - (22.65 * i))

            # seperator2
            c.line(250 + 50, 801 - (22.65 * i), 250 + 50, 825 - (22.65 * i))

            # seperator for id
            c.line(50, 801 - (22.65 * i), 50, 825 - (22.65 * i))

            # Expense id
            c.drawString(15, 809 - (22.65 * i), str(expDetails[timesBeen + i][0]))

            # Expense Date
            c.drawString(15 + 50, 809 - (22.65 * i), expDetails[timesBeen + i][1])

            if expDetails[i][2] == None:
                # Expense Amount
                c.drawString(115 + 50, 809 - (22.65 * i), "SAR " + str(0))
            else:
                # Expense Amount
                c.drawString(115 + 50, 809 - (22.65 * i), "SAR " + str(expDetails[timesBeen + i][2]))

            if expDetails[i][3] == None:
                # Expense Note
                c.drawString(265 + 50, 812 - (22.65 * i), "")
            else:
                # Expense Note
                c.drawString(265 + 50, 812 - (22.65 * i), str(expDetails[timesBeen + i][3]))

            # for the total bar
            if reqTimes - i - 1 == 0 and i < 35:
                if i != 34:
                    # mainbox
                    c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 825 - (22.65 * (i + 1)), 100 + 50, 802 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15 + 50, 809 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                            " and year(Date) = " + "'" + str(year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevBals
                    except:
                        value = prevBals
                    if value == None:
                        # Expense Amount total
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Expense Amount total
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value))
                else:
                    c.showPage()
                    c.setPageSize(A4)
                    i = 0

                    # mainbox
                    c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 825 - (22.65 * (i + 1)), 100 + 50, 802 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15, 809 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Amount) AS 'totalAmount' FROM expenseBalance WHERE Item_Name = " + "'" + value + "'" + \
                            " and year(Date) = " + "'" + str(year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevBals
                    except:
                        value = prevBals
                    if value == None:
                        # Expense Amount total
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Expense Amount total
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value))


class debitCredit(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Debit/Credit")

        self.setFixedWidth(1400)
        self.setFixedHeight(600)

        header = QHBoxLayout()
        header_label = QLabel("Debit/Credit")
        header_label.setFixedSize(600, 40)
        header_label.setFont(QFont('Arial', 20))

        header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.addWidget(header_label)

        iconBox = QGridLayout()
        iconBox_wid1 = Box("red")
        button_row1 = QHBoxLayout(iconBox_wid1)
        self.yearCombo = QComboBox()

        for i in range(2022, 2050):
            self.yearCombo.addItem(str(i))
            self.yearCombo.currentIndexChanged.connect(lambda: self.updateBalance())

        self.pdfBtn = QPushButton("PDF")
        self.pdfBtn.clicked.connect(self.pdf)

        button_row1.addWidget(self.yearCombo)
        button_row1.addWidget(self.pdfBtn)
        iconBox_wid1.setFixedHeight(50)
        iconBox.addWidget(iconBox_wid1, 0, 0)

        year = self.yearCombo.currentText()

        rowQuery = "SELECT COUNT(Date) FROM Debit_Credit WHERE " + \
                   " year(Date) = " + "'" + year + "'"

        sheet_box = Box("White")
        sheetV = QVBoxLayout(sheet_box)
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        sheet_box.setMaximumHeight(400)
        self.sheet = MyTable(total_rows, 7)
        col_headers = ["id", "Date", "Debit", "Credit", "Notes", "Update", "Delete"]
        sheetV.setSpacing(0)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.sheet.setColumnWidth(0, 100)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        for i in range(total_rows):
            query = "SELECT id, Date, Debit, Credit, Notes FROM Debit_Credit WHERE" + \
                    " year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            values = mycursor.fetchall()
            item = QTableWidgetItem(str(values[i][0]))
            item1 = QTableWidgetItem(str(values[i][1]))
            item2 = QTableWidgetItem(str(values[i][2]))
            item3 = QTableWidgetItem(str(values[i][3]))
            item4 = QTableWidgetItem(str(values[i][4]))
            self.sheet.setItem(i, 0, item)
            self.sheet.setItem(i, 1, item1)
            self.sheet.setItem(i, 2, item2)
            self.sheet.setItem(i, 3, item3)
            self.sheet.setItem(i, 4, item4)
            btn1 = QPushButton(self.sheet)
            btn1.setText("Edit")
            btn1.setStyleSheet("background-color: green; color: white")
            btn1.setProperty('row', i)
            btn1.clicked.connect(self.edit)
            self.sheet.setCellWidget(i, 5, btn1)
            btn = QPushButton(self.sheet)
            btn.setText("Delete")
            btn.setStyleSheet("background-color: red; color: white")
            btn.setProperty('row', i)
            btn.clicked.connect(self.delete)
            self.sheet.setCellWidget(i, 6, btn)

        sheetV.addWidget(self.sheet)

        total_sheet_box = Box("White")
        total_sheetV = QVBoxLayout(total_sheet_box)
        total_sheet_box.setMaximumHeight(40)
        self.total_sheet = MyTable(1, 4)
        total_sheetV.setSpacing(0)
        self.total_sheet.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        total_sheetV.setContentsMargins(0, 0, 0, 0)
        self.total_sheet.setColumnWidth(0, 400)

        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)

        query = "SELECT SUM(Debit) AS 'totalDebit', SUM(Credit) AS 'totalCredit' FROM Debit_Credit WHERE year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()

        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            item2 = QTableWidgetItem(str(result[0][1]))
            item3 = QTableWidgetItem(str(result[0][0] - result[0][1]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)
            self.total_sheet.setItem(0, 2, item2)
            self.total_sheet.setItem(0, 3, item3)

        else:
            item1 = QTableWidgetItem(str(0))
            item2 = QTableWidgetItem(str(0))
            item3 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)
            self.total_sheet.setItem(0, 2, item2)
            self.total_sheet.setItem(0, 3, item3)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        total_sheetV.addWidget(self.total_sheet)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(header)
        mainLayout.addLayout(iconBox)
        mainLayout.addWidget(sheet_box)
        mainLayout.addWidget(total_sheet_box)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def updateBalance(self):
        self.sheet.clear()

        year = self.yearCombo.currentText()

        rowQuery = "SELECT COUNT(Date) FROM Debit_Credit WHERE" + \
                   " year(Date) = " + "'" + year + "'"

        col_headers = ["id", "Date", "Debit", "Credit", "Notes", "Update", "Delete"]
        self.sheet.setHorizontalHeaderLabels(col_headers)
        horiz_header = self.sheet.horizontalHeader()
        horiz_header.setSectionResizeMode(4, QHeaderView.Stretch)
        self.sheet.setColumnWidth(0, 100)

        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]

        rowPosition = self.sheet.rowCount()
        rowsAdd = total_rows - rowPosition
        if rowPosition < total_rows:
            for i in range(rowsAdd):
                self.sheet.insertRow(rowPosition)
                rowPosition += 1

        for i in range(total_rows):
            query = "SELECT id, Date, Debit, Credit, Notes FROM Debit_Credit WHERE" + \
                    " year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            values = mycursor.fetchall()
            item = QTableWidgetItem(str(values[i][0]))
            item1 = QTableWidgetItem(str(values[i][1]))
            item2 = QTableWidgetItem(str(values[i][2]))
            item3 = QTableWidgetItem(str(values[i][3]))
            item4 = QTableWidgetItem(str(values[i][4]))
            self.sheet.setItem(i, 0, item)
            self.sheet.setItem(i, 1, item1)
            self.sheet.setItem(i, 2, item2)
            self.sheet.setItem(i, 3, item3)
            self.sheet.setItem(i, 4, item4)
            btn1 = QPushButton(self.sheet)
            btn1.setText("Edit")
            btn1.setStyleSheet("background-color: green; color: white")
            btn1.setProperty('row', i)
            btn1.clicked.connect(self.edit)
            self.sheet.setCellWidget(i, 5, btn1)
            btn = QPushButton(self.sheet)
            btn.setText("Delete")
            btn.setStyleSheet("background-color: red; color: white")
            btn.setProperty('row', i)
            btn.clicked.connect(self.delete)
            self.sheet.setCellWidget(i, 6, btn)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.total_sheet.clear()
        self.total_sheet.setColumnWidth(0, 300)
        self.total_sheet.horizontalHeader().setVisible(False)
        self.total_sheet.verticalHeader().setVisible(False)
        self.total_sheet.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        query = "SELECT SUM(Debit) AS 'totalDebit', SUM(Credit) AS 'totalCredit' FROM Debit_Credit WHERE year(Date) = " + "'" + year + "'"
        mycursor.execute(query)
        result = mycursor.fetchall()

        item = QTableWidgetItem("Total")
        if result[0][0] != None:
            item1 = QTableWidgetItem(str(result[0][0]))
            item2 = QTableWidgetItem(str(result[0][1]))
            item3 = QTableWidgetItem(str(result[0][0] - result[0][1]))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)
            self.total_sheet.setItem(0, 2, item2)
            self.total_sheet.setItem(0, 3, item3)

        else:
            item1 = QTableWidgetItem(str(0))
            item2 = QTableWidgetItem(str(0))
            item3 = QTableWidgetItem(str(0))
            self.total_sheet.setItem(0, 0, item)
            self.total_sheet.setItem(0, 1, item1)
            self.total_sheet.setItem(0, 2, item2)
            self.total_sheet.setItem(0, 3, item3)

        self.total_sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def edit(self):
        buttn = self.sender()
        row = buttn.property('row')

        self.bool = "False"

        def kbtnClick(code):

            if code == "Wardah":

                self.dialog.close()
                self.change = popup()
                self.change.show()
                idd = self.sheet.item(row, 0).text()
                dayte = self.sheet.item(row, 1).text()

                debit = self.sheet.item(row, 2).text()
                credit = self.sheet.item(row, 3).text()

                form = QFormLayout(self.change)
                line1 = QLineEdit()
                line1.setText(dayte)
                form.addRow("Date: ", line1)
                line2 = QLineEdit()
                line2.setText(debit)
                form.addRow("Debit: ", line2)
                line3 = QLineEdit()
                line3.setText(credit)
                form.addRow("Credit: ", line3)
                self.change.layout.addLayout(form)

                self.change.label.setText("Change to new details")
                button = QPushButton(self.change)
                button.setText("OK")
                self.change.layout.addWidget(button)
                self.change.okBtn.setVisible(False)
                button.clicked.connect(lambda: kbtnclick2())

                def kbtnclick2():
                    datee = line1.text()
                    totall = line2.text()
                    notess = line3.text()
                    if notess == "":
                        notess = " "

                    query = "UPDATE debit_credit SET Date = " + "'" + datee + "'" + ", debit = " + totall + ", credit " \
                                                                                                            "= " + \
                            notess + \
                            ", notes = 'Changed' WHERE id = " + "'" + idd + "'" + " AND Date = " + "'" + dayte + "'" + "AND debit = " + debit + \
                            " AND credit = " + credit

                    if dayte != datee:
                        change = [str(date.today()), "debit/credit", "date", "edit", dayte, datee]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    if debit != totall:
                        change = [str(date.today()), "debit/credit", "debit", "edit", debit, totall]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()

                    if credit != notess:
                        change = [str(date.today()), "debit/credit", "credit", "edit", credit, notess]
                        mycursor.execute(sqlFormula3, change)
                        mydb.commit()
                    mycursor.execute(query)
                    mydb.commit()
                    self.change.close()
                    self.updateBalance()

        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Get Authorization")
        form = QFormLayout(self.dialog)
        code = QLineEdit()
        form.addRow("Code: ", code)
        self.dialog.layout.addLayout(form)
        button = QPushButton(self.dialog)
        button.setText("OK")
        self.dialog.layout.addWidget(button)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(lambda: kbtnClick(code.text()))

    def delete(self):
        buttn = self.sender()
        row = buttn.property('row')

        def kbtnClick(code):
            if code == "Wardah":
                self.dialog.close()
                self.change = popup()
                self.change.show()
                dayte = self.sheet.item(row, 1).text()
                idd = self.sheet.item(row, 0).text()
                debit = self.sheet.item(row, 2).text()
                credit = self.sheet.item(row, 3).text()
                query = "SELECT id, Date, Debit, Credit FROM debit_credit WHERE Date = " + "'" + dayte + "'" + " AND Debit = " + debit + " AND Credit = " + credit
                mycursor.execute(query)
                values = mycursor.fetchall()
                rowQuery = "SELECT COUNT(id) FROM debit_credit WHERE Date = " + "'" + dayte + "'" + " AND Debit = " + debit + " AND Credit = " + credit
                mycursor.execute(rowQuery)
                rowCount = mycursor.fetchone()

                self.change.label.setText(
                    "Check the details of the record you want to delete \n (Click on the record you want to delete)")
                recBtn = QPushButton(self.change)
                recBtn.setText(idd + " : " + dayte + " : " + debit + " : " + credit)
                self.change.layout.addWidget(recBtn)

                recBtn.clicked.connect(lambda: kbtnclick2())
                self.change.okBtn.hide()

                def kbtnclick2():
                    query = "DELETE FROM debit_credit WHERE id = '" + idd + "' AND debit = " + debit + " AND date = " + "'" + dayte + "'" + " AND credit = " + credit
                    delete = [str(date.today()), "debit/credit", "Row", "delete",
                              dayte + " : " + debit + " : " + credit, "nothing"]
                    mycursor.execute(sqlFormula3, delete)
                    mydb.commit()
                    mycursor.execute(query)
                    mydb.commit()
                    self.change.close()
                    self.updateBalance()

        self.dialog = popup()
        self.dialog.show()
        self.dialog.label.setText("Get Authorization")
        form = QFormLayout(self.dialog)
        code = QLineEdit()
        form.addRow("Code: ", code)
        self.dialog.layout.addLayout(form)
        button = QPushButton(self.dialog)
        button.setText("OK")
        self.dialog.layout.addWidget(button)
        self.dialog.okBtn.setVisible(False)
        button.clicked.connect(lambda: kbtnClick(code.text()))

    def pdf(self):
        Date = str(date.today())
        year = self.yearCombo.currentText()
        dayOne = str(year) + "-01-01"
        my_path = "D-C/" + year + "-- " + Date + '.pdf'
        c = canvas.Canvas(my_path, bottomup=1, pagesize=A4)
        c.setStrokeColorRGB(0, 0, 0)
        c.setFont('Helvetica', 25)
        c.drawString(230, 800, "Debit/Credit")
        c.setFont('Helvetica', 12)
        c.drawString(240, 770, dayOne + " - " + Date)

        # prerequisites
        rowQuery = "SELECT COUNT(Date) FROM Debit_Credit WHERE" + \
                   " year(Date) = " + "'" + str(year) + "'"
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        query = "SELECT id, Date, Debit, Credit FROM Debit_Credit WHERE" + \
                " year(Date) = " + "'" + str(year) + "'"
        mycursor.execute(query)
        expDetails = mycursor.fetchall()

        c.setFont('Helvetica', 9)
        prevYr = int(year) - 0
        prevDebs = 0.0
        prevCreds = 0.0
        val = 24.30 * cm  # start point for the rect
        min1 = 0

        #  For Heading

        # mainbox
        c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 2), 20.1 * cm, .8 * cm, fill=0)

        # seperator1
        c.line(100 + 50, 689 + (22.65 * 2), 100 + 50, 712 + (22.65 * 2))

        # seperator2
        c.line(350 + 50, 689 + (22.65 * 2), 350 + 50, 712 + (22.65 * 2))

        # seperator for id
        c.line(50, 689 + (22.65 * 2), 50, 712 + (22.65 * 2))

        # Transaction id
        c.drawString(15, 696 + (22.65 * 2), "id")

        # Transaction Date
        c.drawString(15 + 50, 696 + (22.65 * 2), "Date")

        # Debit Amt
        c.drawString(115 + 50, 696 + (22.65 * 2), "Debit")

        # Credit Amt
        c.drawString(365 + 50, 696 + (22.65 * 2), "Credit")

        # For previous balance

        # mainbox
        c.rect(.40 * cm, 24.30 * cm + (.8 * cm * 1), 20.1 * cm, .8 * cm, fill=0)

        # seperator1
        c.line(100 + 50, 689 + (22.65 * 1), 100 + 50, 712 + (22.65 * 1))

        # seperator2
        c.line(350 + 50, 689 + (22.65 * 1), 350 + 50, 712 + (22.65 * 1))

        # seperator for id
        c.line(50, 689 + (22.65 * 1), 50, 712 + (22.65 * 1))

        # Transaction Date
        c.drawString(15 + 50, 696 + (22.65 * 1), "Previous Balance")

        if prevYr == 0:

            # Debit Amt
            c.drawString(115 + 50, 696 + (22.65 * 1), "SAR 0")

            # Credit Amt
            c.drawString(365 + 50, 696 + (22.65 * 1), "SAR 0")

        else:
            for i in range(prevYr):
                query = "SELECT Sum(Debit), Sum(Credit) FROM Debit_Credit WHERE" + \
                   " year(Date) = " + "'" + str(2022 + i) + "'"
                mycursor.execute(query)
                prevBal = mycursor.fetchall()
                prevDeb = prevBal[0][0]
                prevDebs += float(prevDeb)
                prevCred = prevBal[0][1]
                prevCreds += float(prevCred)

                # Debit Amt
                c.drawString(115 + 50, 696 + (22.65 * 1), "SAR " + prevDebs)

                # Credit Amt
                c.drawString(365 + 50, 696 + (22.65 * 1), "SAR " + prevCreds)


        for i in range(total_rows):
            if i == 0:
                min1 = i

            if (i == 29):
                reqTimes = total_rows - i
                self.addNewPage(c, reqTimes, 29)
                break

            # mainbox
            c.rect(.40 * cm, 24.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

            # seperator1
            c.line(100 + 50, 689 - (22.65 * i), 100 + 50, 712 - (22.65 * i))

            # seperator2
            c.line(350 + 50, 689 - (22.65 * i), 350 + 50, 712 - (22.65 * i))

            # seperator for id
            c.line(50, 689 - (22.65 * i), 50, 712 - (22.65 * i))

            # Transaction id
            c.drawString(15, 696 - (22.65 * i), str(expDetails[i][0]))

            # Transaction Date
            c.drawString(15 + 50, 696 - (22.65 * i), expDetails[i][1])

            if expDetails[i][2] == None:
                # Debit Amt
                c.drawString(115 + 50, 696 - (22.65 * i), "SAR " + str(0))
            else:
                # Debit Amt
                c.drawString(115 + 50, 696 - (22.65 * i), "SAR " + str(expDetails[i][2]))

            if expDetails[i][3] == None:
                # Credit Amt
                c.drawString(365 + 50, 696 - (22.65 * i), "SAR " + str(0))
            else:
                # Credit Amt
                c.drawString(365 + 50, 696 - (22.65 * i), "SAR " + str(expDetails[i][3]))

            # for the total bar
            if i == total_rows - 1 and i < 29:
                # mainbox
                c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                # seperator1
                c.line(100 + 50, 689 - (22.65 * (i + 1)), 100 + 50, 712 - (22.65 * (i + 1)))

                # seperator2
                c.line(350 + 50, 689 - (22.65 * (i + 1)), 350 + 50, 712 - (22.65 * (i + 1)))

                # Total
                c.drawString(15 + 50, 696 - (22.65 * (i + 1)), "Total")

                # total query
                query = "SELECT SUM(Debit) AS 'totalDebit', SUM(Credit) AS 'totalCredit' FROM Debit_Credit WHERE year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                result = mycursor.fetchall()
                try:
                    value = float(result[0][0]) + prevDebs
                    value1 = float(result[0][1]) + prevCreds
                except:
                    value = prevDebs
                    value1 = prevCreds
                if value == None:
                    # Total Debit
                    c.drawString(115 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(0))
                else:
                    # Total Debit
                    c.drawString(115 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(value))

                if value1 == None:
                    # Total Credit
                    c.drawString(365 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(0))
                else:
                    # Total Credit
                    c.drawString(365 + 50, 696 - (22.65 * (i + 1)), "SAR " + str(value1))

                if value1 != None and value != None:
                    bal = value - value1

                    # mainbox
                    c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 689 - (22.65 * (i + 2)), 100 + 50, 712 - (22.65 * (i + 2)))

                    # Total
                    c.drawString(15 + 50, 696 - (22.65 * (i + 2)), "Balance")

                    c.drawString(115 + 50, 696 - (22.65 * (i + 2)), "SAR " + str(bal))

                else:
                    # mainbox
                    c.rect(.40 * cm, 24.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 689 - (22.65 * (i + 2)),  + 50, 712 - (22.65 * (i + 2)))

                    # Total
                    c.drawString(15 + 50, 696 - (22.65 * (i + 2)), "Balance")

                    c.drawString(115 + 50, 696 - (22.65 * (i + 2)), "SAR " + str(0))

        c.showPage()  # saves current page
        c.save()

    def addNewPage(self, c, reqTimes, timesBeen):
        # this method is to add rows and values to excess pages
        c.showPage()
        c.setPageSize(A4)

        # prerequisites
        year = self.yearCombo.currentText()
        query = "SELECT id, Date, Debit, Credit FROM Debit_Credit WHERE" + \
                " year(Date) = " + "'" + str(year) + "'"
        mycursor.execute(query)
        expDetails = mycursor.fetchall()
        c.setFont('Helvetica', 9)
        prevYr = int(year) - 2022
        prevDebs = 0.0
        prevCreds = 0.0

        if prevYr == 0:
            for i in range(prevYr):
                query = "SELECT Sum(Debit), Sum(Credit) FROM Debit_Credit WHERE" + \
                   " year(Date) = " + "'" + str(2022 + i) + "'"
                mycursor.execute(query)
                prevBal = mycursor.fetchall()
                prevDeb = prevBal[0][0]
                prevDebs += float(prevDeb)
                prevCred = prevBal[0][1]
                prevCreds += float(prevCred)

        for i in range(reqTimes):

            if (i == 35):
                self.addNewPage(c, (reqTimes - i), (timesBeen + i))
                break
            # mainbox
            c.rect(.40 * cm, 28.30 * cm - (.8 * cm * i), 20.1 * cm, .8 * cm, fill=0)

            # seperator1
            c.line(100 + 50, 801 - (22.65 * i), 100 + 50, 825 - (22.65 * i))

            # seperator2
            c.line(350 + 50, 801 - (22.65 * i), 350 + 50, 825 - (22.65 * i))

            # seperator for id
            c.line(50, 801 - (22.65 * i), 50, 825 - (22.65 * i))

            # Transaction id
            c.drawString(15, 809 - (22.65 * i), str(expDetails[timesBeen + i][0]))

            # Transaction Date
            c.drawString(15 + 50, 809 - (22.65 * i), expDetails[timesBeen + i][1])

            if expDetails[i][2] == None:
                # Debit Amt
                c.drawString(115 + 50, 809 - (22.65 * i), "SAR " + str(0))
            else:
                # Debit Amt
                c.drawString(115 + 50, 809 - (22.65 * i), "SAR " + str(expDetails[timesBeen + i][2]))

            if expDetails[i][3] == None:
                # Credit Amt
                c.drawString(365 + 50, 812 - (22.65 * i), "SAR " + str(0))
            else:
                # Credit Amt
                c.drawString(365 + 50, 812 - (22.65 * i), "SAR " + str(expDetails[timesBeen + i][3]))

            # for the total bar
            if reqTimes - i - 1 == 0 and i < 35:
                if i != 34:
                    # mainbox
                    c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 825 - (22.65 * (i + 1)), 100 + 50, 802 - (22.65 * (i + 1)))

                    # seperator2
                    c.line(350 + 50, 825 - (22.65 * (i + 1)), 350 + 50, 802 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15 + 50, 809 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Debit) AS 'totalDebit', SUM(Credit) AS 'totalCredit' FROM Debit_Credit WHERE year(Date) = " + "'" + str(
                        year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevDebs
                        value1 = float(result[0][1]) + prevCreds
                    except:
                        value = prevDebs
                        value1 = prevCreds
                    if value == None:
                        # Total Debit
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Total Debit
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value))

                    if value1 == None:
                        # Total Credit
                        c.drawString(365 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Total Credit
                        c.drawString(365 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value1))

                    if value1 != None and value != None:
                        bal = value - value1

                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(100 + 50, 825 - (22.65 * (i + 2)), 100 + 50, 802 - (22.65 * (i + 2)))

                        # Total
                        c.drawString(15 + 50, 809 - (22.65 * (i + 2)), "Balance")

                        c.drawString(115 + 50, 809 - (22.65 * (i + 2)), "SAR " + str(bal))

                    else:
                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(100 + 50, 825 - (22.65 * (i + 2)), 100 + 50, 802 - (22.65 * (i + 2)))

                        # Total
                        c.drawString(15 + 50, 809 - (22.65 * (i + 2)), "Balance")

                        c.drawString(115 + 50, 809 - (22.65 * (i + 2)), "SAR " + str(0))
                else:
                    c.showPage()
                    c.setPageSize(A4)

                    i = 0

                    # mainbox
                    c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 1)), 20.1 * cm, .8 * cm, fill=0)

                    # seperator1
                    c.line(100 + 50, 825 - (22.65 * (i + 1)), 100 + 50, 802 - (22.65 * (i + 1)))

                    # seperator2
                    c.line(350 + 50, 825 - (22.65 * (i + 1)), 350 + 50, 802 - (22.65 * (i + 1)))

                    # Total
                    c.drawString(15 + 50, 809 - (22.65 * (i + 1)), "Total")

                    # total query
                    query = "SELECT SUM(Debit) AS 'totalDebit', SUM(Credit) AS 'totalCredit' FROM Debit_Credit WHERE year(Date) = " + "'" + str(
                        year) + "'"
                    mycursor.execute(query)
                    result = mycursor.fetchall()
                    try:
                        value = float(result[0][0]) + prevDebs
                        value1 = float(result[0][1]) + prevCreds
                    except:
                        value = prevDebs
                        value1 = prevCreds
                    if value == None:
                        # Total Debit
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Total Debit
                        c.drawString(115 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value))

                    if value1 == None:
                        # Total Credit
                        c.drawString(365 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(0))
                    else:
                        # Total Credit
                        c.drawString(365 + 50, 809 - (22.65 * (i + 1)), "SAR " + str(value1))

                    if value1 != None and value != None:
                        bal = value - value1

                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(100 + 50, 825 - (22.65 * (i + 2)), 100 + 50, 802 - (22.65 * (i + 2)))

                        # Total
                        c.drawString(15 + 50, 809 - (22.65 * (i + 2)), "Balance")

                        c.drawString(115 + 50, 809 - (22.65 * (i + 2)), "SAR " + str(bal))

                    else:
                        # mainbox
                        c.rect(.40 * cm, 28.30 * cm - (.8 * cm * (i + 2)), 20.1 * cm, .8 * cm, fill=0)

                        # seperator1
                        c.line(100 + 50, 825 - (22.65 * (i + 2)), 100 + 50, 802 - (22.65 * (i + 2)))

                        # Total
                        c.drawString(15 + 50, 809 - (22.65 * (i + 2)), "Balance")

                        c.drawString(115 + 50, 809 - (22.65 * (i + 2)), "SAR " + str(0))


class changes(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Changes")

        self.setFixedWidth(1400)
        self.setFixedHeight(600)

        header = QHBoxLayout()
        self.header_label = QLabel("Changes")
        self.header_label.setFixedSize(600, 40)
        self.header_label.setFont(QFont('Arial', 20))

        self.header_label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        header.addWidget(self.header_label)

        iconBox = QGridLayout()
        iconBox_wid1 = Box("red")
        button_row1 = QHBoxLayout(iconBox_wid1)
        self.yearCombo = QComboBox()

        for i in range(2022, 2050):
            self.yearCombo.addItem(str(i))
            self.yearCombo.currentIndexChanged.connect(lambda: self.updateBalance())

        self.pdfBtn = QPushButton("Deleted Entries")
        self.pdfBtn.clicked.connect(self.modeSwitch)

        button_row1.addWidget(self.yearCombo)
        button_row1.addWidget(self.pdfBtn)
        iconBox_wid1.setFixedHeight(50)
        iconBox.addWidget(iconBox_wid1, 0, 0)

        year = self.yearCombo.currentText()

        rowQuery = "SELECT COUNT(Date) FROM Changes WHERE " + \
                   " year(Date) = " + "'" + year + "'"

        sheet_box = Box("White")
        sheetV = QVBoxLayout(sheet_box)
        mycursor.execute(rowQuery)
        res = mycursor.fetchone()
        total_rows = res[0]
        sheet_box.setMaximumHeight(400)
        self.sheet = MyTable(total_rows, 7)
        col_headers = ["id", "Date", "Table Changed", "Item Name", "Change Type", "Old Value", "New Value"]
        sheetV.setSpacing(0)
        sheetV.setContentsMargins(0, 0, 0, 0)
        self.sheet.setHorizontalHeaderLabels(col_headers)
        self.sheet.setColumnWidth(0, 100)

        for i in range(total_rows):
            query = "SELECT id, Date, TableChanged, ItemName, ChangeType, OldVal, NewVal FROM Changes WHERE" + \
                    " year(Date) = " + "'" + year + "'"
            mycursor.execute(query)
            values = mycursor.fetchall()
            item = QTableWidgetItem(str(values[i][0]))
            item1 = QTableWidgetItem(str(values[i][1]))
            item2 = QTableWidgetItem(str(values[i][2]))
            item3 = QTableWidgetItem(str(values[i][3]))
            item4 = QTableWidgetItem(str(values[i][4]))
            item5 = QTableWidgetItem(str(values[i][5]))
            item6 = QTableWidgetItem(str(values[i][6]))

            self.sheet.setItem(i, 0, item)
            self.sheet.setItem(i, 1, item1)
            self.sheet.setItem(i, 2, item2)
            self.sheet.setItem(i, 3, item3)
            self.sheet.setItem(i, 4, item4)
            self.sheet.setItem(i, 5, item5)
            self.sheet.setItem(i, 6, item6)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        sheetV.addWidget(self.sheet)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(header)
        mainLayout.addLayout(iconBox)
        mainLayout.addWidget(sheet_box)

        widget = QWidget()
        widget.setLayout(mainLayout)
        self.setCentralWidget(widget)

    def updateBalance(self):
        self.sheet.clear()

        currentMode = self.pdfBtn.text()

        if currentMode == "Deleted Entries":
            self.header_label.setText("Deletd Entries")
            self.pdfBtn.setText("Changes")
            col_headers = ["id", "Date Deleted", "Old ID", "Date", "Expense Name", "Amount", "Notes"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            self.sheet.setColumnWidth(0, 100)

            year = self.yearCombo.currentText()
            rowQuery = "SELECT COUNT(*) FROM deletedEntries WHERE" + \
                       " year(Date) = " + "'" + year + "'"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                query = "Select id , dateDeleted, oldID, date, Item_Name, Amount, Notes From " \
                        "deletedEntries Where year(dateDeleted) = '" + year + "'"
                mycursor.execute(query)
                val = mycursor.fetchall()

                item0 = QTableWidgetItem(str(val[i][0]))
                item1 = QTableWidgetItem(str(val[i][1]))
                item2 = QTableWidgetItem(str(val[i][2]))
                item3 = QTableWidgetItem(str(val[i][3]))
                item4 = QTableWidgetItem(str(val[i][4]))
                item5 = QTableWidgetItem(str(val[i][5]))
                item6 = QTableWidgetItem(str(val[i][6]))

                self.sheet.setItem(i, 0, item0)
                self.sheet.setItem(i, 1, item1)
                self.sheet.setItem(i, 2, item2)
                self.sheet.setItem(i, 3, item3)
                self.sheet.setItem(i, 4, item4)
                self.sheet.setItem(i, 5, item5)
                self.sheet.setItem(i, 6, item6)

        else:
            year = self.yearCombo.currentText()


            rowQuery = "SELECT COUNT(Date) FROM Changes WHERE" + \
                       " year(Date) = " + "'" + year + "'"

            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            col_headers = ["id", "Date", "Table Changed", "Item Name", "Change Type", "Old Value", "New Value"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            horiz_header = self.sheet.horizontalHeader()
            self.sheet.setColumnWidth(0, 100)

            for i in range(total_rows):
                query = "SELECT id, Date, TableChanged, ItemName, ChangeType, OldVal, NewVal FROM Changes WHERE" + \
                        " year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                values = mycursor.fetchall()
                item = QTableWidgetItem(str(values[i][0]))
                item1 = QTableWidgetItem(str(values[i][1]))
                item2 = QTableWidgetItem(str(values[i][2]))
                item3 = QTableWidgetItem(str(values[i][3]))
                item4 = QTableWidgetItem(str(values[i][4]))
                item5 = QTableWidgetItem(str(values[i][5]))
                item6 = QTableWidgetItem(str(values[i][6]))

                self.sheet.setItem(i, 0, item)
                self.sheet.setItem(i, 1, item1)
                self.sheet.setItem(i, 2, item2)
                self.sheet.setItem(i, 3, item3)
                self.sheet.setItem(i, 4, item4)
                self.sheet.setItem(i, 5, item5)
                self.sheet.setItem(i, 6, item6)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

    def modeSwitch(self):
        self.sheet.clear()
        currentMode = self.pdfBtn.text()
        if currentMode == "Deleted Entries":
            self.header_label.setText("Deletd Entries")
            self.pdfBtn.setText("Changes")
            col_headers = ["id", "Date Deleted", "Old ID", "Date", "Expense Name", "Amount", "Notes"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            self.sheet.setColumnWidth(0, 100)

            year = self.yearCombo.currentText()
            rowQuery = "SELECT COUNT(*) FROM deletedEntries WHERE" + \
                       " year(Date) = " + "'" + year + "'"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                query = "Select id , dateDeleted, oldID, date, Item_Name, Amount, Notes From " \
                        "deletedEntries Where year(dateDeleted) = '" + year + "'"
                mycursor.execute(query)
                val = mycursor.fetchall()

                item0 = QTableWidgetItem(str(val[i][0]))
                item1 = QTableWidgetItem(str(val[i][1]))
                item2 = QTableWidgetItem(str(val[i][2]))
                item3 = QTableWidgetItem(str(val[i][3]))
                item4 = QTableWidgetItem(str(val[i][4]))
                item5 = QTableWidgetItem(str(val[i][5]))
                item6 = QTableWidgetItem(str(val[i][6]))

                self.sheet.setItem(i, 0, item0)
                self.sheet.setItem(i, 1, item1)
                self.sheet.setItem(i, 2, item2)
                self.sheet.setItem(i, 3, item3)
                self.sheet.setItem(i, 4, item4)
                self.sheet.setItem(i, 5, item5)
                self.sheet.setItem(i, 6, item6)

        else:
            self.header_label.setText("Changes")
            self.pdfBtn.setText("Deleted Entries")
            col_headers = ["id", "Date", "Table Changed", "Item Name", "Change Type", "Old Value", "New Value"]
            self.sheet.setHorizontalHeaderLabels(col_headers)
            self.sheet.setColumnWidth(0, 100)

            year = self.yearCombo.currentText()

            rowQuery = "SELECT COUNT(Date) FROM Changes WHERE " + \
                       " year(Date) = " + "'" + year + "'"
            mycursor.execute(rowQuery)
            res = mycursor.fetchone()
            total_rows = res[0]

            rowPosition = self.sheet.rowCount()
            rowsAdd = total_rows - rowPosition
            if rowPosition < total_rows:
                for i in range(rowsAdd):
                    self.sheet.insertRow(rowPosition)
                    rowPosition += 1

            for i in range(total_rows):
                query = "SELECT id, Date, TableChanged, ItemName, ChangeType, OldVal, NewVal FROM Changes WHERE" + \
                        " year(Date) = " + "'" + year + "'"
                mycursor.execute(query)
                values = mycursor.fetchall()
                item = QTableWidgetItem(str(values[i][0]))
                item1 = QTableWidgetItem(str(values[i][1]))
                item2 = QTableWidgetItem(str(values[i][2]))
                item3 = QTableWidgetItem(str(values[i][3]))
                item4 = QTableWidgetItem(str(values[i][4]))
                item5 = QTableWidgetItem(str(values[i][5]))
                item6 = QTableWidgetItem(str(values[i][6]))

                self.sheet.setItem(i, 0, item)
                self.sheet.setItem(i, 1, item1)
                self.sheet.setItem(i, 2, item2)
                self.sheet.setItem(i, 3, item3)
                self.sheet.setItem(i, 4, item4)
                self.sheet.setItem(i, 5, item5)
                self.sheet.setItem(i, 6, item6)

        self.sheet.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)










app = QApplication(sys.argv)
window = BalanceSheet()
window.show()

app.exec()

def _append_run_path():
    if getattr(sys, "frozen", false):
        pathList = []

        pathList.append(sys._MEIPASS)

        _main_app_path = os.path.dirname(sys.executable)

        os.environ["PATH"] += os.pathsep + os.pathsep.join(pathList)

    logging.error("current PATH: %s", os.environ["PATH"])

_append_run_path()
