import io
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

import boto3
import requests

# ============================================================
# Configuration
# ============================================================
K8S_MODE = False
REQUEST_TIMEOUT = 10

API_URL = "http://host.docker.internal:8000"

S3_ENDPOINT = "http://host.docker.internal:4566"
K8S_MODE = os.getenv("K8S_MODE", "true").lower() in ("1", "true", "yes")
K8S_NAMESPACE = os.getenv("K8S_NAMESPACE", "default")
K8S_INFRA_NAMESPACE = os.getenv("K8S_INFRA_NAMESPACE", "video-infra")

API_PORT = int(os.getenv("API_PORT", "8000"))
S3_PORT = int(os.getenv("S3_PORT", "4566"))

API_URL = os.getenv("API_URL", f"http://127.0.0.1:{API_PORT}")
S3_ENDPOINT = os.getenv("S3_ENDPOINT_URL", f"http://127.0.0.1:{S3_PORT}")

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY_ID", "test")
S3_SECRET_KEY = os.getenv("S3_SECRET_ACCESS_KEY", "test")
S3_REGION = os.getenv("S3_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "videos")

TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "180"))
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "3"))

TEST_DATA_DIR = Path(os.getenv("TEST_DATA_DIR", "./test-data"))

TEST_VIDEOS = [
    TEST_DATA_DIR / "video-1.mov",
    TEST_DATA_DIR / "video-2.mov",
]

TEST_PASSWORD = os.getenv("TEST_PASSWORD", "Test@123456")

_port_forward_processes = []

# ============================================================
# Helpers
# ============================================================


def log(message: str):
    print(f"\n[TEST] {message}")


def success(message: str):
    print(f"[OK] {message}")


def fail(message: str):
    print(f"\n[FAIL] {message}")
    sys.exit(1)


def start_port_forward(namespace, service, local_port, remote_port):
    log(
        f"Starting port-forward: {namespace}/svc/{service} "
        f"{local_port}:{remote_port}"
    )

    process = subprocess.Popen(
        [
            "kubectl",
            "port-forward",
            "-n",
            namespace,
            f"svc/{service}",
            f"{local_port}:{remote_port}",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    _port_forward_processes.append(process)

    deadline = time.time() + 10
    while time.time() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr else ""
            fail(f"Could not start port-forward for {service}: " f"{stderr.strip()}")

        try:
            import socket

            with socket.create_connection(("127.0.0.1", local_port), timeout=0.5):
                success(f"Port-forward ready: localhost:{local_port}")
                return
        except OSError:
            time.sleep(0.5)

    fail(f"Timeout starting port-forward for {service}.")


def stop_port_forwards():
    for process in _port_forward_processes:
        if process.poll() is None:
            process.terminate()

    for process in _port_forward_processes:
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()


def setup_environment():
    if not K8S_MODE:
        return

    log("Kubernetes mode enabled.")

    start_port_forward(
        K8S_NAMESPACE,
        "video-management-api",
        API_PORT,
        8000,
    )

    start_port_forward(
        K8S_INFRA_NAMESPACE,
        "localstack",
        S3_PORT,
        4566,
    )


def create_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=S3_ENDPOINT,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_KEY,
        region_name=S3_REGION,
    )


# ============================================================
# Infrastructure checks
# ============================================================


def check_api():
    log("Checking API health...")

    response = requests.get(
        f"{API_URL}/health",
        timeout=10,
    )

    if response.status_code != 200:
        fail(f"API health check failed: " f"{response.status_code} " f"{response.text}")

    success(f"API is healthy: {response.json()}")


def ensure_bucket(s3):
    log(f"Checking S3 bucket: {S3_BUCKET}")

    try:
        s3.head_bucket(Bucket=S3_BUCKET)

        success("S3 bucket exists.")

    except Exception:
        log("Bucket does not exist. Creating it...")

        s3.create_bucket(Bucket=S3_BUCKET)

        success("S3 bucket created.")


# ============================================================
# Test data
# ============================================================


def validate_test_videos():
    log("Checking test videos...")

    for video in TEST_VIDEOS:

        if not video.exists():
            fail(f"Test video not found: {video}")

        if video.stat().st_size == 0:
            fail(f"Test video is empty: {video}")

        success(f"{video.name}: " f"{video.stat().st_size} bytes")


# ============================================================
# Authentication
# ============================================================


def register_user():
    username = f"test_{int(time.time())}"
    email = f"{username}@example.com"
    password = "Test@123456"

    log(f"Creating test user: {username}")

    payload = {
        "username": username,
        "email": email,
        "password": password,
    }

    response = requests.post(
        f"{API_URL}/auth/register",
        json=payload,
        timeout=10,
    )

    if response.status_code not in (200, 201):
        fail(
            f"User registration failed: " f"{response.status_code} " f"{response.text}"
        )

    success("Test user created.")

    return username, password


def login(
    username: str,
    password: str,
):
    payload = {
        "username": username,
        "password": password,
    }

    response = requests.post(
        f"{API_URL}/auth/login",
        json=payload,
        timeout=10,
    )

    if response.status_code != 200:
        fail(f"Login failed: " f"{response.status_code} " f"{response.text}")

    data = response.json()

    token = data.get("access_token")

    if not token:
        fail("Login response does not contain " f"access_token: {data}")

    success("Login successful.")

    return token


# ============================================================
# Upload
# ============================================================


def upload_video(
    token: str,
    video_path: Path,
):
    log(f"Uploading {video_path.name}...")

    headers = {
        "Authorization": f"Bearer {token}",
    }

    with video_path.open("rb") as video_file:

        import mimetypes

        content_type = (
            mimetypes.guess_type(video_path.name)[0] or "application/octet-stream"
        )

        files = {
            "file": (
                video_path.name,
                video_file,
                content_type,
            )
        }

        response = requests.post(
            f"{API_URL}/api/videos",
            headers=headers,
            files=files,
            timeout=60,
        )

    if response.status_code not in (
        200,
        201,
    ):
        fail(
            f"Upload failed for "
            f"{video_path.name}: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    video_id = data.get("id")

    if not video_id:
        fail("Upload response does not contain " f"video id: {data}")

    success(f"{video_path.name} uploaded. " f"Video ID: {video_id}")

    return {
        "video_id": video_id,
        "filename": video_path.name,
        "response": data,
    }


def upload_all_videos(token: str):
    """
    Upload all videos before waiting for any result.
    This verifies that multiple requests can be
    submitted to the processing queue.
    """

    log(f"Uploading {len(TEST_VIDEOS)} videos...")

    uploads = []

    for video_path in TEST_VIDEOS:

        result = upload_video(
            token,
            video_path,
        )

        uploads.append(result)

    return uploads


def upload_invalid_video(
    token: str,
    video_path: Path,
):
    log("Uploading invalid video to trigger processing failure...")

    with video_path.open("rb") as video_file:
        response = requests.post(
            f"{API_URL}/api/videos",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "file": (
                    video_path.name,
                    video_file,
                    "video/quicktime",
                )
            },
            timeout=REQUEST_TIMEOUT,
        )

    if response.status_code != 201:
        fail(
            f"Invalid video upload failed: " f"{response.status_code} - {response.text}"
        )

    data = response.json()
    video_id = data.get("id")

    if not video_id:
        fail(f"Invalid video upload response does not contain " f"video ID: {data}")

    success(f"Invalid video uploaded. Video ID: {video_id}")

    return video_id


def wait_for_failed_status(
    token: str,
    video_id: str,
    timeout: int = 60,
):
    log("Waiting for video processing failure...")

    start = time.time()

    while time.time() - start < timeout:
        response = requests.get(
            f"{API_URL}/api/videos/{video_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            fail(
                f"Failed to get video status: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()
        current_status = data.get("status")

        if current_status in ("FAILED", "failed"):
            error_message = data.get("error_message")

            if not error_message:
                fail("Video reached FAILED status but " "error_message is empty.")

            success(f"Video failed as expected. " f"Error: {error_message}")

            return data

        time.sleep(POLL_INTERVAL)

    fail(
        f"Video did not reach FAILED status within {timeout}s. "
        f"Last status: {current_status}"
    )


def validate_video_list(token: str, expected_video_ids: list[str]):
    log("Validating video list...")

    response = requests.get(
        f"{API_URL}/api/videos/",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )

    if response.status_code != 200:
        fail(f"Video list failed: " f"{response.status_code} - {response.text}")

    data = response.json()

    items = data.get("items", [])
    total = data.get("total")

    returned_ids = {item["id"] for item in items}

    expected_ids = set(expected_video_ids)

    if not expected_ids.issubset(returned_ids):
        fail(
            "Video list does not contain all uploaded videos. "
            f"Expected: {expected_ids}, "
            f"Returned: {returned_ids}"
        )

    if total is None:
        fail("Video list response does not contain 'total'.")

    success(
        f"Video list OK. "
        f"Total: {total}. "
        f"Uploaded videos found: {len(expected_ids)}"
    )


def validate_video_details(token: str, uploads: list[dict]):
    log("Validating video details...")

    for upload in uploads:
        video_id = upload["video_id"]
        filename = upload["filename"]

        response = requests.get(
            f"{API_URL}/api/videos/{video_id}",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            fail(
                f"Video detail failed for {filename}: "
                f"{response.status_code} - {response.text}"
            )

        data = response.json()

        if data.get("id") != video_id:
            fail(f"Wrong video ID returned for {filename}: " f"{data.get('id')}")

        if data.get("original_filename") != filename:
            fail(
                f"Wrong filename returned for {filename}: "
                f"{data.get('original_filename')}"
            )

        if data.get("status") not in ("COMPLETED", "completed"):
            fail(f"Unexpected status for {filename}: " f"{data.get('status')}")

        if data.get("frame_count") != 171:
            fail(
                f"Unexpected frame count for {filename}: " f"{data.get('frame_count')}"
            )

    success(f"Video details OK for {len(uploads)} videos.")


def validate_video_download(token: str, uploads: list[dict]):
    log("Validating video downloads...")

    for upload in uploads:
        video_id = upload["video_id"]
        filename = upload["filename"]

        response = requests.get(
            f"{API_URL}/api/videos/{video_id}/download",
            headers={"Authorization": f"Bearer {token}"},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            fail(
                f"Video download failed for {filename}: "
                f"{response.status_code} - {response.text}"
            )

        content_type = response.headers.get("Content-Type", "")

        if "application/zip" not in content_type:
            fail(f"Unexpected content type for {filename}: " f"{content_type}")

        if not response.content:
            fail(f"Downloaded file is empty for {filename}")

        try:
            with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                frames = [
                    name
                    for name in zip_file.namelist()
                    if name.lower().endswith(".jpg")
                ]

                if not frames:
                    fail(f"Downloaded ZIP contains no JPG frames " f"for {filename}")

        except zipfile.BadZipFile:
            fail(f"Downloaded file is not a valid ZIP for {filename}")

        success(
            f"{filename}: download OK, "
            f"{len(frames)} frames, "
            f"{len(response.content)} bytes."
        )


def validate_user_isolation(
    owner_token: str,
    other_user_token: str,
    video_id: str,
):
    log("Validating user video isolation...")

    # Owner must be able to access the video
    response = requests.get(
        f"{API_URL}/api/videos/{video_id}",
        headers={"Authorization": f"Bearer {owner_token}"},
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        fail(
            f"Video owner cannot access own video: "
            f"{response.status_code} - {response.text}"
        )

    success("Video owner can access the video.")

    # Another user must NOT be able to access it
    response = requests.get(
        f"{API_URL}/api/videos/{video_id}",
        headers={"Authorization": f"Bearer {other_user_token}"},
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 404:
        fail(
            f"Video isolation failed. "
            f"Expected 404 for another user, "
            f"got {response.status_code}: {response.text}"
        )

    success("Other user cannot access the video.")


# ============================================================
# S3 validation
# ============================================================


def check_input_object(
    s3,
    video_id: str,
    filename: str,
):
    log(f"Checking input object for " f"{filename}...")

    prefix = f"videos/{video_id}/input/"

    response = s3.list_objects_v2(
        Bucket=S3_BUCKET,
        Prefix=prefix,
    )

    objects = response.get(
        "Contents",
        [],
    )

    if not objects:
        fail(f"No input object found for " f"video {video_id}")

    for obj in objects:
        success(f"Input object found: " f"{obj['Key']} " f"({obj['Size']} bytes)")

    return objects[0]["Key"]


def wait_for_output(
    s3,
    video_id: str,
    filename: str,
):
    output_key = f"videos/{video_id}/output/frames.zip"

    log(f"Waiting for output of " f"{filename}...")

    start = time.time()

    while time.time() - start < TIMEOUT_SECONDS:

        try:

            response = s3.head_object(
                Bucket=S3_BUCKET,
                Key=output_key,
            )

            size = response["ContentLength"]

            if size > 0:

                elapsed = time.time() - start

                success(
                    f"Output found for "
                    f"{filename}: "
                    f"{output_key} "
                    f"({size} bytes) "
                    f"in {elapsed:.1f}s"
                )

                return output_key

        except Exception:
            pass

        elapsed = int(time.time() - start)

        print(
            f"  {filename}: " f"waiting... " f"{elapsed}s / " f"{TIMEOUT_SECONDS}s",
            end="\r",
        )

        time.sleep(POLL_INTERVAL)

    fail(
        f"Worker did not generate output "
        f"for {filename} within "
        f"{TIMEOUT_SECONDS} seconds."
    )


# ============================================================
# ZIP validation
# ============================================================


def validate_output_zip(
    s3,
    output_key: str,
    filename: str,
):
    log(f"Downloading output for " f"{filename}...")

    response = s3.get_object(
        Bucket=S3_BUCKET,
        Key=output_key,
    )

    content = response["Body"].read()

    if not content:
        fail(f"Output ZIP is empty for " f"{filename}.")

    try:

        with zipfile.ZipFile(
            io.BytesIO(content),
            "r",
        ) as archive:

            files = archive.namelist()

            frame_files = [name for name in files if name.lower().endswith(".jpg")]

            if not frame_files:
                fail(f"ZIP for {filename} " "contains no JPG frames.")

            success(f"{filename}: ZIP valid, " f"{len(frame_files)} frames.")

            return len(frame_files)

    except zipfile.BadZipFile:

        fail(f"Output for {filename} " "is not a valid ZIP file.")


# ============================================================
# Main
# ============================================================


def main():
    print(
        "\n"
        "==============================================\n"
        " FIAP X - Full Video Processing Flow Test\n"
        "=============================================="
    )

    print(f"\nAPI:       {API_URL}")
    print(f"S3:        {S3_ENDPOINT}")
    print(f"S3 Bucket: {S3_BUCKET}")
    print(f"K8S Mode:  {K8S_MODE}")

    try:
        setup_environment()

        check_api()

        s3 = create_s3_client()
        ensure_bucket(s3)

        validate_test_videos()

        username, password = register_user()
        token = login(username=username, password=password)
        other_username, other_password = register_user()

        other_token = login(
            username=other_username,
            password=other_password,
        )

        start_time = time.time()

        uploads = upload_all_videos(token)
        validate_video_list(
            token,
            [upload["video_id"] for upload in uploads],
        )

        log("Validating input objects in S3...")
        for upload in uploads:
            check_input_object(
                s3=s3,
                video_id=upload["video_id"],
                filename=upload["filename"],
            )

        results = []
        for upload in uploads:
            output_key = wait_for_output(
                s3=s3,
                video_id=upload["video_id"],
                filename=upload["filename"],
            )

            frame_count = validate_output_zip(
                s3=s3,
                output_key=output_key,
                filename=upload["filename"],
            )

            results.append(
                {
                    "filename": upload["filename"],
                    "video_id": upload["video_id"],
                    "output_key": output_key,
                    "frame_count": frame_count,
                }
            )
        invalid_video = Path(TEST_DATA_DIR) / "invalid-video.mov"

        invalid_video_id = upload_invalid_video(
            token,
            invalid_video,
        )

        wait_for_failed_status(
            token,
            invalid_video_id,
        )
        validate_video_details(token, uploads)

        validate_video_download(token, uploads)
        validate_user_isolation(
            owner_token=token,
            other_user_token=other_token,
            video_id=uploads[0]["video_id"],
        )

        total_time = time.time() - start_time

        print(
            "\n"
            "==============================================\n"
            " FLOW TEST PASSED\n"
            "=============================================="
        )
        print(f"\nTotal processing flow: {total_time:.1f}s")
        print(f"Videos processed: {len(results)}")
        print("\nResults:")

        for result in results:
            print(f"\n  Video: {result['filename']}")
            print(f"  ID: {result['video_id']}")
            print(f"  Output: {result['output_key']}")
            print(f"  Frames: {result['frame_count']}")

    finally:
        if K8S_MODE:
            log("Stopping Kubernetes port-forwards...")
            stop_port_forwards()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[TEST] Test interrupted.")
        stop_port_forwards()
        sys.exit(130)
