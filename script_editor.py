import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSplitter, QTextEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QLabel, QLineEdit, 
    QSpacerItem, QSizePolicy, QDialog, QTableWidget, QTableWidgetItem
)

from script_company_finder import Companies
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from functools import partial
import pdb
import requests
import json
import datetime

class ScriptInterpreter:
    
    def __init__(self, script, preview_container):
        self.script = script
        self.preview_container = preview_container
        self.widget_registry = {} # Store references to widgets by name
        self.commands = []  # Store commands to be executed

    def interpret(self):
        # Clear previous widgets
        layout = self.preview_container.layout()
        if layout:
            for i in reversed(range(layout.count())):
                widget_to_remove = layout.itemAt(i).widget()
                if widget_to_remove is not None:
                    widget_to_remove.setParent(None)

        
        end_horizontal_found = True
        in_command_block = False
        in_function_block = False
        
        # Parse the script line by line
        lines = self.script.splitlines()
        for line in lines:
            
            line = line.strip()
           

            
            
            if line.startswith("Buttons") and end_horizontal_found == True:
                self._create_button(line)
            elif line.startswith("Horizontal:"):
                # Start a new horizontal layout
                horizontal_layout = QHBoxLayout()
                #horizontal_layout.setSpacing(10)
                self._add_hbox_layout_to_container(horizontal_layout)
                end_horizontal_found = False
            
                
                
            
                
            elif line.startswith("Buttons") and end_horizontal_found == False:
                self._create_button(line)
                
            elif line.startswith("Label") and end_horizontal_found == False:
                self._create_label(line, horizontal_layout)
               
            elif line.startswith("TextInput") and end_horizontal_found == False:
                self._create_text_input(line, horizontal_layout)
                
                
            
                
            elif line.startswith("Label") and end_horizontal_found == True:
                    self._create_label(line)
                    
            elif line.startswith("TextInput") and end_horizontal_found == True:
                    self._create_text_input(line)
                    
            elif line.startswith("End Horizontal"):
                end_horizontal_found = True
            # Check for Command blocks
            elif line.startswith("Command:"):
                #pdb.set_trace() 
                in_command_block = True
                continue
            
            elif line.startswith("End Command"):
                in_command_block = False
                self._apply_commands()
                continue
            elif in_command_block == True :
                self._parse_command(line)
                
                continue
            # Check for Function blocks
            elif line.startswith("Function:"):
                #pdb.set_trace() 
                in_function_block = True
                continue
            
            elif line.startswith("End Function"):
                in_function_block = False
                
                continue
            elif in_function_block == True :
                self._parse_function(line)
                
                continue
            elif line.startswith("Table("):
                # Extract table name and option (showdata | showstructure)
                table_spec = line[len("Table("):-1]  # Remove "Table(" prefix and ")" suffix
                table_name, option = table_spec.split(",", 1)
                table_name = table_name.strip()
                option = option.strip()

                if option == "showdata":
                    self.show_table_data(table_name)
                elif option == "showstructure":
                    self.show_table_structure(table_name)
                else:
                    print("Invalid option specified. Use showdata or showstructure.")
            

        

        # Add spacer to push everything to the top
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        layout.addItem(spacer)

    def Show_Current_Date(self, target_label):
        target_widget = self.widget_registry.get(target_label)
        if isinstance(target_widget, QLabel):
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            target_widget.setText(current_date)

    def show_table_data(self, table_name):
        try:
            response = requests.get(f'http://localhost:5000/get-table-data/{table_name}')
            if response.status_code == 200:
                result = response.json()
                columns = result['columns']
                records = result['data']

                # Display the table data
                self.display_table(records, columns)
            else:
                print(f"Error fetching table data: {response.status_code}")
        except Exception as e:
            print(f"Error: {str(e)}")

    def display_table(self, data, headers):
        """
        Display data in the right pane using a QTableWidget
        """
        

        table_widget = QTableWidget()
        table_widget.setRowCount(len(data))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)

        # Add data to the table
        for row_index, row_data in enumerate(data):
            for col_index, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                table_widget.setItem(row_index, col_index, item)

        # Add the table widget to the right pane
        self.preview_container.layout().addWidget(table_widget)
        
    def show_table_structure(self, table_name):
    
        try:
            # Make a request to fetch table structure from the Flask app
            response = requests.get(f"http://localhost:5000/get-table-structure/{table_name}")
            if response.status_code == 200:
                data = response.json()
                
                columns = data['columns']  # Extract column headers
                structure = data['structure']  # Extract structure data
                #pdb.set_trace() 
                # Set up the QTableWidget to display the table structure
                self.table_widget = QTableWidget()
                self.table_widget.setRowCount(len(structure))
                self.table_widget.setColumnCount(len(columns))
                self.table_widget.setHorizontalHeaderLabels(columns)

                # Populate the table widget with the structure data
                for row_idx, row_data in enumerate(structure):
                    for col_idx, column_name in enumerate(columns):
                        value = str(row_data.get(column_name, ''))
                        self.table_widget.setItem(row_idx, col_idx, QTableWidgetItem(value))
                self.preview_container.layout().addWidget(self.table_widget)
            else:
                print(f"Error fetching table structure: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    
    def _parse_command(self, line):
        """
        Parse commands from the Command block.
        """
        #pdb.set_trace()
        if line.startswith("Button_Clicked"):
            parts = line.split(':')
            
            button_name = parts[1]
            
            action = parts[2]
            target = parts[3]
            self.commands.append({
                "button_name": button_name,
                "action": action,
                "target": target
            })

    def _parse_function(self, line):
        """
        Parse function from the Command block.
        """
        # Strip any extra spaces
        line = line.strip()

        # Check if the line contains a function call with parentheses
        if line.startswith("Show_Current_Date"):
            # Extract the argument inside the parentheses
            if "(" in line and ")" in line:
                start = line.index("(") + 1
                end = line.index(")")
                argument = line[start:end].strip()

                # Check if the argument is a valid widget name
                if argument in self.widget_registry:
                    
                    # Call the Show_Current_Date method and pass the QLabel
                    self.Show_Current_Date(argument)
                    
                else:
                    print(f"Error: No widget found with the name {argument}.")
        

    def _apply_commands(self):
        #pdb.set_trace()
        """
        Apply the parsed commands to the corresponding widgets.
        """
        for command in self.commands:
            button_name = command["button_name"]
            action = command["action"]
            target = command["target"]
            
            action = action.strip()
            button_name= button_name.strip()
            target = target.strip()
            
        
            # Retrieve the button from the registry
            button = self.widget_registry.get(button_name.strip())
            
        
            if button is not None:
                # Use lambda to capture the action argument properly
                #button.clicked.connect(lambda _, a=action: self._execute_action(a))
                button.clicked.connect(partial(self._execute_action, action, target))

    def _execute_action(self, action, target):
        #pdb.set_trace()
        """
        Execute the action when the button is clicked.
        """
        if action.startswith("print"):
            # Extract the target of the print command
            
            _, target_widget = action.split(maxsplit=1)
            
            widget = self.widget_registry.get(target_widget)
            
            if isinstance(widget, QLineEdit):
                # Print the content of the text input
                print(widget.text())
                if target:
                    widget1 = self.widget_registry.get(target)
                    if isinstance(widget1, QLabel):
                        widget1.setText(widget.text())

    def _create_button(self, line, layout=None):
        _, label = line.split(maxsplit=1)
        button = QPushButton(label)
        button.setFixedHeight(30)  # Set fixed height
        button_name = label.strip()
        self.widget_registry[button_name] = button  # Register button by name
        if layout != None:
            layout.addWidget(button)
        else:
            self.preview_container.layout().addWidget(button)

    def _create_label(self, line, layout=None):
        # Extract label information and alignment
        label_parts = line.split("(")
        label_name = label_parts[0].split()[1].strip()  # Label name (like Label1)
    
        if len(label_parts) > 1:
            text_and_align = label_parts[1].rstrip(")").split(":")
            label_text = text_and_align[0].strip()  # Label text (like "Result")
            alignment = text_and_align[1].strip().lower() if len(text_and_align) > 1 else 'left'
        else:
            label_text = ""
            alignment = 'left'
    
        label = QLabel(label_text)
        label.setFixedHeight(30)  # Set fixed height
        
        # Register the text input by its name
        self.widget_registry[label_name] = label

        # Set alignment based on the provided value (left, center, right)
        if alignment == 'center':
            label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        elif alignment == 'right':
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        else:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        if layout != None:
            layout.addWidget(label)
        else:
            self.preview_container.layout().addWidget(label)

    def _create_text_input(self, line, layout=None):
        
        # Extract the name and placeholder from the line
        name_placeholder = line[len("TextInput "):]  # Remove "TextInput " part
        parts = name_placeholder.split("(", 1)
        
        self.name = parts[0].strip()
        placeholder_and_comp = parts[1].rstrip(")")  # Remove closing parenthesis
    
        # Check if 'COMP' is specified
        if ',' in placeholder_and_comp:
            
            comp_option, placeholder  = placeholder_and_comp.split(",", 1)
            
            comp_option = comp_option.strip()
            
        else:
            self.name = parts[0].strip()
            placeholder = parts[1].strip()
            comp_option = None
    
        
    
        # Create the text input widget
        text_input = QLineEdit()
        text_input.setPlaceholderText(placeholder)
        text_input.setFixedHeight(30)  # Set fixed height

        # Register the text input by its name
        self.widget_registry[self.name] = text_input
    
        # Create a horizontal layout for the TextInput and Button
        text_input_layout = QHBoxLayout()
        text_input_layout.addWidget(text_input)
    
        # If 'COMP' is specified, add a button next to the text input
        if comp_option == "COMP":
            comp_button = QPushButton()
            comp_button.setFixedSize(30, 30)
        
            # Set the font for the inverted arrow (e.g., using a unicode character)
            font = QFont('Arial Black')
            font.setPointSize(12)  # Set appropriate font size
            comp_button.setFont(font)
            comp_button.setText("...")  # Inverted arrow character
            comp_button.clicked.connect(self.open_companies_dialog)

            # Add the button to the horizontal layout next to the text input
            text_input_layout.addWidget(comp_button)
    
        # Add the horizontal layout (with TextInput and optional button) to the main layout
        if layout is not None:
            layout.addLayout(text_input_layout)
        else:
            self.preview_container.layout().addLayout(text_input_layout)
    def open_companies_dialog(self):
        # Open the Companies dialog (from the company_finder.py file)
        initial_settings = {}  # You can pass any necessary settings here
        dialog = Companies(initial_settings)
    
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Handle what happens when the dialog is accepted (OK)
            selected_company = dialog.companies_Table.currentItem().text()
            print(f"Selected company: {selected_company}")
            widget = self.widget_registry.get(self.name)
            if isinstance(widget, QLineEdit):
                widget.setText(selected_company)
    def _add_hbox_layout_to_container(self, layout):
        # Create a container widget for the HBoxLayout
        hbox_widget = QWidget()
        hbox_widget.setLayout(layout)
        #hbox_widget.setFixedHeight(50)  # Set a fixed height for the HBoxLayout widget
        self.preview_container.layout().addWidget(hbox_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Custom Scripting Language Interpreter")
        self.setGeometry(100, 100, 800, 600)

        # Create a QSplitter to split left and right sections
        self.splitter = QSplitter(Qt.Orientation.Horizontal, self)

        # Left Pane: TextEdit for entering script and a button to test it
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        hbox_buttons = QHBoxLayout()

        # Load script button
        self.load_button = QPushButton("Load Script")
        self.load_button.clicked.connect(self.load_script_from_server)

        # Save script button (NEW)
        self.save_button = QPushButton("Save Script")
        self.save_button.clicked.connect(self.save_script_to_server)
        

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter your script here...")

        self.test_button = QPushButton("Test Script")
        self.test_button.clicked.connect(self.run_script)
        
        hbox_buttons.addWidget(self.load_button)
        hbox_buttons.addWidget(self.save_button)
        self.left_layout.addLayout(hbox_buttons)
        self.left_layout.addWidget(self.text_edit)
        self.left_layout.addWidget(self.test_button)

        # Right Pane: ScrollArea to preview the widgets from the script
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.preview_container = QWidget()
        self.preview_container.setLayout(QVBoxLayout())
        self.scroll_area.setWidget(self.preview_container)

        # Add left and right panes to the splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.scroll_area)
        splitter_sizes = [int(0.30 * self.width()), int(0.70 * self.width())]
        self.splitter.setSizes(splitter_sizes)

        # Set splitter as the central widget of the main window
        self.setCentralWidget(self.splitter)
        
    def save_script_to_server(self):  # NEW
        url = "http://localhost:5000/save-script/test_script.scp"
        script_content = self.text_edit.toPlainText()

        try:
            # Send a POST request with the script content
            response = requests.post(url, json={"script": script_content})
            response.raise_for_status()

            print("Script saved successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error saving script: {e}")
            
    def load_script_from_server(self):
        # URL of the server endpoint
        url = "http://localhost:5000/get-script/test_script.scp"
        
        try:
            # Send request to fetch script content
            response = requests.get(url)
            response.raise_for_status()
            
            # Set the text editor content to the script content
            self.text_edit.setText(response.text)
        
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving script: {e}")

    def run_script(self):
        # Get the layout of the container inside the scroll area
        layout = self.preview_container.layout()
    
        # Remove all widgets from the layout
        while layout.count():
            item = layout.takeAt(0)  # Get the first item from the layout
            widget = item.widget()   # Get the widget from the layout item
            if widget is not None:
                widget.setParent(None)  # Remove the widget from the layout
        
        # Get the script from the text editor
        script = self.text_edit.toPlainText()
        

        # Interpret and render the widgets in the right pane
        interpreter = ScriptInterpreter(script, self.preview_container)
        interpreter.interpret()


# Main application
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()

# Run the PyQt6 event loop
sys.exit(app.exec())
