import json
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import customtkinter as ctk 
from PIL import Image, ImageTk 
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# --- CONFIGURATION ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class LedgerTool(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("Ledger Print Tool by G.A.Raj")
        self.geometry("700x750")
        
        if os.path.exists("logo.ico"):
            self.iconbitmap("logo.ico")

        # Data Storage
        self.ledgers = []
        self.filtered_ledgers = []
        self.raw_data = {} 
        self.file_path = "Master.json"

        # Layout Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Build UI
        self.setup_ui()
        
        # Load Data
        if os.path.exists(self.file_path):
            self.load_data(self.file_path)
        else:
            self.load_file_dialog()

        # --- FIX 1: Auto-Focus Search Bar on Startup ---
        # We use .after(200) to ensure the window is fully loaded before setting focus
        self.after(200, lambda: self.search_entry.focus_set())

    def setup_ui(self):
        # --- 1. HEADER & LOGO ---
        self.header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        if os.path.exists("logo.png"):
            img = Image.open("logo.png")
            self.logo_image = ctk.CTkImage(light_image=img, dark_image=img, size=(50, 50))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=self.logo_image, text="")
            self.logo_label.pack(side="left", padx=(0, 15))
        
        title_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_frame.pack(side="left")
        ctk.CTkLabel(title_frame, text="Ledger Address Print", font=("Roboto", 24, "bold")).pack(anchor="w")
        ctk.CTkLabel(title_frame, text="Devloped by Govardhan Raj ", font=("Roboto", 12), text_color="gray").pack(anchor="w")

        btn_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        ctk.CTkButton(btn_frame, text="Load JSON", command=self.load_file_dialog, 
                      width=100, fg_color="#607D8B", hover_color="#455A64").pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="+ Create New", command=self.open_create_ledger_window, 
                      width=100).pack(side="left", padx=5)

        # --- 2. SEARCH BAR ---
        self.search_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.search_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.update_list)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, textvariable=self.search_var, 
                                         placeholder_text="🔍 Search Ledger Name...", 
                                         height=40, font=("Roboto", 14))
        self.search_entry.pack(fill="x")
        
        self.search_entry.bind("<Down>", self.focus_listbox)
        self.search_entry.bind("<Return>", self.print_ledger)

        # --- 3. LISTBOX AREA ---
        list_frame = ctk.CTkFrame(self, corner_radius=10)
        list_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        self.ledger_listbox = tk.Listbox(list_frame, font=("Consolas", 12), 
                                         bg="#2b2b2b", fg="white", 
                                         selectbackground="#1f538d", selectforeground="white",
                                         borderwidth=0, highlightthickness=0,
                                         activestyle="none")
        self.ledger_listbox.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        scrollbar = ctk.CTkScrollbar(list_frame, command=self.ledger_listbox.yview)
        scrollbar.pack(side="right", fill="y", padx=(0,5), pady=5)
        self.ledger_listbox.config(yscrollcommand=scrollbar.set)
        
        self.ledger_listbox.bind("<Return>", self.print_ledger)

        # --- 4. ACTION & FOOTER ---
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")

        self.print_btn = ctk.CTkButton(bottom_frame, text="PRINT", command=self.print_ledger, 
                      height=50, font=("Roboto", 16, "bold"), fg_color="#2CC985", hover_color="#23A06A")
        self.print_btn.pack(fill="x", pady=(0, 20))

        footer_line = ctk.CTkFrame(bottom_frame, height=2, fg_color="#333333")
        footer_line.pack(fill="x", pady=10)
        
        credit_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        credit_frame.pack(fill="x")
        
        self.status_label = ctk.CTkLabel(credit_frame, text="Ready", text_color="gray", font=("Roboto", 10))
        self.status_label.pack(side="left")

        dev_name = ctk.CTkLabel(credit_frame, text="Govardhan Raj", font=("Roboto", 11, "bold"), text_color="#3B8ED0")
        dev_name.pack(side="right")
        dev_label = ctk.CTkLabel(credit_frame, text="Developed by ", font=("Roboto", 11), text_color="gray")
        dev_label.pack(side="right")

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
        try:
            with open(path, 'r', encoding='utf-16') as f:
                data = json.load(f)
        except (UnicodeError, json.JSONDecodeError):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")
                return

        if data:
            self.raw_data = data 
            self.process_json_data(data)
            self.status_label.configure(text=f"Loaded: {os.path.basename(path)}")

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
        except Exception as e:
            messagebox.showerror("Error", f"JSON Parse Error: {e}")

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.ledger_listbox.delete(0, tk.END)
        self.filtered_ledgers = []

        for l in self.ledgers:
            if search_term in l["name"].lower():
                self.filtered_ledgers.append(l)
                self.ledger_listbox.insert(tk.END, f" {l['name']}") 
        
        if self.filtered_ledgers:
            self.ledger_listbox.selection_set(0)

    def get_ledger_details(self, ledger_data):
        details = {}
        details['name'] = ledger_data.get('metadata', {}).get('name', '')
        details['gstin'] = "N/A"
        details['address'] = ""
        details['state'] = "N/A"
        details['mobile'] = ledger_data.get('ledgermobile', 'N/A')
        
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

    def open_create_ledger_window(self):
        top = ctk.CTkToplevel(self)
        top.title("Create New Ledger")
        top.geometry("450x550")
        
        # --- FIX 2: Ensure Window stays on top ---
        top.attributes("-topmost", True) 
        top.lift()
        top.focus_force()

        form_frame = ctk.CTkFrame(top)
        form_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(form_frame, text="Create New Ledger", font=("Roboto", 18, "bold")).pack(pady=10)

        fields = {}
        labels = ["Party Name", "Address (comma separated)", "State", "GSTIN", "Mobile"]
        
        for label in labels:
            ctk.CTkLabel(form_frame, text=label + ":", anchor="w").pack(fill="x", padx=20, pady=(5,0))
            entry = ctk.CTkEntry(form_frame)
            entry.pack(fill="x", padx=20, pady=(0,5))
            fields[label] = entry

        def save_new():
            name = fields["Party Name"].get()
            if not name:
                # Temporarily disable topmost so the message box appears correctly above it
                top.attributes("-topmost", False)
                messagebox.showwarning("Error", "Name is required")
                top.attributes("-topmost", True)
                return
            
            new_ledger = {
                "metadata": { "type": "Ledger", "name": name },
                "ledgermobile": fields["Mobile"].get(),
                "ledmailingdetails": [{
                    "address": fields["Address (comma separated)"].get().split(','),
                    "state": fields["State"].get()
                }],
                "ledgstregdetails": [{
                    "gstin": fields["GSTIN"].get()
                }]
            }

            if "tallymessage" not in self.raw_data:
                self.raw_data["tallymessage"] = []
            
            self.raw_data["tallymessage"].append(new_ledger)
            
            try:
                with open(self.file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.raw_data, f, indent=4)
                
                self.process_json_data(self.raw_data)
                
                # Handle message box with topmost window
                top.attributes("-topmost", False)
                messagebox.showinfo("Success", "New Ledger Saved!")
                top.destroy()
            except Exception as e:
                top.attributes("-topmost", False)
                messagebox.showerror("Error", f"Failed to save file: {e}")
                top.attributes("-topmost", True)

        ctk.CTkButton(form_frame, text="SAVE LEDGER", command=save_new, height=40).pack(pady=20, padx=20, fill="x")

    def print_ledger(self, event=None):
        selection = self.ledger_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Ledger", "Please select a ledger to print.")
            return

        note_number = simpledialog.askstring("Packing Note", "Enter Packing Note Number:")
        if note_number is None: return 
        packing_note_text = f"Packing Note: {note_number}"

        index = selection[0]
        selected_item = self.filtered_ledgers[index]
        details = self.get_ledger_details(selected_item['data'])

        pdf_file = f"{details['name']}_Ledger.pdf".replace("/", "_").replace("\\", "_")
        c = canvas.Canvas(pdf_file, pagesize=A4)
        width, height = A4
        
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width / 2, height - 50, packing_note_text)
        c.setLineWidth(1)
        c.line(50, height - 65, width - 50, height - 65)

        y = height - 100
        c.setFont("Helvetica-Bold", 25)
        c.drawCentredString(width / 2, y, details['name'])
        y -= 30 

        c.setFont("Helvetica-Bold", 18)
        raw_address = details['address']
        if raw_address:
            address_lines = [line.strip() for line in raw_address.split(',')]
            for line in address_lines:
                if line:
                    c.drawCentredString(width / 2, y, line)
                    y -= 20
        y -= 10
        c.setFont("Helvetica", 18)
        c.drawCentredString(width / 2, y, f"State: {details['state']}")
        y -= 20
        c.drawCentredString(width / 2, y, f"GSTIN: {details['gstin']}")
        y -= 20
        if details['mobile'] and details['mobile'] != 'N/A':
             c.drawCentredString(width / 2, y, f"Mobile: {details['mobile']}")
             y -= 20

        y -= 15
        c.setLineWidth(0.5)
        c.line(50, y+10, width - 50, y+10)
        y -= 8
        
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, y, "From,  MADHUR MILAN SILK")
        y -= 20
        
        c.setFont("Helvetica", 18)
        c.drawString(50, y, "No.29/1, 2nd floor,Sri Balaji Complex,")
        y -= 20
        c.drawString(50, y, "Appaji rao lane,S.D.D. Road Cross,")
        y -= 20
        c.drawString(50, y, "BENGALURU-560002")
        y -= 25
        
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "GSTIN:- 29AGJPR1392P1ZH   PH: 080-41144941")

        c.save()
        # messagebox.showinfo("Printed", f"PDF saved as: {pdf_file}")
        try:
            os.startfile(pdf_file)
        except:
            pass

if __name__ == "__main__":
    app = LedgerTool()
    app.mainloop()