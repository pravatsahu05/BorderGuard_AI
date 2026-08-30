import os
import cv2
import time


# ============================================================
# BORDERGUARD AI
# BASIC VIDEO PIPELINE
# ============================================================


CAMERA_ID = "CAM-01"


def draw_overlay(frame, fps):
    """
    Add basic surveillance information to a video frame.

    Parameters:
        frame: Current video frame.
        fps: Current processing FPS.

    Returns:
        Frame with surveillance overlay.
    """

    height, width = frame.shape[:2]

    # --------------------------------------------------------
    # Camera information
    # --------------------------------------------------------
    cv2.putText(
        frame,
        f"CAMERA: {CAMERA_ID}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    # --------------------------------------------------------
    # FPS information
    # --------------------------------------------------------
    cv2.putText(
        frame,
        f"FPS: {fps:.2f}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")

    cv2.putText(
        frame, current_time, (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
    )

    # --------------------------------------------------------
    # System status
    # --------------------------------------------------------
    cv2.putText(
        frame,
        "BORDERGUARD AI | SYSTEM ONLINE",
        (20, height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )

    # --------------------------------------------------------
    # Border around frame
    # --------------------------------------------------------
    cv2.rectangle(frame, (5, 5), (width - 5, height - 5), (255, 255, 255), 2)

    return frame


def process_video(video_path):
    """
    Read and process a video frame-by-frame.

    Parameters:
        video_path: Path to the input video.
    """

    # --------------------------------------------------------
    # Open video
    # --------------------------------------------------------
    cap = cv2.VideoCapture(video_path)

    # --------------------------------------------------------
    # Verify that video opened successfully
    # --------------------------------------------------------
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    # --------------------------------------------------------
    # Obtain video properties
    # --------------------------------------------------------
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print("=" * 60)
    print("          BORDERGUARD AI VIDEO PIPELINE")
    print("=" * 60)

    print(f"Camera ID       : {CAMERA_ID}")
    print(f"Video FPS       : {original_fps:.2f}")
    print(f"Resolution      : {frame_width} x {frame_height}")
    print(f"Total Frames    : {total_frames}")
    print("=" * 60)

    # --------------------------------------------------------
    # Create video writer
    # --------------------------------------------------------
    output_path = "outputs/videos/phase2_output.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        original_fps if original_fps > 0 else 25,
        (frame_width, frame_height),
    )

    # --------------------------------------------------------
    # FPS measurement variables
    # --------------------------------------------------------
    frame_count = 0
    start_time = time.time()

    # --------------------------------------------------------
    # Main video-processing loop
    # --------------------------------------------------------
    while True:

        # Read one frame.
        success, frame = cap.read()

        # Stop when there are no more frames.
        if not success:
            break

        frame_count += 1

        # ----------------------------------------------------
        # Calculate processing FPS
        # ----------------------------------------------------
        elapsed_time = time.time() - start_time

        if elapsed_time > 0:
            processing_fps = frame_count / elapsed_time
        else:
            processing_fps = 0

        # ----------------------------------------------------
        # Add BorderGuard overlay
        # ----------------------------------------------------
        frame = draw_overlay(frame, processing_fps)

        # ----------------------------------------------------
        # Save processed frame to output video
        # ----------------------------------------------------
        writer.write(frame)

        # ----------------------------------------------------
        # Display frame
        # ----------------------------------------------------
        cv2.imshow("BorderGuard AI - Camera Feed", frame)

        # ----------------------------------------------------
        # Press Q to exit
        # ----------------------------------------------------
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Video processing stopped by user.")
            break

    # --------------------------------------------------------
    # Cleanup
    # --------------------------------------------------------
    cap.release()
    writer.release()
    cv2.destroyAllWindows()

    print("=" * 60)
    print("Video processing completed.")
    print(f"Processed frames : {frame_count}")
    print(f"Output video     : {output_path}")
    print("=" * 60)


if __name__ == "__main__":

    # Change this path to your actual input video.
    VIDEO_PATH = "data/simulation/sample.mp4"

    process_video(VIDEO_PATH)
