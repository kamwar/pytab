import cv2
import numpy as np
import os
import math
import skew

FILE_PDF_1 = "pdf_example_1.png"
FILE_PDF_2 = "pdf_example_2.png"
FILE_PDF_2X = "pdf_example_2x.png"
FILE_PDF_2XX = "pdf_example_2xx.png"
FILE_PDF_3 = "pdf_example_3.png"
FILE_PACKING_LIST_1 = "packing_list_1.png"
FILE_PACKING_LIST_2 = "packing_list_2.png"

TRESHOLD_METHOD_OTSU = 0
TRESHOLD_METHOD_VALUE = 1
TRESHOLD_METHOD_ADAPTIVE = 2

file_name = FILE_PACKING_LIST_1
treshold_method = TRESHOLD_METHOD_ADAPTIVE
scale = 10


def main():
    if not os.path.exists(file_name):
        raise Exception("File: {} not found".format(file_name))
    img = cv2.imread(file_name)

    # Convert to gray scale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    #blur = cv2.bilateralFilter(gray, 9, 75, 75)

    if treshold_method == TRESHOLD_METHOD_OTSU:
        # threshold the image, setting all foreground pixels to 255 and all background pixels to 127
        th, threshed = cv2.threshold(blur, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    elif treshold_method == TRESHOLD_METHOD_VALUE:
        th, threshed = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
    elif treshold_method == TRESHOLD_METHOD_ADAPTIVE:
        threshed = cv2.adaptiveThreshold(~blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, -2)

    # Correct image angle
    angle = skew.get_skew(file_name)
    aligned_orig = correct_skew(gray, angle)
    aligned = correct_skew(threshed, angle)

    # Detect horizontal lines
    horizontal = detect_horizontal_lines(aligned)
    # Detect vertical lines
    vertical = detect_vertical_lines(aligned)

    # create a mask which includes the tables
    mask = horizontal + vertical
    # Show extracted vertical and horizontal lines
    cv2.imwrite("result_horizontal_vertical.png", mask)

    # find the joints between the lines of the tables, we will use this information in order to descriminate tables from pictures (tables will contain more than 4 joints while a picture only 4 (i.e. at the corners))
    joints = cv2.bitwise_and(horizontal, vertical)
    cv2.imwrite("result_joints.png", joints)

    # Find external contours from the mask, which most probably will belong to tables or to images
    # kamwar no point argument
    im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # vector<vector<Point> > contours_poly( contours.size() );
    # vector<Rect> boundRect( contours.size() );
    # vector<Mat> rois;
    contours_poly = []
    boundRect = []
    rois = []
    for i in range(len(contours)):
        # find the area of each contour
        area = cv2.contourArea(contours[i])

        #filter individual lines of blobs that might exist and they do not represent a table
        if area < 100:  # value is randomly chosen, you will need to find that by yourself with trial and error procedure
            continue
        contour_poly = cv2.approxPolyDP(contours[i], 3, True)
        contours_poly.append(contour_poly)
        try:
            bound_single = cv2.boundingRect(contour_poly)
            boundRect.append(bound_single)
        except:
            pass

        # find the number of joints that each table has
        roi_joints = joints[bound_single[1]:bound_single[1]+bound_single[3], bound_single[0]:bound_single[0]+bound_single[2]]
        joints_contours = cv2.findContours(roi_joints, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        # if the number is not more than 5 then most likely it not a table
        if len(joints_contours[1]) <= 4:
            continue
        rect_orig = aligned_orig[bound_single[1]:bound_single[1]+bound_single[3], bound_single[0]:bound_single[0]+bound_single[2]]
        rect_threshed = aligned[bound_single[1]:bound_single[1]+bound_single[3], bound_single[0]:bound_single[0]+bound_single[2]]
        rect_mask = mask[bound_single[1]:bound_single[1]+bound_single[3], bound_single[0]:bound_single[0]+bound_single[2]]
        rois.append([rect_orig, rect_threshed, rect_mask, roi_joints])
    if not rois:
        # Table not recognized
        rois.append([aligned_orig, aligned, mask, joints])

    for roi in rois:
        # Now you can do whatever post process you want with the data within the rectangles/tables.
        if 0:
            horizontal_roi = np.hstack((roi[0], roi[2]))
            cv2.imshow("roi", horizontal_roi)
            cv2.waitKey()
        find_cells(roi[0], roi[2], roi[3])


def detect_horizontal_lines(img):
    horizontal = img
    # Specify size on horizontal axis
    rows, cols = horizontal.shape
    horizontalsize = cols // scale
    # Create structure element for extracting horizontal lines through morphology operation
    size = (horizontalsize, 1)  # rows, cols
    horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, size)
    # cv2.imwrite("result_horizontal.png", horizontalStructure)

    # Apply morphology operations
    point = (-1, -1)
    horizontal = cv2.erode(horizontal, horizontalStructure, point)
    horizontal = cv2.dilate(horizontal, horizontalStructure, point)
    return horizontal


def detect_vertical_lines(img):
    vertical = img
    # Specify size on vertical axis
    rows, cols = vertical.shape
    verticalsize = cols // scale

    # Create structure element for extracting vertical lines through morphology operations
    size = (1, verticalsize)  # rows, cols
    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, size)

    # Apply morphology operations
    point = (-1, -1)
    vertical = cv2.erode(vertical, verticalStructure, point)
    vertical = cv2.dilate(vertical, verticalStructure, point)
    # vertical = cv2.dilate(vertical, vertical, verticalStructure, Point(-1, -1)) # expand vertical lines

    # Show extracted vertical lines
    cv2.imwrite("result_vertical.png", vertical)
    return vertical


def correct_skew(img, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = img.shape[:2]
    (cx, cy) = (w // 2, h // 2)
    ## (4) Find rotated matrix, do rotation
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
    cv2.imwrite("result_rot.png", rotated)  # kam
    return rotated


def find_boundaries(img):
    ## (5) find and draw the upper and lower boundary of each lines
    hist = cv2.reduce(img, 1, cv2.REDUCE_AVG).reshape(-1)
    #th = 250
    th = 245
    H, W = img.shape[:2]
    uppers = [y for y in range(H - 1) if hist[y] <= th and hist[y + 1] > th]
    lowers = [y for y in range(H - 1) if hist[y] > th and hist[y + 1] <= th]

    boundaries = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    for y in uppers:
        cv2.line(boundaries, (0, y), (W, y), (255, 0, 0), 1)

    for y in lowers:
        cv2.line(boundaries, (0, y), (W, y), (0, 255, 0), 1)

    cv2.imwrite("result.png", boundaries)
    return boundaries


def find_cells(roi_org, roi_table, roi_joints):
    if 1:
        roi_table_rgb = cv2.cvtColor(roi_table, cv2.COLOR_GRAY2BGR)
        joints_red = cv2.cvtColor(roi_joints, cv2.COLOR_GRAY2BGR)
        _th, mask = cv2.threshold(roi_joints, 127, 255, 0)
        # color all masked pixel red:
        joints_red[mask > 0] = (0, 0, 255)

        roi_table_borders = cv2.copyMakeBorder(roi_table_rgb, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=[255, 0, 0])
        mask = 255 * np.ones(joints_red.shape, joints_red.dtype)
        # The location of the center of the src in the dst
        width, height, channels = roi_table_borders.shape
        center = (height // 2 + 3, width // 2 + 3)
        # Seamlessly clone src into dst and put the results in output
        joints_and_table = cv2.seamlessClone(joints_red, roi_table_borders, mask, center, cv2.MIXED_CLONE)
        roi_org_boundaries = find_boundaries(roi_org)
        roi_org_rgb = cv2.copyMakeBorder(roi_org_boundaries, 3, 3, 3, 3, cv2.BORDER_CONSTANT, value=[255, 0, 0])

        horizontal_roi = np.hstack((roi_org_rgb, joints_and_table))
        cv2.imshow("roi", horizontal_roi)
        cv2.waitKey()


'''
    rois = []
    src = cv2.Canny(roi_table, 100, 200, 3)
    im2, contours, hierarchy = cv2.findContours(src, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        roi = None
        #area = brect[2] * brect[3]
        area = cv2.contourArea(contour)
        if area < 1000:
            continue
        brect = cv2.boundingRect(contour)
        roi = roi_table[brect[1]:brect[1] + brect[3], brect[0]:brect[0] + brect[2]]
        rois.append(roi)
        cv2.imshow("roi", roi)
        cv2.waitKey()

    for roi in rois:
        if 0:
            #horizontal_roi = np.hstack((roi[0], roi[1]))
            cv2.imshow("roi", roi)
            cv2.waitKey()
'''

if __name__ == "__main__":
    main()
