 
import json
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

class NotebookCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jupyter Notebook Creator")
        self.root.geometry("600x700")
        
        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabel", padding=3)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input text area
        ttk.Label(self.main_frame, text="Enter CHAIN/THOUGHT text:").grid(row=0, column=0, sticky=tk.W)
        self.text_input = tk.Text(self.main_frame, height=15, width=60)
        self.text_input.grid(row=1, column=0, columnspan=2, pady=5)
        
        # Formatting options
        ttk.Label(self.main_frame, text="Formatting Options:").grid(row=2, column=0, sticky=tk.W)
        self.add_timestamps = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.main_frame, text="Add timestamps to blocks", variable=self.add_timestamps).grid(row=3, column=0, sticky=tk.W)
        
        # Output file name
        ttk.Label(self.main_frame, text="Output File Name:").grid(row=4, column=0, sticky=tk.W)
        self.filename_entry = ttk.Entry(self.main_frame, width=40)
        self.filename_entry.insert(0, "chains_and_thoughts.ipynb")
        self.filename_entry.grid(row=5, column=0, sticky=tk.W)
        ttk.Button(self.main_frame, text="Browse", command=self.browse_file).grid(row=5, column=1)
        
        # Buttons
        ttk.Button(self.main_frame, text="Create Notebook", command=self.create_notebook).grid(row=6, column=0, pady=10)
        ttk.Button(self.main_frame, text="Clear Input", command=self.clear_input).grid(row=6, column=1)
        
        # Status label
        self.status_var = tk.StringVar()
        ttk.Label(self.main_frame, textvariable=self.status_var, wraplength=500).grid(row=7, column=0, columnspan=2, pady=5)
        
    def browse_file(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".ipynb",
            filetypes=[("Jupyter Notebook", "*.ipynb"), ("All files", "*.*")]
        )
        if filename:
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, filename)
    
    def clear_input(self):
        self.text_input.delete("1.0", tk.END)
        self.status_var.set("")
    
    def create_notebook(self):
        try:
            raw_text = self.text_input.get("1.0", tk.END).strip()
            if not raw_text:
                messagebox.showwarning("Input Error", "Please enter some CHAIN/THOUGHT text")
                return
                
            # Split into initial blocks with CHAIN/THOUGHT markers
            blocks = re.split(r"(?=\*\*\[CHAIN_\d+\]|\*\*\[THOUGHT_\d+_\d+\])", raw_text.strip())
            blocks = [b.strip() for b in blocks if b.strip()]
            
            # Initialize cells list with a separator before the first CHAIN
            cells = []
            if blocks and any("**[CHAIN_" in b for b in blocks):
                cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})
            
            # Process each block
            for i, block in enumerate(blocks):
                if self.add_timestamps.get():
                    lines = block.splitlines()
                    if lines:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        lines.insert(1, f"*Created: {timestamp}*")
                    block = "\n".join(lines)
                
                # Add separator before CHAIN blocks
                if re.match(r"\*\*\[CHAIN_\d+\]", block):
                    cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})
                
                cells.append({"cell_type": "markdown", "metadata": {}, "source": block.splitlines(keepends=True)})
            
            # Extract and add RESPONSE section in a separate cell
            response_match = re.search(r"\*\*\[RESPONSE\]\*\*", raw_text, re.MULTILINE)
            if response_match:
                response_start = response_match.end()
                response_text = raw_text[response_start:].strip()
                if response_text:
                    # Remove the RESPONSE section from the last block if it was included
                    if cells and "[RESPONSE]" in cells[-1]["source"][0]:
                        cells[-1]["source"] = [s for s in cells[-1]["source"] if "[RESPONSE]" not in s]
                    # Add separator and RESPONSE section
                    cells.append({"cell_type": "markdown", "metadata": {}, "source": ["---\n"]})
                    cells.append({"cell_type": "markdown", "metadata": {}, "source": [f"**[RESPONSE]**\n{response_text}\n"]})
            
            # Notebook structure
            notebook = {
                "cells": cells,
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "file_extension": ".py",
                        "name": "python"
                    }
                },
                "nbformat": 4,
                "nbformat_minor": 5
            }
            
            # Save file
            output_file = self.filename_entry.get()
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(notebook, f, ensure_ascii=False, indent=2)
            
            self.status_var.set(f"✅ Notebook saved as {output_file}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create notebook: {str(e)}")
            self.status_var.set(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NotebookCreatorGUI(root)
    root.mainloop()