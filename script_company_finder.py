from PyQt6.QtWidgets import  QDialog, QDialogButtonBox,  QPushButton,  QTableWidget, QTableWidgetItem, QHeaderView, QVBoxLayout, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import QFont
import sqlite3
import pandas as pd
import pdb
import requests
class Companies(QDialog):
    def __init__(self, initial_settings, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        row1_layout = QHBoxLayout()
        row2_layout = QHBoxLayout()
        # Create table
        self.companies_Table = QTableWidget(self)
        self.companies_Table.setRowCount(15)
        self.companies_Table.setColumnCount(2)
        self.companies_Table.cellDoubleClicked.connect(self.on_company_selected)
        #self.companies_Table.cellDoubleClicked.connect(lambda row, col: self.on_company_selected(row, col))
        self.companies_Table.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.companies_Table.setStyleSheet("QHeaderView::section{background-color: #f0f0f0;}")
        self.companies_Table.verticalHeader().setVisible(True)
        
        row_height = 30
        self.companies_Table.verticalHeader().setDefaultSectionSize(row_height)

        headers = ["Comapny Code", "Name"]
        font = QFont("Arial", 12)

        self.companies_Table.setHorizontalHeaderLabels(headers)
        self.companies_Table.setFixedWidth(548)
        self.companies_Table.setFixedHeight(400)
        self.companies_Table.setColumnWidth(0, int(0.25 * 500))
        self.companies_Table.setColumnWidth(1, int(0.75 * 500))

        self.layout.addWidget(self.companies_Table)

        # Fetch companies from Flask app API
        self.fetch_companies()
        
        #conn = sqlite3.connect('accountingdb.db')
        #cursor = conn.execute("SELECT * from companies")
        #records = cursor.fetchall()
        #df = pd.DataFrame(records)
        #for ind in df.index:
        #    v =  df[0][ind]

        #    it = QTableWidgetItem(v)
        #    self.companies_Table.setItem(ind, 0, it)

        #    vv =  df[1][ind]
        #    it = QTableWidgetItem(vv)
        #    self.companies_Table.setItem(ind, 1, it)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)
        
    # Fetch the companies list from the Flask API
    def fetch_companies(self):
        #pdb.set_trace() 
        try:
            response = requests.get('http://localhost:5000/get-companies')
            if response.status_code == 200:
                companies = response.json()
                self.populate_table(companies)
            else:
                print(f"Failed to fetch companies: {response.status_code}")
        except Exception as e:
            print(f"Error fetching companies: {str(e)}")

    # Populate the table with the fetched companies
    def populate_table(self, companies):
        self.companies_Table.setRowCount(len(companies))
        for row, company in enumerate(companies):
            company_code = company["company_code"]
            company_name = company["company_name"]

            code_item = QTableWidgetItem(company_code)
            name_item = QTableWidgetItem(company_name)

            self.companies_Table.setItem(row, 0, code_item)
            self.companies_Table.setItem(row, 1, name_item)


    def on_company_selected(self, row, column):
        print(f"Double-clicked on row {row}, column {column}")  # Debugging print
    
        company_code = self.companies_Table.item(row, 0).text()  # Get the company code
        company_name = self.companies_Table.item(row, 1).text()  # Get the company name

        print(f"Selected Company Code: {company_code}, Name: {company_name}")

        # Store the selected company details
        self.selected_company = (company_code)

        # Optionally, close the dialog
        self.accept()
    def get_selected_company(self):
        return getattr(self, 'selected_company', None)
