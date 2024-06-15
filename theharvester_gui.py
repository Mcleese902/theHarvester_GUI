import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, 
                             QTextEdit, QVBoxLayout, QWidget, QLabel, QComboBox, QAction, QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os

class WorkerThread(QThread):
    update_progress = pyqtSignal(int)
    update_output = pyqtSignal(str)
    update_error = pyqtSignal(str)

    def __init__(self, command_args):
        super().__init__()
        self.command_args = command_args

    def run(self):
        try:
            process = subprocess.Popen(self.command_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.update_output.emit(output.strip())
                    self.update_progress.emit(50)  # Update progress as an example
            stderr = process.stderr.read()
            if stderr:
                self.update_error.emit(stderr.strip())
            self.update_progress.emit(100)  # Update progress to 100% when done
        except Exception as e:
            self.update_error.emit(str(e))


class TheHarvesterGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('theHarvester GUI')
        self.setGeometry(100, 100, 800, 600)

        self.initUI()
        self.create_menu()
        self.apply_styles()

    def initUI(self):
        main_layout = QVBoxLayout()

        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignTop)

        self.domain_label = QLabel("Enter Domain:")
        form_layout.addWidget(self.domain_label)

        self.domain_input = QLineEdit()
        form_layout.addWidget(self.domain_input)

        self.source_label = QLabel("Select Source:")
        form_layout.addWidget(self.source_label)

        self.source_combo = QComboBox()
        self.source_combo.addItems(["all", "baidu", "bing", "bingapi", "certspotter", "crtsh", "dogpile",
                                    "duckduckgo", "exalead", "github-code", "google", "hunter", "intelx",
                                    "linkedin", "linkedin_links", "netcraft", "otx", "pentesttools", "rapiddns",
                                    "securityTrails", "spyse", "threatcrowd", "trello", "twitter", "urlscan", "virustotal",
                                    "yahoo"])
        form_layout.addWidget(self.source_combo)

        self.command_label = QLabel("Select Command:")
        form_layout.addWidget(self.command_label)

        self.command_combo = QComboBox()
        self.command_combo.addItems([
            "-d <domain> -b all",  # Basic search with all sources
            "-d <domain> -l 500 -b all",  # Limit results to 500
            "-d <domain> -f <filename> -b all",  # Save output to XML and HTML
            "-d <domain> --dns-server 8.8.8.8 -b all",  # Use specific DNS server
            "-d <domain> -v -b all",  # Verbose output
            "-d <domain> -h -b all",  # Display help message
            "-d <domain> -c -b all",  # Perform a virtual host lookup
            "-d <domain> -e -b all",  # Perform a DNS brute force
            "-d <domain> -t 60 -b all",  # Set a search timeout
            "-d <domain> -l 500 -b google -f <filename>",  # Search google and save output
            "-d <domain> -b bing --dns-server 8.8.8.8 -v",  # Search bing with specific DNS and verbose output
            "-d <domain> -b google -e",  # Search google and perform DNS brute force
            "-d <domain> -b linkedin -t 60",  # Search linkedin with timeout
            "-d <domain> -b google -c",  # Search google and perform virtual host lookup
            "-d <domain> -b google -e -f <filename>",  # Search google, DNS brute force, and save output
            "-d <domain> -b bing --dns-server 8.8.8.8 -v -l 100",  # Search bing with DNS server, verbose, and limit results
            "-d <domain> -b all -f <filename> -t 120",  # Search all sources, save output, and set timeout
            "-d <domain> -b google -c -v"  # Search google, perform virtual host lookup, and verbose output
        ])
        form_layout.addWidget(self.command_combo)

        self.run_button = QPushButton('Run theHarvester')
        self.run_button.clicked.connect(self.run_theharvester)
        form_layout.addWidget(self.run_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        form_layout.addWidget(self.progress_bar)

        main_layout.addLayout(form_layout)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        main_layout.addWidget(self.output_text)

        self.footer = QLabel("Black Diamond Utilities © 2024")
        self.footer.setObjectName("footer")
        self.footer.setAlignment(Qt.AlignCenter)

        footer_layout = QVBoxLayout()
        footer_layout.addWidget(self.footer)

        main_layout.addLayout(footer_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def create_menu(self):
        menubar = self.menuBar()

        help_menu = menubar.addMenu('Help')

        how_to_action = QAction('How to Use', self)
        how_to_action.triggered.connect(self.show_how_to)
        help_menu.addAction(how_to_action)

    def show_how_to(self):
        how_to_text = """
        How to Use theHarvester GUI:

        1. Enter the Domain:
           - Input the domain you want to scan in the "Enter Domain" field.

        2. Select Source:
           - Choose the source(s) you want to use from the "Select Source" dropdown.

        3. Select Command:
           - Pick an advanced command from the "Select Command" dropdown menu.

        4. Run theHarvester:
           - Click the "Run theHarvester" button to execute the command.

        5. View Results:
           - The results of the command will be displayed in the text area below.

        Common Commands:
        - -d <domain> -b all : Perform a basic search with all sources.
        - -d <domain> -l 500 -b all : Limit the results to 500.
        - -d <domain> -f <filename> -b all : Save the output to XML and HTML formats.
        - -d <domain> --dns-server 8.8.8.8 -b all : Use a specific DNS server for the search.
        - -d <domain> -v -b all : Enable verbose output.
        - -d <domain> -h -b all : Display help message.
        - -d <domain> -c -b all : Perform a virtual host lookup.
        - -d <domain> -e -b all : Perform a DNS brute force.
        - -d <domain> -t 60 -b all : Set a search timeout to 60 seconds.

        For more detailed information, please refer to the official theHarvester documentation.
        """
        QMessageBox.information(self, "How to Use", how_to_text)

    def run_theharvester(self):
        domain = self.domain_input.text()
        source = self.source_combo.currentText()
        command_template = self.command_combo.currentText()
        command = command_template.replace("<domain>", domain).replace("<filename>", "output")  # Replace placeholders

        command_parts = command.split()  # Split the command into parts for subprocess

        harvester_path = os.path.expanduser('~/Desktop/theHarvester_gui/theHarvester/theHarvester.py')

        # Debugging: Print the current working directory and script path
        print(f"Current working directory: {os.getcwd()}")
        print(f"Expected theHarvester script path: {harvester_path}")

        try:
            if os.path.exists(harvester_path):
                # Ensure the script is executable
                if not os.access(harvester_path, os.X_OK):
                    self.output_text.setText(f"Error: theHarvester script at {harvester_path} is not executable.")
                    return

                # Build the command based on user input
                command_args = ['python3', harvester_path]
                command_args.extend(command_parts)

                print(f"Running command: {' '.join(command_args)}")  # Debugging output

                self.worker_thread = WorkerThread(command_args)
                self.worker_thread.update_progress.connect(self.update_progress)
                self.worker_thread.update_output.connect(self.update_output)
                self.worker_thread.update_error.connect(self.update_error)
                self.worker_thread.start()

            else:
                self.output_text.setText(f"Error: theHarvester script not found at the specified path: {harvester_path}")
        except Exception as e:
            self.output_text.setText(f"Error: {e}")

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_output(self, text):
        self.output_text.append(text)

    def update_error(self, text):
        self.output_text.append(f"Error: {text}")

    def apply_styles(self):
        style = """
        /* QSS Stylesheet for TailwindCSS-like Styling */

        QWidget {
            background-color: #1a1a1a; /* Dark background */
            color: #e5e7eb; /* Light text */
            font-family: 'Arial', sans-serif;
        }

        QLabel {
            color: #a3a3a3; /* Light grey text for labels */
            font-size: 14px;
            margin-bottom: 8px;
        }

        QLineEdit, QComboBox, QTextEdit {
            background-color: #2d2d2d; /* Slightly lighter background */
            border: 1px solid #4b5563; /* Grey border */
            border-radius: 5px;
            padding: 8px;
            color: #e5e7eb;
        }

        QPushButton {
            background-color: #6b21a8; /* Purple button */
            color: #e5e7eb;
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
            margin-top: 10px;
        }

        QPushButton:hover {
            background-color: #9d4edd; /* Lighter purple on hover */
        }

        QPushButton:pressed {
            background-color: #4b5563; /* Darker grey on press */
        }

        #footer {
            background-color: #111827; /* Very dark background */
            color: #9ca3af; /* Grey text */
            padding: 10px;
            text-align: center;
            font-size: 12px;
            border-top: 1px solid #374151; /* Top border */
        }
        """
        self.setStyleSheet(style)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TheHarvesterGUI()
    window.show()
    sys.exit(app.exec_())

