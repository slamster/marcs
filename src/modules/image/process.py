import cv2
import numpy as np
import logging

class Process:
  @staticmethod
  def detectCube(img):
    """
    Crops image to cube and returns it (overwrites image)
    """
    print("Detecting cube....")
    image = cv2.imread(img)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
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
    

    # Print the remaining
    for c in contours:
      cv2.drawContours(image, [c], -1, (0, 255, 0), 2)

    #x, y, w, h = cv2.boundingRect(black_contour)
    #cropped_image = image[y:y+h, x:x+w]
    #cv2.drawContours(image, [black_contour], -1, (0, 255, 0), 2)
    cv2.imwrite(img, image)
    print("Cube contour added")

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


