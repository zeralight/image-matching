from fpdf import FPDF
from os.path import join, isfile
import csv
import sys
import re

if __name__ == '__main__':
    jpegs_path = "../ALL_JPG_REDUCED_200"
    tifs_path = "../ALL_TIF_REDUCED_200"
    
    not_found = 0
    pdf_size = 384
    nfile = 1
    with open(sys.argv[1], "r") as csvfile:
        reader = csv.reader(csvfile) 
        i = 0
        count = 0
        for row in reader:
            if count%pdf_size == 0:
                global pdf
                pdf = FPDF()
                pdf.set_font("Arial", size=8)
            jpeg_fname, tif_fname = row[:2]
            if i == 0:
                pdf.add_page()
            if isfile(join(jpegs_path, jpeg_fname)) and isfile(join(tifs_path, tif_fname)):
                pdf.image(join(jpegs_path, jpeg_fname), 60, 50*i + 10, w=30)
                pdf.image(join(tifs_path, tif_fname), 120, 50*i + 10, w=30)
            else:
                print("{} or {} not found".format(join(jpegs_path, jpeg_fname), join(tifs_path, tif_fname)))
                not_found += 1

            pdf.ln(1)
            pdf.text(55, 50*i + 44, txt=jpeg_fname)
            pdf.text(115, 50*i + 44, txt=tif_fname)

            pdf.ln(1)
            i = (i+1)%6
            count += 1
            if count%pdf_size == 0:
                print("Saving pdf " + str(nfile))
                pdf.output("pdf/results-phash_{}.pdf".format(nfile))
                nfile += 1
        if count%pdf_size > 0:
            print("Saving pdf " + str(nfile))
            pdf.output("pdf/results-phash_{}.pdf".format(nfile))
            nfile += 1
    print("not found:", not_found)