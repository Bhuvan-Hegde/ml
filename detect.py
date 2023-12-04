import numpy as np
import cv2
import imutils
import pytesseract
import pandas as pd
import time

# Load image
image_path = 'images/10.jpg'
img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
img = imutils.resize(img, width=500)

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Bilateral filter for noise reduction
gray = cv2.bilateralFilter(gray, 11, 17, 17)

# Adaptive thresholding
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours
cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if len(cnts) == 2 else cnts[1]

# Iterate through contours
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    
    if len(approx) == 4 and cv2.contourArea(c) > 1000:
        NumberPlateCnt = approx

        # Masking the part other than the number plate
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [NumberPlateCnt], 0, 255, -1)
        new_image = cv2.bitwise_and(img, img, mask=mask)

        # OCR Configuration
        config = ('-l eng --oem 1 --psm 6')

        # Run Tesseract OCR on the masked image
        text = str(pytesseract.image_to_string(new_image, config=config))

        # Data is stored in CSV file
        raw_data = {'date': [time.asctime(time.localtime(time.time()))],
                    'v_number': [text]}

        df = pd.DataFrame(raw_data, columns=['date', 'v_number'])
        df.to_csv('data.csv')

        # Print recognized text
        print("Recognized Text:", text)

        # Display the final processed image with the license plate highlighted
        cv2.imshow("Final_image", new_image)
        cv2.waitKey(0)
