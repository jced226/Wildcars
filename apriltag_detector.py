
import cv2
from pupil_apriltags import Detector
from pathlib import Path


IMAGE_DIR = Path(
    r"C:\Users\JC Edwards\EE490_Capstone\VisionSystem"
)

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

    # Load image
    image = cv2.imread(str(image_path))

    if image is None:
        print(f"ERROR: Could not load {image_path}")
        continue

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect AprilTags
    detections = detector.detect(gray)

    # Process every detection
    for index, tag in enumerate(detections, start=1):

        corners = tag.corners.astype(int)
        center_x, center_y = tag.center

        print("  Corners:")
        for corner_index, corner in enumerate(corners, start=1):
            print(
                f"    Corner {corner_index}: "
                f"({corner[0]}, {corner[1]})"
            )

        # Draw the tag outline
        for i in range(4):
            start = tuple(corners[i])
            end = tuple(corners[(i + 1) % 4])

            cv2.line(
                image,
                start,
                end,
                (0, 255, 0),
                3
            )

        # Mark center
        center = (int(center_x), int(center_y))
        cv2.circle(image, center, 6, (0, 0, 255), -1)

        # Label ID
        cv2.putText(
            image,
            f"ID: {tag.tag_id}",
            (center[0] + 10, center[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )
