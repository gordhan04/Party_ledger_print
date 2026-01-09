import json
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

class LedgerTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Ledger Print Tool by Govardhan Raj")
        self.root.geometry("600x600")

        self.ledgers = []
        self.filtered_ledgers = []
        self.raw_data = {} # To store full JSON structure for saving

        # UI Layout
        self.setup_ui()
        
        # Load Data automatically if file exists
        self.file_path = "Master.json"
        if os.path.exists(self.file_path):
            self.load_data(self.file_path)
        else:
            self.load_file_dialog()

    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, pady=10)
        header_frame.pack(fill="x")
        tk.Label(header_frame, text="Ledger Printing Tool by Govardhan Raj", font=("Arial", 16, "bold")).pack()
        
        btn_frame = tk.Frame(header_frame)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Load JSON File", command=self.load_file_dialog, bg="#e1e1e1").pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ Create New Ledger", command=self.open_create_ledger_window, bg="#2196F3", fg="white").pack(side="left", padx=5)

        # Search Bar
        search_frame = tk.Frame(self.root, pady=5, padx=10)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Search Ledger:", font=("Arial", 10)).pack(anchor="w")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Arial", 12))
        self.search_entry.pack(fill="x", pady=5)
        
        # Key Bindings for Navigation
        self.search_entry.bind("<Down>", self.focus_listbox)
        self.search_entry.bind("<Return>", self.print_ledger)

        # Listbox
        list_frame = tk.Frame(self.root, padx=10, pady=5)
        list_frame.pack(fill="both", expand=True)
        
        self.ledger_listbox = tk.Listbox(list_frame, font=("Arial", 11), height=15)
        self.ledger_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.ledger_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.ledger_listbox.config(yscrollcommand=scrollbar.set)
        
        # Listbox Bindings
        self.ledger_listbox.bind("<Return>", self.print_ledger)

        # Print Button
        btn_frame = tk.Frame(self.root, pady=15)
        btn_frame.pack(fill="x")
        tk.Button(btn_frame, text="PRINT LEDGER (Enter)", command=self.print_ledger, 
                  bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), height=2).pack(fill="x", padx=20)

    def focus_listbox(self, event):
        self.ledger_listbox.focus_set()
        if self.ledger_listbox.size() > 0:
            self.ledger_listbox.selection_clear(0, tk.END)
            self.ledger_listbox.selection_set(0)

    def load_file_dialog(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            self.file_path = file_path
            self.load_data(file_path)

    def load_data(self, path):
        data = None
        # Try UTF-16 (Tally default) then UTF-8
        try:
            with open(path, 'r', encoding='utf-16') as f:
                data = json.load(f)
        except (UnicodeError, json.JSONDecodeError):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file encoding: {e}")
                return

        if data:
            self.raw_data = data # Store raw data for saving later
            self.process_json_data(data)

    def process_json_data(self, data):
        try:
            self.ledgers = []
            if "tallymessage" in data:
                for item in data["tallymessage"]:
                    if "metadata" in item and item["metadata"].get("type") == "Ledger":
                        ledger_obj = item
                        name = item["metadata"].get("name", "Unknown")
                        self.ledgers.append({
                            "name": name,
                            "data": ledger_obj
                        })
            
            self.ledgers.sort(key=lambda x: x["name"])
            self.update_list()
            # No message box here to avoid annoyance on restart
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse JSON structure: {e}")

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.ledger_listbox.delete(0, tk.END)
        self.filtered_ledgers = []

        for l in self.ledgers:
            if search_term in l["name"].lower():
                self.filtered_ledgers.append(l)
                self.ledger_listbox.insert(tk.END, l["name"])
        
        # Auto-select first item if search matches
        if self.filtered_ledgers:
            self.ledger_listbox.selection_set(0)

    def get_ledger_details(self, ledger_data):
        details = {}
        details['name'] = ledger_data.get('metadata', {}).get('name', '')
        details['gstin'] = "N/A"
        details['address'] = ""
        details['state'] = "N/A"
        details['mobile'] = ledger_data.get('ledgermobile', 'N/A')
        
        # Extract Address & State
        if 'ledmailingdetails' in ledger_data:
            mail_info = ledger_data['ledmailingdetails']
            if isinstance(mail_info, list) and len(mail_info) > 0:
                addr_list = mail_info[0].get('address', [])
                clean_addr = [x for x in addr_list if isinstance(x, str)]
                details['address'] = ", ".join(clean_addr)
                details['state'] = mail_info[0].get('state', 'N/A')
        
        if 'ledgstregdetails' in ledger_data:
            gst_info = ledger_data['ledgstregdetails']
            if isinstance(gst_info, list) and len(gst_info) > 0:
                details['gstin'] = gst_info[0].get('gstin', 'N/A')
        
        return details

    # --- CREATE NEW LEDGER FUNCTIONALITY ---
    def open_create_ledger_window(self):
        top = tk.Toplevel(self.root)
        top.title("Create New Ledger")
        top.geometry("400x450")
        
        tk.Label(top, text="Party Name:").pack(pady=2)
        entry_name = tk.Entry(top, width=40)
        entry_name.pack(pady=2)

        tk.Label(top, text="Address (comma for new line):").pack(pady=2)
        entry_address = tk.Entry(top, width=40)
        entry_address.pack(pady=2)

        tk.Label(top, text="State:").pack(pady=2)
        entry_state = tk.Entry(top, width=40)
        entry_state.pack(pady=2)

        tk.Label(top, text="GSTIN:").pack(pady=2)
        entry_gst = tk.Entry(top, width=40)
        entry_gst.pack(pady=2)

        tk.Label(top, text="Mobile:").pack(pady=2)
        entry_mobile = tk.Entry(top, width=40)
        entry_mobile.pack(pady=2)

        def save_new():
            name = entry_name.get()
            if not name:
                messagebox.showwarning("Error", "Name is required")
                return
            
            # Construct JSON Object compatible with existing Tally logic
            address_parts = entry_address.get().split(',')
            
            new_ledger = {
                "metadata": { "type": "Ledger", "name": name },
                "ledgermobile": entry_mobile.get(),
                "ledmailingdetails": [{
                    "address": address_parts,
                    "state": entry_state.get()
                }],
                "ledgstregdetails": [{
                    "gstin": entry_gst.get()
                }]
            }

            # Update Internal Data
            if "tallymessage" not in self.raw_data:
                self.raw_data["tallymessage"] = []
                
            self.raw_data["tallymessage"].append(new_ledger)
            
            # Save to File
            try:
                # Save as UTF-8 so Python reads it easily next time
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.raw_data, f, indent=4)
                
                # Reload UI
                self.process_json_data(self.raw_data)
                messagebox.showinfo("Success", "New Ledger Saved!")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

        tk.Button(top, text="SAVE LEDGER", command=save_new, bg="#2196F3", fg="white").pack(pady=20)

    # --- PRINTING FUNCTIONALITY ---
    def print_ledger(self, event=None):
        selection = self.ledger_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Ledger", "Please select a ledger to print.")
            return

        # 1. Ask for Packing Note Number
        note_number = simpledialog.askstring("Input", "Enter Packing Note Number:")
        if note_number is None: return # User cancelled
        packing_note_text = f"Packing Note: {note_number}"

        index = selection[0]
        selected_item = self.filtered_ledgers[index]
        details = self.get_ledger_details(selected_item['data'])

        # PDF Setup
        pdf_file = f"{details['name']}_Ledger.pdf".replace("/", "_").replace("\\", "_")
        c = canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4
        
        # ================== CENTERED SECTION ==================
        
        # 1. Packing Note (Center, Size 18) - Updated with User Input
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 50, packing_note_text)
        
        # Divider Line
        c.setLineWidth(1)
        c.line(50, height - 65, width - 50, height - 65)

        y = height - 100

        # 2. Party Name (Center, Size 18)
        c.setFont("Helvetica-Bold", 25)
        c.drawCentredString(width / 2, y, details['name'])
        y -= 30 

        # 3. Address (Center, Split by comma)
        c.setFont("Helvetica-Bold", 18)
        
        raw_address = details['address']
        if raw_address:
            address_lines = [line.strip() for line in raw_address.split(',')]
            for line in address_lines:
                if line:
                    c.drawCentredString(width / 2, y, line)
                    y -= 20
        
        y -= 10
        
        # State, GSTIN, Mobile (Center)
        c.drawCentredString(width / 2, y, f"State: {details['state']}")
        y -= 20
        c.drawCentredString(width / 2, y, f"GSTIN: {details['gstin']}")
        y -= 20
        if details['mobile'] and details['mobile'] != 'N/A':
             c.drawCentredString(width / 2, y, f"Mobile: {details['mobile']}")
             y -= 20

        # ================== LEFT ALIGNED SECTION ==================
        
        y -= 15 # Add spacing before the Sender Details
        
        # Draw Divider Line
        c.setLineWidth(0.5)
        c.line(50, y+10, width - 50, y+10)
        y -= 5
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "From,  MADHUR MILAN SILK")
        y -= 20
        
        c.setFont("Helvetica", 12)
        c.drawString(50, y, "No.29/1, 2nd floor,Sri Balaji Complex,")
        y -= 15
        c.drawString(50, y, "Appaji rao lane,S.D.D. Road Cross,")
        y -= 15
        c.drawString(50, y, "BENGALURU-560002")
        y -= 25
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "GSTIN:- 29AGJPR1392P1ZH   PH: 080-41144941")

        c.save()
        messagebox.showinfo("Printed", f"PDF saved as: {pdf_file}")
        try:
            os.startfile(pdf_file)
        except:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = LedgerTool(root)
    root.mainloop()