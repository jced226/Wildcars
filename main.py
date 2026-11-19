
import cv2
import json
import numpy as np
import subprocess
from pathlib import Path
from pupil_apriltags import Detector

# ============================================================
# CAMERA CONFIGURATION
# ============================================================

W, H = 640, 480

camera = subprocess.Popen(
    [
        "rpicam-vid",
        "--timeout", "0",
        "--width", str(W),
        "--height", str(H),
        "--framerate", "30",
        "--codec", "mjpeg",
        "--nopreview",
        "--output", "-"
    ],
    stdout=subprocess.PIPE,
    stderr=None,
    bufsize=0
)

# Read one JPEG frame from the rpicam-vid MJPEG stream.
def get_camera_frame():

    if camera.stdout is None:
        return None

    data = bytearray()

    # Find the beginning of a JPEG frame.
    while True:
        byte = camera.stdout.read(1)

        if not byte:
            return None

        data.append(byte[0])

        if len(data) >= 2 and data[-2:] == b'\xff\xd8':
            break

    # Read until the end of the JPEG frame.
    while True:
        byte = camera.stdout.read(1)

        if not byte:
            return None

        data.append(byte[0])

        if len(data) >= 2 and data[-2:] == b'\xff\xd9':
            break

    frame = cv2.imdecode(
        np.frombuffer(data, dtype=np.uint8),
        cv2.IMREAD_COLOR
    )

    return frame


# ============================================================
# GREEN FLAG DETECTION CONFIGURATION
# ============================================================

lower_green = np.array([35, 52, 72], dtype=np.uint8)
upper_green = np.array([85, 255, 255], dtype=np.uint8)

initial_y = None

movement_threshold = 20
minimum_green_area = 100

flag_triggered = False


# ============================================================
# APRILTAG DETECTION CONFIGURATION
# ============================================================

TAG_FAMILY = "tagStandard41h12"

tag_detector = Detector(
    families=TAG_FAMILY,
    nthreads=2,
    quad_decimate=1.0,
    quad_sigma=0.0,
    refine_edges=1,
    decode_sharpening=0.25
)

IMAGE_DIR = Path(__file__).resolve().parent
REFERENCE_FILE = IMAGE_DIR / "reference_tag.json"

reference_id = None

reference_saved = False
searching_for_match = False
match_found = False

missing_frames = 0
REQUIRED_MISSING_FRAMES = 5


# ============================================================
# MAIN VISION SYSTEM
# ============================================================

try:

    while True:

        # ----------------------------------------------------
        # GET CAMERA FRAME
        # ----------------------------------------------------

        frame = get_camera_frame()

        if frame is None:

            print("Could not read from the Arducam.")
            break


        # ====================================================
        # 1. GREEN FLAG DETECTION
        # ====================================================

        flag_status = "Searching for green flag"

        if not flag_triggered:

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            mask = cv2.inRange(
                hsv,
                lower_green,
                upper_green
            )

            mask = cv2.morphologyEx(
                mask,
                cv2.MORPH_OPEN,
                np.ones((5, 5), np.uint8)
            )

            contours, _ = cv2.findContours(
                mask,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )

            largest_contour = None
            largest_area = 0

            for contour in contours:

                area = cv2.contourArea(contour)

                if area > largest_area and area > minimum_green_area:

                    largest_area = area
                    largest_contour = contour


            if largest_contour is not None:

                x, y, w, h = cv2.boundingRect(largest_contour)

                cx = x + w // 2
                cy = y + h // 2

                current_position = (cx, cy)

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    frame,
                    current_position,
                    6,
                    (0, 0, 255),
                    cv2.FILLED
                )

                if initial_y is None:

                    initial_y = cy

                upward_movement = initial_y - cy

                if upward_movement >= movement_threshold:

                    flag_triggered = True

                    flag_status = "GREEN FLAG DETECTED!"

                    print("GREEN FLAG DETECTED!")

                else:

                    flag_status = (
                        f"Tracking green flag: "
                        f"{upward_movement} px upward"
                    )

                cv2.putText(
                    frame,
                    f"Flag Position: ({cx}, {cy})",
                    (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (0, 255, 0),
                    2
                )

            else:

                initial_y = None

        else:

            flag_status = "GREEN FLAG DETECTED!"


        # ====================================================
        # 2. APRILTAG DETECTION
        # ====================================================

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        detections = tag_detector.detect(gray)

        current_ids = {
            tag.tag_id for tag in detections
        }


        # Save the first AprilTag detected.
        if not reference_saved and detections:

            reference_id = detections[0].tag_id

            reference_data = {
                "reference_id": reference_id,
                "tag_family": TAG_FAMILY
            }

            with open(REFERENCE_FILE, "w") as file:

                json.dump(
                    reference_data,
                    file,
                    indent=4
                )

            reference_saved = True

            print("\nFIRST APRILTAG SAVED!")
            print(f"Reference ID: {reference_id}")


        # Wait for the reference tag to disappear.
        elif reference_saved and not searching_for_match and not match_found:

            if reference_id not in current_ids:

                missing_frames += 1

            else:

                missing_frames = 0

            if missing_frames >= REQUIRED_MISSING_FRAMES:

                searching_for_match = True

                print("\nReference tag has left the camera.")
                print("Searching for the reference AprilTag again...")


        # Search for the reference tag again.
        elif searching_for_match and not match_found:

            if reference_id in current_ids:

                match_found = True

                print("\n!!! APRILTAG MATCH FOUND !!!")
                print(f"Matching AprilTag ID: {reference_id}")

                # Terminal alert on Linux.
                print("\a", end="", flush=True)


        # ----------------------------------------------------
        # DRAW APRILTAG DETECTIONS
        # ----------------------------------------------------

        for tag in detections:

            corners = tag.corners.astype(int)

            center = tuple(
                tag.center.astype(int)
            )

            # Draw AprilTag outline.
            for i in range(4):

                cv2.line(
                    frame,
                    tuple(corners[i]),
                    tuple(corners[(i + 1) % 4]),
                    (255, 0, 0),
                    2
                )

            # Draw AprilTag center.
            cv2.circle(
                frame,
                center,
                5,
                (0, 0, 255),
                -1
            )

            # Display AprilTag ID.
            cv2.putText(
                frame,
                f"ID: {tag.tag_id}",
                (center[0] + 10, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )


        # ====================================================
        # 3. DISPLAY SYSTEM STATUS
        # ====================================================

        if match_found:

            tag_status = f"APRILTAG MATCH FOUND: ID {reference_id}"

        elif searching_for_match:

            tag_status = f"Searching for AprilTag ID {reference_id}"

        elif reference_saved:

            tag_status = f"Reference AprilTag Saved: ID {reference_id}"

        else:

            tag_status = "Waiting for First AprilTag"


        # Green flag status.
        cv2.putText(
            frame,
            flag_status,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 0, 255) if flag_triggered else (255, 255, 255),
            2
        )

        # AprilTag status.
        cv2.putText(
            frame,
            tag_status,
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 255),
            2
        )

        cv2.imshow("Wildcats Vision System", frame)


# ============================================================
# CLEANUP
# ============================================================

finally:

    if camera.poll() is None:

        camera.terminate()

    camera.wait()

    cv2.destroyAllWindows()

    print("Vision system stopped.")
