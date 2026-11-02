
import cv2
from pupil_apriltags import Detector
from pathlib import Path

# Change to opencv camera to scan the Apirl Tags
IMAGE_DIR = Path(
    r"C:\Users\JC Edwards\EE490_Capstone\VisionSystem"
)

# Contatins the 3 image 
IMAGE_FILES = [
    "Apriltag_1.jpg",
    "Apriltag_2.jpg",
    "Apriltag_3.jpg"
]

detector = Detector(
    families="tagStandard41h12",
    nthreads=2,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25
)

for filename in IMAGE_FILES:

    image_path = IMAGE_DIR / filename
    output_path = IMAGE_DIR / f"{image_path.stem}_detected.jpg"

    image = cv2.imread(str(image_path))

    print(f"Image dimensions: {image.shape[1]} x {image.shape[0]}")

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    detections = detector.detect(gray)

for index, tag in enumerate(detections, start=1):
    corners = tag.corners.astype(int)
    center_x, center_y = tag.center

