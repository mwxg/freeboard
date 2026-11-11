import cv2

def main() -> None:
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open webcam")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read a frame")
                break

            # mirror the image so it feels better
            frame = cv2.flip(frame, 1)

            cv2.imshow("Freeboard Camera", frame)

            # q closes preview
            if cv2.waitKey(1) & 0xff == ord("q"):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()