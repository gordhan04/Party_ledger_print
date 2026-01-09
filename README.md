Ledger Search & Print Tool
A simple, efficient desktop application designed to search, view, and print Tally ledger details directly from a JSON export. This tool automatically formats ledger information—including Party Name, Mailing Details, Address, State, and GSTIN—into a professional A4 PDF ready for printing.

Created by Vibe Coding with the help of Google Gemini.

🚀 Features
Instant Search: Quickly filter through thousands of ledgers using the search bar.

Auto-Encoding Detection: Seamlessly loads Tally JSON exports (supports both UTF-16 and UTF-8 encoding).

One-Click PDF Generation: Instantly generates an A4 PDF for the selected ledger.

Professional Formatting:

Centered Layout: Party Name and Mailing Details are center-aligned for a professional look.

Smart Address Formatting: Automatically splits long addresses into new lines based on commas.

Sender Footer: Includes a fixed "From" section with company details at the bottom left.

Cross-Platform: Works on Windows, macOS, and Linux (requires Python).

🛠️ Prerequisites
Before running the tool, ensure you have the following installed:

Python (3.6 or higher)

ReportLab Library (for PDF generation)

To install the required library, open your terminal or command prompt and run:

Bash

pip install reportlab
📂 How to Use
Prepare your Data: Ensure you have your Tally export file ready (e.g., Master.json).

Run the Tool:

Bash

python ledger_tool.py
Load File:

The tool looks for Master.json in the same folder automatically.

If not found, click "Load JSON File" and select your file manually.

Search & Print:

Type a name in the search box to find a ledger.

Select the ledger from the list.

Click the green "PRINT LEDGER (A4 PDF)" button.

View Output: The PDF will be saved in the same folder and will attempt to open automatically.

📝 Configuration (Sender Details)
The footer "From" details are currently hardcoded in the script. To change them:

Open ledger_tool.py in any text editor (Notepad, VS Code, etc.).

Scroll to the bottom of the print_ledger function (around line 190).

Modify the strings inside the c.drawString() functions:

Python

c.drawString(50, y, "From, YOUR COMPANY NAME")
c.drawString(50, y, "Your Address Line 1")
# ... update remaining lines as needed
📄 License
This project is open-source and free to use.

Developed with ❤️ by Vibe Coding & Google Gemini