import cv2
import tkinter as tk
from PIL import ImageTk, Image
import os
from numpy import ndarray
import numpy as np
import base64


threshold_ = 65

def custom_filter(img_to_find: ndarray):
    # Facet must be in the middle of picture in X axis.
    green_channel = img_to_find[:,:,1]
    img_h, img_w, _ = img_to_find.shape
    print(f"image size {img_h}, {img_w}")
    startline = int(img_w/10)
    varr = find_verticle_array(green_channel, startline)
    varr_mid = find_verticle_array(green_channel, int(img_w/2))
    cutpoint_y = find_cut_point(varr)
    cutend_y = find_cut_point(varr_mid)
    cutpoint_x, cutend_x = find_horiz_point(green_channel[cutpoint_y])
    start_y = cutpoint_y-15
    end_y = cutend_y + 10
    mid_y = int((start_y + end_y)/2)
    cutpoint_x, cutend_x = find_horiz_point(green_channel[mid_y])
    start_x = cutpoint_x -20
    end_x = cutend_x + 20
    print(f"crop to [{start_y}: {end_y}, {start_x}: {end_x}]")
    mask = green_channel[start_y: end_y, start_x: end_x]
    # print(varr)
    histogram = {0:0}
    for i in range(len(mask)):
        for j in range(len(mask[i])):
            if int(mask[i][j]) > 100:
                try:
                    histogram[int(mask[i][j])] += 1
                except:
                    histogram[int(mask[i][j])] = 1
    # print(histogram)
    peak_color = keywithmaxval(histogram)
    # print(peak_color)
    # overwrite the green channel to other channel for more evidance.
    img_with_mask = img_to_find[start_y: end_y, start_x: end_x]
    img_with_mask[:,:,0] = img_with_mask[:,:,1]
    img_with_mask[:,:,2] = img_with_mask[:,:,1]
    _, output = cv2.threshold(img_with_mask, round(peak_color) + 25,255,cv2.THRESH_BINARY)
    
    # Save
    maskfile = os.path.join(r"tmp", "mask.png")
    resultfile = os.path.join(r"tmp", "tmp.png")
    cv2.imwrite(maskfile, mask)
    cv2.imwrite(resultfile, output)
    return maskfile, resultfile


def decode_binary(input: str, resize: bool = False):
    input_file = Image.open(input)
    if resize:
        input_file = input_file.resize([640, 480])
    tmp_image = os.path.join(r"tmp", "working.png")
    input_file.save(tmp_image)
    input_file.close()
    with open(tmp_image, "rb") as image_file:
        image_data_base64_encoded_string = base64.b64encode(image_file.read())
    return image_data_base64_encoded_string

    
def open_picture(event):
    selected = fileselect.get()
    ori_full_filepath = os.path.join(r"example", selected)
    if os.path.exists(ori_full_filepath):
        original_base64 = decode_binary(ori_full_filepath, True)
        oiginal_picture = tk.PhotoImage(data=bytes(original_base64))
        imglive.config(image=oiginal_picture)
        imglive.image = oiginal_picture
        imglive.update()
        image_to_filter = cv2.imread(ori_full_filepath, 3)
        image_to_filter = cv2.resize(image_to_filter, (640, 480))
        filter_image, result_image = custom_filter(image_to_filter)
        filter_base64 = decode_binary(filter_image)
        filter_picture = tk.PhotoImage(data=bytes(filter_base64))
        imgfilter.config(image=filter_picture)
        imgfilter.image = filter_picture
        result_base64 = decode_binary(result_image)
        result_picture = tk.PhotoImage(data=bytes(result_base64))
        imgresult.config(image=result_picture)
        imgresult.image = result_picture
        imgfilter.update()
        imgresult.update()


def keywithmaxval(d):
    v = list(d.values())
    k = list(d.keys())
    return k[v.index(max(v))]

def find_verticle_array(arr, position: int):
    return arr[:,position]

def find_cut_point(arr):
    i = 0
    for value in arr:
        if value > threshold_:
            i += 1
        else:
            break
    return i

def find_horiz_point(arr):
    i = 0
    hole_detected = False
    for value in arr:
        if value < threshold_:
            hole_detected = True
            i += 1
        else:
            if hole_detected:
                break
    reverse_arr = arr[::-1]
    j = 0
    hole_detected = False
    for value in reverse_arr:
        if value < threshold_:
            j += 1
            hole_detected = True
        else:
            if hole_detected:
                break
    end_edge = len(arr) - j
    return i, end_edge
#######################################################3##
#########################################################
#######33                   Main
#########################################################
#######################################################3##
root = tk.Tk()
root.geometry('1200x600')
f_path = r"example"
if not os.path.exists(r'tmp'):
    os.makedirs(r'tmp')
included_pic_extensions = ['.jpg', '.JPG', '.png', '.PNG', 'TIF', 'tif']
image_blank =  tk.PhotoImage(data=bytes(b'iVBORw0KGgoAAAANSUhEUgAAAB8AAAAgCAYAAADqgqNBAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAU0SURBVFhHrZZdaBRXFMd/d3Y3bnYys0kktexuEg3YBgwYESttffG9lT4VfNBIaykp+mIi5kFoixh9FT+IgX6khYbSvhhoHyqm5sEq2ooYvxYKajSGgtWd/Uq6mZnTB7PTnUnWxNgfXObec869/8vlzL1HsThq1apVsVAo1AisVEo1AitFxOsD5W+5r0Tkd+DQo0eP0sEFyyiARCLxDvB2lYWalFI1wYkLEYlE0HUd27bJ5/OIyLSIHJiamjoBSDBeJRKJ95VS31caQ6EQuq5jGAamaRKPx4nH49TH49TX11Pf0EBD4NvY2Iiu64TDYcR1ufDbb3z26adMPHgA8ItS6oOHDx9OVuqQTCZPJZNJSSaT8vVXX8mDiQnJZDJSKBRkZmZGZkslcWxbXNcVcV15Ef5+/Fg+6e6WZDIpiUTi70Qi8b5PPJVKDZbF161bJ7+OjgbXeCls25bh4WF5/bXXypv4trW1tR5ApVKpQRH5qLwZTdPo6elh7969aJrm2yiA4zgUi0VyuRzZbJZsNuv1g9/KfjqdJpfLlZe5D2ybJ15m9erVtLW1USwWsSyLXC5HJpNhenoax3GC4cvhu6rii6GUIhqNEovF0GMxdF1Hr6ujbq4ZhuFrpmGg6zpffPklly9fRkR+rCqu6zq7P/yQplde8S1gGAaGaWIaBuFIhFAohKZpXlNKeW0hTp8+zaFDhxCRH30JV9m6urqCufO/MDg4WE68H+Zn1ByRSCRoWhKO45BOp7ly5Qqjo6OcOXOGa9euBcMACAcN1Th79ixjY2NYlkUmk8GyLGKxGENDQ6xYscKL6+vrY3h42Bs3Nzdz4MABOjs7PVuZkGma7wIbg461a9eybds2AFzXpauri4sXL3Lz5k3u3bvH1NQUExMTuK7Lli1bvHkdHR1s6Ozkp59/RinFhQsXWL9+vZcDV69eZWxsDOBW1WOvRNM0zp07R29vb9DFwMAA169f98aJRILODRu8cU1NTdXkW5I4QDQapWaBPLBtm56eHkqlUtC1KEsWr6S2thbDMLzx7du3OX78uC9mKSxLPBaLsX//fp/txIkT3Lp1y2dbjGWJA+zYsYNNmzZ549nZWfbt24dt276457Fs8XA4zJEjR3y/2Y0bNzh58qQv7nksWxygvb2dPXv2+GzHjh0jna5aOfl4KXGA7u5u2tvbvXGpVOLgwYO+mGq8tHg0GuXo0aOEQiHPNjnpr5aqoeG68wq7F2Xjxo3s2rUraF4UDU37M2h8UZRS9Pb20tzcHHQ9Fy0SiXwDPA46FsKVZ4dULBYZGhrizp07ns8wDA4fPrxg6VUN7e7du3+FlfoIqFobiQg7d+6kv78fgJmZGfr7+xkZGfHFbd26lb6+PgzDoKmpie3bty94JQdRqVTqcGUxsXv3bq8AcBxHLl26JDfGx+X+/fvy9MkTyefz4jiOr1AQEXFdVwr5vBSLxWfldoCBgYF5xYSYpvm5grPl3cjcETP3qm3evJl1HR20tLRQ39CArusLHrFSipiuU1tb671mIsL09DSTk5OcP3/+v9iKebS2tr5q2/YloHXNmjWMjIxgmiaFQoFcLucrjZfaLMuiUCgwOztbKQXw9byHtqWl5S3bts8ppaJB3/+GyBMtFHpvnjjPSp+PXdc9tcgl5ADTQF4plQPySiSrlMqKUlnAUkpZImJpYKFpGcCKwNNa00yPj48/XVAc0NpaWt50RN4QpWbnJltAJgJWJBZ7qrtuISJS+qeuzrEsy4nH427bH3+4P4A7t8ail9e/a0xLDkORZUQAAAAASUVORK5CYII='), height=60, width=60)
list_of_files_tmp = [fn for fn in os.listdir(f_path)
    if any((fn.endswith(ext) for ext in included_pic_extensions)) and (not fn.startswith('.'))]
list_of_files = []
[list_of_files.append(x) for x in list_of_files_tmp if x not in list_of_files]
fileselect = tk.StringVar(root)
fileselect.set(list_of_files[0])
list_of_files = list_of_files 
filelist_optionmenu = tk.OptionMenu(root, fileselect, *list_of_files, command=open_picture)
filelist_optionmenu.place(x=50, y=10)
imglive = tk.Label(root, image=image_blank, borderwidth=2, justify='center', border=2, relief="solid", width=650, height=460)
imglive.place(x=5, y=50)
imgfilter = tk.Label(root, image=image_blank, borderwidth=2, justify='center', border=2, relief="solid", width=400, height=130)
imgfilter.place(x=700, y=50)
imgresult = tk.Label(root, image=image_blank, borderwidth=2, justify='center', border=2, relief="solid", width=400, height=130)
imgresult.place(x=700, y=200)
root.mainloop()
