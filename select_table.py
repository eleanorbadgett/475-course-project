# --- select_table.py ---
import fitz
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import tkinter as tk
from tkinter import ttk

def render_image(filename, page_number=0):
    zoom = 5.0
    doc = fitz.open(filename)

    if page_number < 0 or page_number >= len(doc):
        raise IndexError(f"Invalid page index {page_number}")

    page = doc[page_number]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
    if pix.n == 1:
        img = np.repeat(img, 3, axis=2)

    return interactive_selector(img, zoom, filename, page, page_number)


# -------------------------------------------------------------------
# INTERACTIVE SELECTION WINDOW
# -------------------------------------------------------------------
def interactive_selector(img, zoom, filename, page, page_number):
    selection = {"x0": None, "y0": None, "x1": None, "y1": None}
    h_lines = []
    v_lines = []

    fig, ax = plt.subplots(figsize=(8, 10))
    ax.imshow(img)
    ax.set_title("Select table region → Enter Dimensions → Adjust → DONE")
    plt.subplots_adjust(bottom=0.12)

    # --------------------- RECTANGLE SELECT ---------------------
    def onselect(eclick, erelease):
        selection["x0"] = eclick.xdata
        selection["y0"] = eclick.ydata
        selection["x1"] = erelease.xdata
        selection["y1"] = erelease.ydata

        # --- AUTO-ZOOM INTO SELECTED AREA ---
        xmin = min(selection["x0"], selection["x1"])
        xmax = max(selection["x0"], selection["x1"])
        ymin = min(selection["y0"], selection["y1"])
        ymax = max(selection["y0"], selection["y1"])
        
        # ---- ADD PADDING ----
        pad_x = (xmax - xmin) * 0.10
        pad_y = (ymax - ymin) * 0.10

        xmin_p = max(0, xmin - pad_x)
        xmax_p = min(img.shape[1], xmax + pad_x)
        ymin_p = max(0, ymin - pad_y)
        ymax_p = min(img.shape[0], ymax + pad_y)

        ax.set_xlim(xmin_p, xmax_p)
        ax.set_ylim(ymax_p, ymin_p)  # y inverted
        fig.canvas.draw_idle()

        # After selecting region → open popup for row/col numbers
        rect_selector.set_active(False)
        open_dimension_popup()

    rect_selector = RectangleSelector(
        ax, onselect, useblit=True, button=[1], interactive=True
    )

    # --------------------- DRAGGING LINES ----------------------
    drag_state = {"line": None}

    def on_pick(event):
        drag_state["line"] = event.artist

    def on_motion(event):
        if drag_state["line"] is None or event.inaxes != ax:
            return
        line = drag_state["line"]

        if line in h_lines:  # horizontal
            y = event.ydata
            line.set_ydata([y, y])
        else:                # vertical
            x = event.xdata
            line.set_xdata([x, x])

        fig.canvas.draw_idle()

    def on_release(event):
        drag_state["line"] = None

    fig.canvas.mpl_connect("pick_event", on_pick)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)


    # ---------------------- POPUP FOR ROW/COL INPUT ----------------------
    def open_dimension_popup():
        popup = tk.Toplevel()
        popup.title("Enter Dimensions")
        popup.geometry("240x160")
        popup.transient()
        popup.grab_set()

        ttk.Label(popup, text="Rows:").pack(pady=(10, 0))
        row_entry = ttk.Entry(popup, justify="center")
        row_entry.pack()

        ttk.Label(popup, text="Columns:").pack(pady=(10, 0))
        col_entry = ttk.Entry(popup, justify="center")
        col_entry.pack()

        def apply_dims():
            try:
                r = int(row_entry.get())
                c = int(col_entry.get())
            except:
                return

            popup.destroy()
            draw_grid(r, c)

        ttk.Button(popup, text="Apply", command=apply_dims).pack(pady=10)
        popup.wait_window()


    # ---------------------- DRAW GRID ----------------------
    def draw_grid(r, c):
        for ln in h_lines + v_lines:
            ln.remove()
        h_lines.clear()
        v_lines.clear()

        x0, y0, x1, y1 = selection["x0"], selection["y0"], selection["x1"], selection["y1"]
        ymin = min(y0, y1)
        ymax = max(y0, y1)
        xmin = min(x0, x1)
        xmax = max(x0, x1)

        # Horizontal lines
        for i in range(1, r):
            y = ymin + i * (ymax - ymin) / r
            h_lines.append(ax.axhline(y, color="red", lw=1.5, picker=5))

        # Vertical lines
        for i in range(1, c):
            x = xmin + i * (xmax - xmin) / c
            v_lines.append(ax.axvline(x, color="blue", lw=1.5, picker=5))

        fig.canvas.draw_idle()


    # ---------------------- DONE BUTTON ----------------------
    from tkinter import messagebox

    def finish(event=None):
        # require that the user has actually drawn a rectangle
        if selection["x0"] is None:
            messagebox.showwarning("No Selection", "Please draw a rectangle around the table before pressing DONE.")
            return
        selection["done"] = True
        plt.close(fig)


    btn_ax = fig.add_axes([0.75, 0.02, 0.2, 0.07])
    done_btn = matplotlib.widgets.Button(btn_ax, "DONE")
    done_btn.on_clicked(finish)

    plt.show()
    # ---------------------- WAIT FOR DONE ----------------------
    while not selection.get("done", False):
        plt.pause(0.1)

    # ---------------------- RETURN RESULTS ----------------------
    # If user never selected anything, return None for rect so caller can handle it

    if selection["x0"] is None:
        return filename, None, [], [], zoom, page
    
    rows = [ln.get_ydata()[0] for ln in h_lines]
    cols = [ln.get_xdata()[0] for ln in v_lines]

    rect = (
        min(selection["x0"], selection["x1"]),
        min(selection["y0"], selection["y1"]),
        max(selection["x0"], selection["x1"]),
        max(selection["y0"], selection["y1"]),
    )

    tk_parent = fig.canvas.manager.window 
    return tk_parent, rect, rows, cols, zoom, page
    #return filename, rect, rows, cols, zoom, page
