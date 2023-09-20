from modules.face.facecolors import FaceColor

import cv2
import numpy as np
import logging
from skimage import img_as_ubyte

class Process:
  def __init__(self, image):
    self.image = image
    self.color_names = [color.name for color in FaceColor]

  def apply_whitebalance_patch(self, image, from_row, from_column, row_width, column_width):
      image = image.copy().astype(np.float64)
      image_patch = image[from_row:from_row+row_width, from_column:from_column+column_width]
      image_max = (image*1.0 / image_patch.max(axis=(0, 1))).clip(0, 1)
      print(f"WHITE BALANCE: Max {image_max.max(axis=(0,1))}")
      # back to uint8:
      balanced_image = img_as_ubyte(image_max)
      #cv2.imwrite("/home/pi/www/marcs-latest-wb.png"  , balanced_image)
      return balanced_image

  def percentile_whitebalance(self, image, percentile_value):
      # TODO: Fix
      percentile = np.percentile(image.copy(), percentile_value, axis=(0, 1))
      balanced_image = image / percentile
      balanced_image = np.clip(balanced_image, 0, 255).astype(np.uint8)

      return balanced_image
  
  def apply_white_balance(self, img):
      # Calculate the average color of the image
      avg_color = np.mean(img, axis=(0, 1))
  
      # Calculate the scaling factors for each color channel
      scale_factors = 128.0 / avg_color
  
      # Apply the scaling factors to each color channel
      balanced_image = img.copy() * scale_factors
  
      # Clip the values to ensure they stay within the valid range (0-255)
      balanced_image = np.clip(balanced_image, 0, 255).astype(np.uint8)
  
      return balanced_image
  

  def get_contour_color(self, img, contour):
    # Create a mask for the contour
    mask = np.zeros(img.shape[:2], img.dtype)
    #cv2.drawContours(mask, [contour], 0, (255, 255, 255), thickness=cv2.FILLED)
    cv2.drawContours(mask, [contour], 0, 255, thickness=cv2.FILLED)
    print(f"Mask {mask.shape} and {mask.dtype} vs image {img.shape} and {img.dtype}")

    # Calculate the average color within the contour
    masked_image = cv2.bitwise_and(img, img, mask=mask)
    average_color_bgr = cv2.mean(img, mask=mask)[0:3] # drop alpha channel
    #average_color_bgr = cv2.median(img, mask=mask)[0:3] # drop alpha channel
    #average_color_bgr = np.mean(masked_image, axis=(0, 1))
    average_color = average_color_bgr[::-1]

    # Get the closest color from the face color class:
    closest_color = FaceColor.from_rgb(average_color)
    #closest_color = FaceColor.from_rgb2(average_color)
    print(f"Avg color is {average_color}, which converts to {closest_color}")
    return closest_color

  def detectCube(self):
    """
    Crops image to cube and returns it (overwrites image)
    """
    print("Detecting cube....")
    image = cv2.imread(self.image)
    org_image = image.copy()
    #wb_image = self.apply_white_balance(image)
    #wb_image = self.percentile_whitebalance(image, 97.5)
    # 800x600 image, center bottom has white square -> 400,580
    #wb_image = self.apply_whitebalance_patch(image.copy(), 400, 580, 20, 20)
    # Draw rectangle we used:
    #cv2.rectangle(wb_image,(400,580),(420,600),(0,0,255),2) # white square for white point
    #cv2.rectangle(wb_image,(335,530),(345,540),(0,255,255),2) # black square?
    # Alternate white patch
    #wb_image = self.apply_whitebalance_patch(image.copy(), 0, 0, 20, 20)
    #cv2.rectangle(wb_image,(0,0),(20,20),(0,0,255),2) # white square for white point
    wb_image = self.apply_whitebalance_patch(image.copy(), 400, 550, 20, 20)
    cv2.rectangle(wb_image,(400,550),(420,570),(0,0,255),2) # white square for white point

    image = wb_image.copy()
    #org_image = wb_image.copy()
    #cv2.imwrite("/home/pi/www/marcs-latest-wb.png"  , wb_image)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image = cv2.equalizeHist(gray_image)
    #gray_image = cv2.convertScaleAbs(gray_image, alpha=1.2, beta=30)  

    blurred_image = cv2.GaussianBlur(gray_image, (7, 7), 0)
    edges = cv2.Canny(blurred_image, 00, 100)  # Adjust the thresholds as needed
    raw_contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(raw_contours) == 0:
        print("No square outlines detected.")
        return

    # Drop the smaller ones
    min_contour_area = 2000  # Adjust this threshold as needed
    min_vertices = 4
    max_vertices = 6
    min_aspect_ratio = 0.9
    max_aspect_ratio = 1.1
    contours = []
    
    for c in raw_contours:
      if cv2.contourArea(c) < min_contour_area:
        continue
      perimeter = cv2.arcLength(c, True)
      approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)
    
      if not (min_vertices <= len(approx) <= max_vertices):
        logging.debug(f"Dropping contour due to mismatch in vertices - got {len(approx)}")
        print(f"Dropping contour due to mismatch in vertices - got {len(approx)}")
        continue

      x, y, w, h = cv2.boundingRect(c)
      aspect_ratio = float(w) / h if h != 0 else 0
      if not (min_aspect_ratio <= aspect_ratio <= max_aspect_ratio):
        logging.debug(f"Dropping contour due to weird aspect ratio, got {aspect_ratio}")
        print(f"Dropping contour due to weird aspect ratio, got {aspect_ratio}")
        continue

      """
      Contour has 4263.5 as area, vertices 8 and aspect ratio 1.3225806451612903
      Contour has 4833.0 as area, vertices 4 and aspect ratio 1.0
      Contour has 4836.0 as area, vertices 4 and aspect ratio 1.0
      Contour has 4845.5 as area, vertices 4 and aspect ratio 1.028169014084507
      Contour has 4438.5 as area, vertices 4 and aspect ratio 1.0147058823529411
      Contour has 4497.0 as area, vertices 4 and aspect ratio 1.0
      Contour has 4486.5 as area, vertices 4 and aspect ratio 1.0441176470588236
      Contour has 4326.5 as area, vertices 4 and aspect ratio 1.0298507462686568
      Contour has 4347.0 as area, vertices 4 and aspect ratio 1.0
      Contour has 4444.5 as area, vertices 4 and aspect ratio 1.0597014925373134
      """
      logging.debug(f"Contour has {cv2.contourArea(c)} as area, vertices {len(approx)} and aspect ratio {aspect_ratio}")
      print(f"Contour has {cv2.contourArea(c)} as area, vertices {len(approx)} and aspect ratio {aspect_ratio}")
      contours.append(c)
    
    # Sort them
    contours = sorted(contours, key=lambda contour: cv2.boundingRect(contour)[1])

    # Print the remaining
    for c in contours:
      cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
    print("Cube contour added")

    #x, y, w, h = cv2.boundingRect(black_contour)
    #cropped_image = image[y:y+h, x:x+w]
    #cv2.drawContours(image, [black_contour], -1, (0, 255, 0), 2)

    #cv2.imwrite(self.image, image)

    # TEST: drop all but the first so we can get the colors correct first.
    #contours = contours[:1]
    ## Sanity check, we should have 9 faces
    #if len(contours) != 9:
    #    print(f"Only found {len(contours)} faces you should retry....")
    #    return contours

    # Let's determine colors from contours
    # loop over the contours
    color_detect_image = cv2.GaussianBlur(org_image, (7, 7), 0)
    for c in contours:
        font = cv2.FONT_HERSHEY_SIMPLEX
        #ccolor = self.get_contour_color(org_image, c)
        ccolor = self.get_contour_color(color_detect_image, c)
        print(f"Contour has color: {ccolor}")
        x, y, w, h = cv2.boundingRect(c)
        cv2.putText(image, str(ccolor), (x, y + 30), font, 0.65, (100,100,0), 1, cv2.LINE_AA)
    cv2.imwrite(self.image, image)

  def detectWhite(img):
    """
    Detect white square and outlines it on the image
    """
    print("Detecting....")
    image = cv2.imread(img)
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_white = np.array([0, 0, 200], dtype=np.uint8)
    upper_white = np.array([255, 50, 255], dtype=np.uint8)
    white_mask = cv2.inRange(hsv_image, lower_white, upper_white)
    kernel = np.ones((5, 5), np.uint8)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(white_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) > 0:
        white_contour = max(contours, key=cv2.contourArea)
    else:
        print("No white side detected.")
        return
    cv2.drawContours(image, [white_contour], -1, (0, 255, 0), 2)
    cv2.imwrite(img, image)
    print("White contour added")


