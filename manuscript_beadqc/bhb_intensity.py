import tkinter as tk
import tkinter.filedialog
from PIL import ImageTk, Image
import numpy as np
import pandas as pd
import cv2
import os
import re

# 

### define the functions used 
# function for getting calculating bhb diam and center pixel intensity, relative stdev on both metrics
# function also draws circle centre and circle perimeter on top of original image to display later
def bhb_diam(im, rmin, rmax, rdmin, conversion_factor, houghparam2):
    sigma = 0.33
    im = cv2.fastNlMeansDenoising(im, 10, 10, 9, 25)
    # eq = cv2.equalizeHist(im) # equalize histogram to improve contrast

    iminput = im
    # blurred = cv2.GaussianBlur(eq, (3, 3), 0) # gaussian blur to smoothe
    otsu_threshold, otsu = cv2.threshold(
        iminput, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
    )    
    otsu_inv = cv2.bitwise_not(otsu)

    # not necessary because hough contains canny
    # iminput = otsu
    # v = np.median(iminput) # take median intensity of blurred image
    # lower = int(max(0, (1-sigma)*v)) # lower bound for Canny filter
    # upper = int(min(255, (1+sigma)*v)) # upper bound for Canny filter
    # edged = cv2.Canny(iminput, lower, upper) # apply Canny filter to detect edges

    iminput = otsu
    circles = cv2.HoughCircles(iminput, cv2.HOUGH_GRADIENT, 1, rdmin, param1 = 30, param2 = houghparam2, minRadius = rmin, maxRadius = rmax) # detect circles
    
    # now draw the circles on top of the original image and measure center pixel intensity
    circles = np.uint16(np.around(circles))
    intensities = []
    for i in circles[0,:]:
        # first measure intensity at the center pixel. this needs to happen BEFORE the center pixel is marked with a black dot!
        if i[0] != np.shape(im)[1] and i[1] != np.shape(im)[0]: # sometimes the script detects a circle right at the edge (?) and it will then try to get intensities out of bounds of the image.
            intensities.append(im[round(i[1]),round(i[0])])
            # draw the outer circle
            cv2.circle(im,(i[0],i[1]),i[2],(255,255,255),2)
            # draw the center of the circle
            cv2.circle(im,(i[0],i[1]),2,(0,0,0),3)
        
    nbeads = int(np.round(np.divide(circles.size, 3), 2)) # calculate total number of beads

    dmean = np.round((np.mean(circles, axis = 1)[0, 2]*conversion_factor*2), 2) # calculate mean diameter
    dstd = np.round((np.std(circles, axis = 1)[0, 2]*conversion_factor*2), 2) # calculate stdev on diameter
    reldstd = np.round(np.multiply(np.divide(dstd, dmean), 100), 2) # relative stdev

    imean = np.round(np.mean(intensities), 2) # mean intensity
    istd = np.round(np.std(intensities), 2) # stdev on intensity
    relistd = np.round(np.multiply(np.divide(istd, imean), 100), 2) # relative stdev on intensity
    height, width  = im.shape

    return [im, circles, nbeads, dmean, reldstd, imean, relistd, otsu, otsu_inv, width, height]

def pickfile():
    output.insert("end", "dmin\tdmax\tparam2\tnbeads\tdmean\treldstd\timean\trelidstd\tvolimean\tbg\tvolidiff\timeandiff\twidth\theight\tfilename\t\n")
    files = tk.filedialog.askopenfilenames(initialdir = ent_path.get(), title = 'Select .tif files to analyse')

    conversion_factor = float(ent_conversionfactor.get())/float(ent_magnificationfactor.get())
    dmin = int(ent_dmin.get())
    rmin = int(np.round(dmin/conversion_factor/2, 0))
    dmax = int(ent_dmax.get())
    rmax = int(np.round(dmax/conversion_factor/2, 0))
    rdmin = 2*rmin #minimum distance between centerpoints
    houghparam2 = float(ent_houghparam2.get())
    for file in files:
        filename = os.path.basename(file)
        im = cv2.imread(file, 0)

        # call the bhb_diam function below
        outim, circles, nbeads, dmean, reldstd, imean, relistd, otsu, otsu_inv, width, height = bhb_diam(im, rmin, rmax, rdmin, conversion_factor, houghparam2)

        volimean = np.round(cv2.mean(im, otsu)[0],2)
        bg = np.round(cv2.mean(im, otsu_inv)[0],2)
        volidiff = np.round(volimean - bg, 2)
        imeandiff = np.round(imean - bg, 2)

        output.insert("end", str(dmin) + "\t" + str(dmax) + "\t" + str(houghparam2) + "\t" + str(nbeads) + 
        "\t" + str(dmean) + "\t" + str(reldstd) + "\t" + str(imean) + "\t" + str(relistd) + "\t" + str(volimean) + "\t" + str(bg) +
        "\t" + str(volidiff) + "\t" + str(imeandiff) + "\t" + str(width) + "\t" + str(height) + "\t" + filename + "\n")

    output.insert("end", "\n")

    # display the image in a scrollable image window
    outim = Image.fromarray(outim)
    outim = ImageTk.PhotoImage(image=outim)
    image_window = ScrollableImage(window, image=outim, scrollbarwidth=20, width=600, height=600)
    image_window.grid(row=0, column=1, rowspan=3)

# scrollableimage courtesy of stackoverflow user saad (https://stackoverflow.com/questions/56043767/show-large-image-using-scrollbar-in-python/56046307#56046307)
class ScrollableImage(tkinter.Frame):
    def __init__(self, master=None, **kw):
        self.image = kw.pop('image', None)
        sw = kw.pop('scrollbarwidth', 10)
        super(ScrollableImage, self).__init__(master=master, **kw)
        self.cnvs = tkinter.Canvas(self, highlightthickness=0, **kw)
        self.cnvs.create_image(0, 0, anchor='nw', image=self.image)
        # Vertical and Horizontal scrollbars
        self.v_scroll = tkinter.Scrollbar(self, orient='vertical', width=sw)
        self.h_scroll = tkinter.Scrollbar(self, orient='horizontal', width=sw)
        # Grid and configure weight.
        self.cnvs.grid(row=0, column=0,  sticky='nsew')
        self.h_scroll.grid(row=1, column=0, sticky='ew')
        self.v_scroll.grid(row=0, column=1, sticky='ns')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        # Set the scrollbars to the canvas
        self.cnvs.config(xscrollcommand=self.h_scroll.set, 
                           yscrollcommand=self.v_scroll.set)
        # Set canvas view to the scrollbars
        self.v_scroll.config(command=self.cnvs.yview)
        self.h_scroll.config(command=self.cnvs.xview)
        # Assign the region to be scrolled 
        self.cnvs.config(scrollregion=self.cnvs.bbox('all'))
        self.cnvs.bind_class(self.cnvs, "<MouseWheel>", self.mouse_scroll)

    def mouse_scroll(self, evt):
        if evt.state == 0 :
            self.cnvs.yview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.yview_scroll(int(-1*(evt.delta/120)), 'units') # For windows
        if evt.state == 1:
            self.cnvs.xview_scroll(-1*(evt.delta), 'units') # For MacOS
            self.cnvs.xview_scroll(int(-1*(evt.delta/120)), 'units') # For windows

### initialize the master window
window = tk.Tk()
window.title("bhbdiam")

## create a frame for all the entries
frm_entry = tk.Frame(master=window)
frm_entry.grid(row=0, column=0, padx=10, pady=10)

# entry and label for dmin
lbl_dmin = tk.Label(master=frm_entry, text="dmin (um)")
lbl_dmin.grid(row=0, column=0, sticky="w")
ent_dmin = tk.Entry(master=frm_entry, width=10)
ent_dmin.insert(0, "35")
ent_dmin.grid(row=0, column=1, sticky="w")

# entry and label for dmax
lbl_dmax = tk.Label(master=frm_entry, text="dmax (um)")
lbl_dmax.grid(row=1, column=0, sticky="w")
ent_dmax = tk.Entry(master=frm_entry, width=10)
ent_dmax.insert(0, "60")
ent_dmax.grid(row=1, column=1, sticky="w")

# entry and label for conversion factor
lbl_conversionfactor = tk.Label(master=frm_entry, text="conversionfactor (um/px)")
lbl_conversionfactor.grid(row=2, column=0, sticky="w")
ent_conversionfactor = tk.Entry(master=frm_entry, width=10)
ent_conversionfactor.insert(0, "6.45")
ent_conversionfactor.grid(row=2, column=1, sticky="w")

# entry and label for magnification factor
lbl_magnificationfactor = tk.Label(master=frm_entry, text="magnification factor")
lbl_magnificationfactor.grid(row=3, column=0, sticky="w")
ent_magnificationfactor = tk.Entry(master=frm_entry, width=10)
ent_magnificationfactor.insert(0, "10")
ent_magnificationfactor.grid(row=3, column=1, sticky="w")

# entry and label for hough param2 (between 1 and 30)
lbl_houghparam2 = tk.Label(master=frm_entry, text="Hough param2 (5-30)")
lbl_houghparam2.grid(row=4, column=0, sticky="w")
ent_houghparam2 = tk.Entry(master=frm_entry, width=10)
ent_houghparam2.insert(0, "7")
ent_houghparam2.grid(row=4, column=1, sticky="w")

# entry and label for path
lbl_path = tk.Label(master=frm_entry, text="path")
lbl_path.grid(row=5, column=0, sticky="w")
ent_path = tk.Entry(master=frm_entry, width=40)
ent_path.insert(0, "C:\\Users\\u0117999\\OneDrive - KU Leuven\\phd\\pub\\submission\\plosbiol\\20210825_final_images")
ent_path.grid(row=5, column=1, sticky="w")

## create a frame for all the buttons
frm_btns = tk.Frame(master=window)
frm_btns.grid(row=1, column=0, padx=10, pady=10)

btn_pickfile = tk.Button(
    master=frm_btns,
    text="pickfile",
    command = pickfile
)
btn_pickfile.grid(row=0, column=0, padx=10, pady=10)

## create a frame for the output box
frm_output = tk.Frame(master=window)
frm_output.grid(row=2, column=0)

# the output box
output = tk.Text(master=frm_output, width=150, height=25)
output.grid(row=0, column=0)
output_scrollbar = tkinter.Scrollbar(window, command=output.yview)
output_scrollbar.grid(row=0, column=1, sticky='nsew')

## invoke the main loop
window.mainloop()