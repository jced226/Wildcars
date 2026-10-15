
import cv2
import numpy as np

W, H = 640, 480

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

lower_blue = np.array([90, 50, 40])
upper_blue = np.array([130, 255, 255])

previous_position = None
movement_threshold = 10 
notification_cooldown = 0
frame_count = 0

while True:
    ret, frame = cap.read()

    if not ret:
        print("Could not read from camera.")
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    mask = cv2.morphologyEx(
        mask, cv2.MORPH_OPEN,
        np.ones((5, 5), np.uint8)
    )

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest_contour = None
    largest_area = 0

    for contour in contours:
        area = cv2.contourArea(contour)

        if area > largest_area and area > 100:
            largest_area = area
            largest_contour = contour

    status = "No blue detected"

    if largest_contour is not None:
        x, y, w, h = cv2.boundingRect(largest_contour)

        cx = x + w // 2
        cy = y + h // 2

        current_position = (cx, cy)

        cv2.rectangle(
            frame, (x, y), (x + w, y + h),
            (0, 255, 0), 2
        )

        cv2.circle(
            frame, current_position, 6,
            (0, 0, 255), cv2.FILLED
        )

        cv2.putText(
            frame, f"Position: ({cx}, {cy})",
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
            0.7, (0, 255, 0), 2
        )

        if previous_position is not None:
            dx = cx - previous_position[0]
            dy = cy - previous_position[1]

            distance = np.sqrt(dx**2 + dy**2)

            if distance >= movement_threshold:
                status = f"MOVEMENT DETECTED: {distance:.1f} px"

                if notification_cooldown == 0:
                    print(
                        f"Blue moved! "
                        f"Position: ({cx}, {cy}), "
                        f"Movement: {distance:.1f} pixels"
                    )
                    notification_cooldown = 10
            else:
                status = "Blue stationary"

        previous_position = current_position

    else:
        previous_position = None

    if notification_cooldown > 0:
        notification_cooldown -= 1

    
    cv2.putText(
        frame, status, (10, 65),
        cv2.FONT_HERSHEY_SIMPLEX, 0.65,
        (0, 0, 255) if "MOVEMENT" in status
        else (255, 255, 255), 2
    )

    cv2.imshow("Blue Object Tracking", frame)
    cv2.imshow("Blue Detection Mask", mask)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

