from select_table import render_image
from pdfplumber_475 import extract_table_from_pdf, data_to_csv
import tkinter as tk



def approval_popup():
    """
    Creates a simple popup window that asks the user to select
    between "Approved" and "Intervene".
    Returns either the string "approved" or "intervene".
    """
    # Create a temporary Tk root
    popup = tk.Tk()
    popup.title("Approval Check")
    popup.geometry("300x150")
    popup.attributes('-topmost', True)  # ensures it appears in front

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

def user_intervention(file_name, page_num):
    table_settings = {}
    extract_table_from_pdf(file_name, page_num)
    decision = approval_popup()
    if decision == "intervene":
        file_name, table_settings = render_image(file_name, page_num)
        
    data = extract_table_from_pdf(file_name, page_num, table_settings)
    return data

def write_data(data, file_name):
    newfilename = file_name.replace(".pdf", "_output.csv")
    data_to_csv(data, newfilename)


def approval_to_output(file_name, page_num):
    data = user_intervention(file_name, page_num)
    write_data(data, file_name)


approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/scf23.pdf", 11)
#approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/JPMorgan_portfolio.pdf", 0)
#approval_to_output("/Users/eleanorbadgett/475-course-project/test_pdfs/department_of_ed.pdf", 0)


