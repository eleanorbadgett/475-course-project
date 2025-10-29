# pip install pymupdf matplotlib numpy
import fitz # PyMuPDF
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import pdfplumber

pdf_path = "/Users/eleanorbadgett/Downloads/475 pdfs/department_of_ed.pdf"
page_number=0
zoom = 3.0

# --- Load and render the page ---
doc = fitz.open(pdf_path)
if page_number < 0 or page_number >= len(doc):
    raise IndexError(f"page_number {page_number} out of range (0..{len(doc)-1})")
page = doc[page_number]

# Render to an image (pixels). With Matrix(zoom, zoom), pixel coords map back by / zoom.
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat, alpha=False)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
if pix.n == 1:
    img = np.repeat(img, 3, axis=2)  # grayscale -> RGB

'''
# --- Interactive selection ---
fig, ax = plt.subplots() #can put figsize=(5,10) in ()
ax.imshow(img, origin="upper")  # keep origin at top-left like PDF
ax.set_title(f"Draw a rectangle on page {page_number+1} of {len(doc)}; close window to cancel")

selection = {"done": False, "x0": None, "y0": None, "x1": None, "y1": None}


def onselect(eclick, erelease):
    selection["x0"], selection["y0"] = eclick.xdata, eclick.ydata
    selection["x1"], selection["y1"] = erelease.xdata, erelease.ydata
    selection["done"] = True
    # Draw a visible rectangle
    x0, y0 = selection["x0"], selection["y0"]
    x1, y1 = selection["x1"], selection["y1"]
    ax.add_patch(plt.Rectangle((min(x0,x1), min(y0,y1)),
                                abs(x1-x0), abs(y1-y0),
                                fill=False, linewidth=2))
    fig.canvas.draw()

toggle_selector = RectangleSelector(
    ax, onselect,
    useblit=True,
    button=[1],           # left mouse button
    minspanx=5, minspany=5,
    spancoords='data',
    interactive=True
)

page_height = page.rect.height
crop = page.cropbox

plt.show()  # <-- blocks until the window is closed

doc.close()
print ("CROP BOX:", crop)
if not selection["done"]:
    raise RuntimeError("No rectangle was selected.")

'''
crop = page.cropbox
def interactive_table_selector(img, page_number, total_pages):
    """
    Let user select a rectangle and define rows/columns interactively.

    Returns:
        rect: (x0, y0, x1, y1)
        rows: list of y positions of row lines
        cols: list of x positions of column lines
    """

    # --- Interactive selection ---
    fig, ax = plt.subplots() #can put figsize=(5,10) in ()
    ax.imshow(img, origin="upper")  # keep origin at top-left like PDF
    ax.set_title(f"Draw a rectangle on page {page_number+1} of {len(doc)}; close window to cancel")

    selection = {"done": False, "x0": None, "y0": None, "x1": None, "y1": None}


    def onselect(eclick, erelease):
        selection["x0"], selection["y0"] = eclick.xdata, eclick.ydata
        selection["x1"], selection["y1"] = erelease.xdata, erelease.ydata
        selection["done"] = True
        # Draw a visible rectangle
        x0, y0 = selection["x0"], selection["y0"]
        x1, y1 = selection["x1"], selection["y1"]
        ax.add_patch(plt.Rectangle((min(x0,x1), min(y0,y1)),
                                    abs(x1-x0), abs(y1-y0),
                                    fill=False, linewidth=2, edgecolor = 'green'))
        fig.canvas.draw_idle()

    rect_selector = RectangleSelector(ax, onselect, useblit=True, button=[1],
                                        minspanx=5, minspany=5,
                                        spancoords='data',
                                        interactive=True)
    

    # plt.show()
    # if not selection["done"]:
    #     return None, None, None

    print("Draw a rectangle and press enter in the terminal to continue.")
    plt.show(block = False)
    while not selection["done"]:
        plt.pause(0.1)  # keeps the figure interactive without closing it

    # Rectangle done → disable selector
    rect_selector.set_active(False)

    # --- Ask for rows/columns ---
    num_rows = int(input("Enter number of rows in table: "))
    num_cols = int(input("Enter number of columns in table: "))

    # --- Create grid lines ---
    x0, y0, x1, y1 = selection["x0"], selection["y0"], selection["x1"], selection["y1"]
    h_lines, v_lines = [], []

    for i in range(1, num_rows):
        y = min(y0,y1) + i * abs(y1-y0)/num_rows
        h_lines.append(ax.axhline(y, color='red', lw=1.5, picker=5))
    for i in range(1, num_cols):
        x = min(x0,x1) + i * abs(x1-x0)/num_cols
        v_lines.append(ax.axvline(x, color='blue', lw=1.5, picker=5))

    fig.canvas.draw_idle()

    # --- Make lines draggable ---
    selected_line = {"line": None, "type": None}

    def on_press(event):
        if event.inaxes != ax:
            return
        for line in h_lines + v_lines:
            contains, _ = line.contains(event)
            if contains:
                selected_line["line"] = line
                if line in h_lines:
                    selected_line["type"] = "horizontal"
                else:
                    selected_line["type"] = "vertical"                
                break

    def on_motion(event):
        line = selected_line["line"]
        if line is None or event.xdata is None or event.ydata is None:
            return
        if line.get_xdata()[0] == line.get_xdata()[1]:  # vertical
            line.set_xdata([event.xdata, event.xdata])
        else:  # horizontal
            line.set_ydata([event.ydata, event.ydata])
        fig.canvas.draw_idle()

    def on_release(event):
        selected_line["line"] = None
        selected_line["type"] = None

    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)

    ax.set_title("Drag lines to adjust rows/columns; close window when done")
    plt.show(block = True)

    # --- Collect final positions ---
    rows = [line.get_ydata()[0] for line in h_lines]
    cols = [line.get_xdata()[0] for line in v_lines]
    rect = (min(x0,x1), min(y0,y1), max(x0,x1), max(y0,y1))
    return rect, rows, cols

# --- Convert from pixel/image coords back to PDF coords (points) ---
# With Matrix(zoom, zoom), pixel = pdf_points * zoom  => pdf_points = pixel / zoom.
rectangle, rows, cols = interactive_table_selector(img, page_number, len(doc))

x0_img, y0_img = rectangle[0], rectangle[1]
x1_img, y1_img = rectangle[2], rectangle[3]

# x0_img, y0_img = selection["x0"], selection["y0"] 
# x1_img, y1_img = selection["x1"], selection["y1"]  

x0_pdf = (min(x0_img, x1_img) / zoom) + crop.x0 + crop.y0
x1_pdf = (max(x0_img, x1_img) / zoom) + crop.x0 + crop.y0
y0_pdf = (min(y0_img, y1_img) / zoom) + crop.x0 + crop.y0
y1_pdf = (max(y0_img, y1_img) / zoom) + crop.x0 + crop.y0

pdf_rows = [(y/zoom) + crop.x0 + crop.y0 for y in rows]
pdf_cols = [(x/zoom) + crop.x0 + crop.y0 for x in cols]

col_edge = [x0_pdf, x1_pdf]
row_edge = [y0_pdf, y1_pdf]
pdf_rows.extend(row_edge)
pdf_cols.extend(col_edge)



table = {"vertical_strategy" : "explicit",
         "explicit_vertical_lines": pdf_cols,
         "horizontal_strategy": "explicit",
         "explicit_horizontal_lines": pdf_rows, 
         }

#print("pixels:", x0_img, y0_img, x1_img, y1_img, "\n") 

# result = {
#     "page": page_number,
#     "pdf_rect": (x0_pdf, y0_pdf, x1_pdf, y1_pdf),
#     "pdf_bbox_xywh": (x0_pdf, y0_pdf, x1_pdf - x0_pdf, y1_pdf - y0_pdf),
# }
# print("Selected rectangle (PDF points):", result)

# print(result)

interactive_table_selector(img, 0, len(doc))



def extract_table_from_pdf(file_path, page_number, table_settings={}):
    
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[page_number]
        im = page.to_image()
        #page.extract_tables(table_settings)
        im.debug_tablefinder(table_settings).show()
        data = page.extract_tables(table_settings)
        return data 
    

# table = {"vertical_strategy" : "explicit",
#          "explicit_vertical_lines": [x1_pdf, x0_pdf],
#          "horizontal_strategy": "explicit",
#          "explicit_horizontal_lines": [y1_pdf, y0_pdf]}



extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/department_of_ed.pdf",0, table)
