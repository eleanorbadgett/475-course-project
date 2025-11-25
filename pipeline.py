from select_table import render_image, interactive_selector
from pdfplumber_475 import extract_table_from_pdf, data_to_csv
import tkinter as tk
from tkinter import messagebox



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


def approval_to_output(file_name, page_num):
    # try:
    #     data = user_intervention(file_name, page_num)
    #     write_data(data, file_name)
    # except Exception as e:
    #      raise
    # Automatic extraction attempt → user reviews
    initial_data = extract_table_from_pdf(file_name, page_num)

    decision = approval_popup()

    if decision == "approved":
        final_data = initial_data
    else:
        # User intervention
        file, rect, rows, cols, zoom, page = render_image(file_name, page_num)

        # convert pixel coords → pdf coords
        table_settings = convert_to_pdf_settings(rect, rows, cols, zoom, page)

        # final extraction using user settings
        final_data = extract_table_from_pdf(file_name, page_num, table_settings)

    # ---------------- save CSV ----------------
    csv_name = file_name.replace(".pdf", "_output.csv")
    data_to_csv(final_data, csv_name)

    # ---------------- success popup ----------------
    messagebox.showinfo("Extraction Complete",
                        f"Data successfully saved as:\n{csv_name}")


# ---------------------- coord conversion helper ----------------------
def convert_to_pdf_settings(rect, rows, cols, zoom, page):
    x0, y0, x1, y1 = rect

    def px_to_pdf(val):
        return val / zoom

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


