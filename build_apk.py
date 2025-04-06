import subprocess
import os
import shutil
from pathlib import Path

def build_apk(
    docker_image="buildozer-docker",
    source_dir="kivy_app",
    output_dir="build_output"
):
    source_path = Path(source_dir).resolve()
    output_path = Path(output_dir).resolve()

    print(f"📦 Building Docker image: {docker_image}")
    subprocess.run(["docker", "build", "-t", docker_image, "."], check=True)

    print(f"⚙️ Running Buildozer in Docker...")
    subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{source_path}:/app",
        "-w", "/app",
        docker_image,
        "buildozer", "-v", "android", "debug"
    ], check=True)

    # Copy APK from /bin
    apk_path = source_path / "bin"
    if apk_path.exists():
        output_path.mkdir(parents=True, exist_ok=True)
        for file in apk_path.glob("*.apk"):
            shutil.copy(file, output_path)
            print(f"✅ APK copied to: {output_path / file.name}")
    else:
        print("❌ APK build failed — no /bin directory found.")

if __name__ == "__main__":
    build_apk()
