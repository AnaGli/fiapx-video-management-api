import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000",
)

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))

POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "3"))

PROCESSING_TIMEOUT = int(os.getenv("PROCESSING_TIMEOUT", "300"))

CONCURRENT_UPLOADS = int(os.getenv("CONCURRENT_UPLOADS", "10"))

TEST_DATA_DIR = Path(os.getenv("TEST_DATA_DIR", "./test-data"))

TEST_VIDEOS = sorted(
    [
        path
        for path in TEST_DATA_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".mov", ".mp4"}
        and path.name != "invalid-video.mov"
    ]
)


def log(message: str):
    print(f"[TEST] {message}", flush=True)


def success(message: str):
    print(f"[OK] {message}", flush=True)


def fail(message: str):
    print(f"[FAIL] {message}", flush=True)
    sys.exit(1)


def register_user():
    username = f"load_test_{int(time.time())}"
    email = f"{username}@example.com"
    password = "Test@123456"

    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code not in (200, 201):
        fail(f"User registration failed: " f"{response.status_code} - {response.text}")

    return username, password


def login(username: str, password: str):
    response = requests.post(
        f"{API_URL}/auth/login",
        json={
            "username": username,
            "password": password,
        },
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        fail(f"Login failed: " f"{response.status_code} - {response.text}")

    token = response.json().get("access_token")

    if not token:
        fail("Login response does not contain access_token.")

    return token


def upload_video(token: str, video_path: Path):
    with video_path.open("rb") as video_file:
        response = requests.post(
            f"{API_URL}/api/videos",
            headers={
                "Authorization": f"Bearer {token}",
            },
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
        raise RuntimeError(
            f"{video_path.name}: " f"{response.status_code} - {response.text}"
        )

    data = response.json()
    video_id = data.get("id")

    if not video_id:
        raise RuntimeError(f"{video_path.name}: response has no video ID")

    return {
        "video_id": video_id,
        "filename": video_path.name,
    }


def create_load():
    videos = [TEST_VIDEOS[i % len(TEST_VIDEOS)] for i in range(CONCURRENT_UPLOADS)]

    log(f"Starting load test with " f"{len(videos)} concurrent uploads...")

    start = time.time()
    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=CONCURRENT_UPLOADS) as executor:

        futures = {
            executor.submit(
                upload_video,
                TOKEN,
                video,
            ): video
            for video in videos
        }

        for future in as_completed(futures):
            video = futures[future]

            try:
                result = future.result()
                results.append(result)

                success(f"{video.name} uploaded: " f"{result['video_id']}")

            except Exception as exc:
                errors.append(f"{video.name}: {exc}")

    elapsed = time.time() - start

    log(f"Upload phase completed in {elapsed:.2f}s")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")

        fail(f"{len(errors)} uploads failed.")

    if len(results) != CONCURRENT_UPLOADS:
        fail(f"Expected {CONCURRENT_UPLOADS} uploads, " f"got {len(results)}.")

    success(f"All {len(results)} uploads accepted.")

    return results


def wait_for_completion(video_id: str):
    start = time.time()

    while time.time() - start < PROCESSING_TIMEOUT:
        response = requests.get(
            f"{API_URL}/api/videos/{video_id}",
            headers={
                "Authorization": f"Bearer {TOKEN}",
            },
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"{video_id}: " f"{response.status_code} - {response.text}"
            )

        data = response.json()
        status = data.get("status")

        if status == "COMPLETED":
            return data

        if status == "FAILED":
            raise RuntimeError(f"{video_id} failed: " f"{data.get('error_message')}")

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(f"{video_id} did not complete within " f"{PROCESSING_TIMEOUT}s")


def validate_processing(results):
    log(f"Waiting for {len(results)} videos " f"to complete...")

    start = time.time()
    completed = 0
    errors = []

    with ThreadPoolExecutor(max_workers=len(results)) as executor:

        futures = {
            executor.submit(
                wait_for_completion,
                result["video_id"],
            ): result
            for result in results
        }

        for future in as_completed(futures):
            result = futures[future]

            try:
                data = future.result()

                completed += 1

                success(
                    f"{result['filename']} "
                    f"{result['video_id']} "
                    f"COMPLETED - "
                    f"{data.get('frame_count')} frames"
                )

            except Exception as exc:
                errors.append(str(exc))

    elapsed = time.time() - start

    log(f"Processing phase completed in " f"{elapsed:.2f}s")

    if errors:
        for error in errors:
            print(f"[ERROR] {error}")

        fail(f"{len(errors)} videos failed during processing.")

    if completed != len(results):
        fail(f"Expected {len(results)} completed videos, " f"got {completed}.")

    success(f"All {completed} videos processed successfully.")


def main():
    global TOKEN

    print()
    print("=" * 46)
    print(" FIAP X - Load Test")
    print("=" * 46)
    print()
    print(f"API: {API_URL}")
    print(f"Concurrent uploads: {CONCURRENT_UPLOADS}")
    print()

    log("Checking API health...")

    response = requests.get(
        f"{API_URL}/health",
        timeout=REQUEST_TIMEOUT,
    )

    if response.status_code != 200:
        fail(f"API health failed: " f"{response.status_code}")

    success("API is healthy.")

    log("Creating load test user...")

    username, password = register_user()

    TOKEN = login(
        username,
        password,
    )

    success("Load test user authenticated.")

    results = create_load()

    validate_processing(results)

    print()
    print("=" * 46)
    print(" LOAD TEST PASSED")
    print("=" * 46)
    print()
    print(f"Concurrent uploads: {CONCURRENT_UPLOADS}")
    print(f"Videos processed:   {len(results)}")
    print()


if __name__ == "__main__":
    main()
