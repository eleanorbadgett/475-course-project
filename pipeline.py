from select_table import render_image, interactive_selector
from pdfplumber_475 import extract_table_from_pdf, data_to_csv
import tkinter as tk
from tkinter import messagebox
import os



def approval_popup(parent_window):
    """
    Creates a simple popup window that asks the user to select
    between "Approved" and "Intervene".
    Returns either the string "approved" or "intervene".
    """
    popup = tk.Toplevel(parent_window)
    popup.title("Approval Check")
    popup.geometry("300x150")
    #popup.transient(parent_window)
    popup.grab_set()
    popup.attributes('-topmost', True)  # ensures it appears in front
    popup.lift()
    #popup.after(10, lambda: popup.lift())
    #parent_window.lower()

    result = tk.StringVar(value="")  # to store user’s choice

    # --- Label text ---
    tk.Label(
        popup,
        text="Review the table.\nIs this selection approved?",
        font=("Arial", 11),
        justify="center"
    ).pack(pady=15)

    # --- Buttons ---
    def on_approve():
        result.set("approved")
        popup.destroy()

    def on_intervene():
        result.set("intervene")
        popup.destroy()

    button_frame = tk.Frame(popup)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Approve", width=10, command=on_approve).grid(row=0, column=0, padx=10)
    tk.Button(button_frame, text="Intervene", width=10, command=on_intervene).grid(row=0, column=1, padx=10)

    # Wait for user choice (blocks until popup destroyed)
    popup.wait_window()

    return result.get()

# def user_intervention(file_name, page_num):
#     table_settings = {}
#     extract_table_from_pdf(file_name, page_num)
#     decision = approval_popup()
#     if decision == "intervene":
#         file_name, table_settings = render_image(file_name, page_num)
        
#     data = extract_table_from_pdf(file_name, page_num, table_settings)
#     return data

# def write_data(data, file_name):
#     newfilename = file_name.replace(".pdf", "_output.csv")
#     data_to_csv(data, newfilename)


def approval_to_output(file_name, page_num, preview_tk_window):
    initial_data = extract_table_from_pdf(file_name, page_num)

    
    decision = approval_popup(preview_tk_window)

    if decision == "approved":
        final_data = initial_data
    else:
        # User intervention
        #file, rect, rows, cols, zoom, page = render_image(file_name, page_num)

        # Show debug image and get reference to that window
        debug_window, rect, rows, cols, zoom, page = render_image(file_name, page_num)
        #decision = approval_popup(preview_tk_window)
        # convert pixel coords → pdf coords
        table_settings = convert_to_pdf_settings(rect, rows, cols, zoom, page)

        # final extraction using user settings
        final_data = extract_table_from_pdf(file_name, page_num, table_settings)

    def test_conflicting_name(file_name):
        if not os.path.exists(file_name):
            return file_name
        name, ext = os.path.splitext(file_name)
        counter = 1 
        new_path = f"{name}.{counter}{ext}"

        while os.path.exists(new_path):
            counter += 1 
            new_path = f"{name}.{counter}{ext}"

        return new_path
    # ---------------- save CSV ----------------
    csv_name = file_name.replace(".pdf", f"_output_{page_num+1}.csv")
    csv_name = test_conflicting_name(csv_name)
    data_to_csv(final_data, csv_name)

    # ---------------- success popup ----------------
    # messagebox.showinfo("Extraction Complete",
    #                     f"Data successfully saved as:\n{csv_name}")
    def extraction_complete_popup(root, csv_name, current_file, current_page):
        """
        Popup after extraction with 3 options:
        1. Continue processing current document
        2. Process new document
        3. Close application
        """
        popup = tk.Toplevel(root)
        popup.title("Extraction Complete")
        popup.geometry("500x200")
        #popup.transient(root)
        popup.grab_set()

        tk.Label(popup, text=f"Data successfully saved as:\n{csv_name}",
                font=("Arial", 11), justify="center").pack(pady=(10, 10))

        # Button 1: Continue Processing Current Document
        def continue_current():
            popup.destroy()
            # simply returns to upload GUI; main window already open

        tk.Button(popup, text="Continue Processing Current Document",
                width=35, command=continue_current).pack(pady=5)

        # Button 2: Process New Document
        def process_new():
            popup.destroy()
            # Reset the upload GUI
            # We can destroy and recreate main window or call your initialize function
            # For minimal edits, just reset variables and entry fields
            root.selected_file.set("")
            root.page_number.set("1")

        tk.Button(popup, text="Process New Document",
                width=35, command=process_new).pack(pady=5)

        # Button 3: Close Application
        def close_app():
            popup.destroy()
            root.quit()

        tk.Button(popup, text="Close Application",
                width=35, command=close_app).pack(pady=5)

        popup.lift()
        popup.attributes('-topmost', True)
        popup.after_idle(popup.attributes, '-topmost', False)
        popup.wait_window()

    extraction_complete_popup(preview_tk_window, csv_name, file_name, page_num)

# ---------------------- coord conversion helper ----------------------
def convert_to_pdf_settings(rect, rows, cols, zoom, page):
    x0, y0, x1, y1 = rect

    crop = page.cropbox 

    print(f"x and y vals: {x0}, {y0}, {x1}, {y1}")

    def px_to_pdf(val):
        return val / zoom + crop.x0 + crop.y0

    pdf_rows = [px_to_pdf(y) for y in rows] + [px_to_pdf(y0), px_to_pdf(y1)]
    pdf_cols = [px_to_pdf(x) for x in cols] + [px_to_pdf(x0), px_to_pdf(x1)]



    return {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": pdf_cols,
        "horizontal_strategy": "explicit",
        "explicit_horizontal_lines": pdf_rows,
    }


if __name__ == "__main__":
    approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/scf23.pdf", 11)
    #approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/JPMorgan_portfolio.pdf", 0)
    #approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/department_of_ed.pdf", 0)

