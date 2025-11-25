import tkinter as tk
from tkinter import filedialog, messagebox
from pipeline import approval_to_output


def start_upload_gui():
    root = tk.Tk()
    root.title("PDF Table Extractor")

    root.resizable(False, False)

    selected_file = tk.StringVar(value="")
    page_number = tk.StringVar(value="1")

    root.selected_file = selected_file
    root.page_number = page_number


    def update_button_state(*args):
        file_ok = bool(selected_file.get())
        page_ok = page_number.get().isdigit()

        if file_ok and page_ok:
            upload_button.config(state="normal")
        else:
            upload_button.config(state="disabled")

    #File Selection
    tk.Label(root, text="Select a PDF file:", font=("Arial", 11)).pack(pady=(20, 5))
    file_frame = tk.Frame(root)
    file_frame.pack()

    file_entry = tk.Entry(file_frame, textvariable=selected_file, width=40, state="readonly")
    file_entry.grid(row=0, column=0, padx=(0, 10))

    def browse_file():
        filename = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            selected_file.set(filename) 

    tk.Button(file_frame, text="Browse", command=browse_file).grid(row=0, column=1)

        # --- Page number input ---
    tk.Label(root, text="Page number:", font=("Arial", 11)).pack(pady=(15, 5))
    tk.Entry(root, textvariable=page_number, justify="center", width=10).pack()

    upload_button = tk.Button(root, text="Upload and Process", width=20, bg="#D0D0D0", fg="black",  activebackground="#B0B0B0",
    activeforeground="black",
    disabledforeground="#888888",  # text stays readable when disabled
    state="disabled")
    
    upload_button.pack(pady=25)
    # --- Run button ---
    def on_run():
        file = selected_file.get()
        if not file:
            messagebox.showerror("Error", "Please select a PDF file.")
            return
        try:
            page = int(page_number.get())-1
        except ValueError:
            messagebox.showerror("Error", "Page number must be an integer.")
            return

        # root.withdraw()  # hide main window during processing
        try:
            approval_to_output(file, page, root)

        except IndexError:
            messagebox.showwarning("Invalid Page Number", "The page number is out of range for the selected file.")
            return 
        
        except Exception as e:
            messagebox.showerror("Processing Error",
            f"An error occurred:\n{str(e)}")
        
        finally:
            root.deiconify()  # show again when done

    upload_button.config(command=on_run)

    selected_file.trace_add("write", update_button_state)
    page_number.trace_add("write", update_button_state)


    root.mainloop()


if __name__ == "__main__":  
    start_upload_gui()