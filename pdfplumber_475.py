import pdfplumber
#from select_table import render_image

#file, table_settings = render_image("/test_pdfs/JPMorgan_portfolio.pdf")

#extract table auto (no settings)

def extract_table_from_pdf(file_path, page_number, table_settings={}):
    
    with pdfplumber.open(file_path) as pdf:
        page = pdf.pages[page_number]
        im = page.to_image()
        #page.extract_tables(table_settings)
        im.debug_tablefinder(table_settings).show()
        data = page.extract_tables(table_settings)
        return data 
    
#write data to csv   
def data_to_csv(data, file_name):
    import csv
    with open(file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        for row in data:
            writer.writerows(row)
    print(f"Data written to {file_name}")

if __name__ == "__main__":
    #scf23.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/475-course-project/test_pdfs/scf23.pdf",11)
    '''
    #QH3_GlobalRealtySharesInc.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/QH3_GlobalRealtySharesInc.pdf", 0)
    # data_to_csv(extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/QH3_GlobalRealtySharesInc.pdf", 0, 
    #                         {"vertical_strategy" : "explicit",
    #                          "explicit_vertical_lines": [70, 320, 400, 470, 540]}), "QH3_globalrealtysharesinc_output.csv")

    #background-checks.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/background-checks.pdf",0)

    #JPMorgan_portfolio.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/JPMorgan_portfolio.pdf",1)

    #nihms.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/nihms.pdf",60)

    #acadian_assets.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/acadian_assets.pdf",2)

    #nces_ed_expend.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/nces_ed_expend.pdf",1)

    #mtis_current.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/mtis_current.pdf",4)

    #statistics.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/statistics.pdf",2)

    #department_of_ed.pdf
    extract_table_from_pdf("/Users/eleanorbadgett/Downloads/475 pdfs/department_of_ed.pdf",0)

    '''