# Brain Blitz Mobile — Android project

A premium dark-themed arithmetic game built with Python + Kivy.

## Included
- Quick Play (3 lives)
- 60-Second Rush
- Survival (3 lives)
- Addition, subtraction, multiplication and division
- Progressive difficulty
- Score, streak, accuracy and local personal-best storage
- Portrait-friendly touch interface

## Run on desktop
Python 3.10+ recommended.

```bash
python -m pip install kivy
python main.py
```

## Build an Android APK (recommended: Ubuntu 22.04 / WSL2)
Buildozer uses Android SDK/NDK and is most reliable on Linux.

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv git zip unzip \
  openjdk-17-jdk autoconf libtool pkg-config \
  zlib1g-dev libncurses5-dev libncursesw5-dev \
  libtinfo6 cmake libffi-dev libssl-dev

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython

buildozer android debug
```

The first build downloads Android build dependencies and can take a while.
The APK will be created under `bin/`.

To install to a connected Android phone with USB debugging enabled:

```bash
buildozer android deploy run
```

## Project files
- `main.py`: game and UI
- `buildozer.spec`: Android packaging configuration

## Notes
- Personal best is stored locally on the device using Kivy JsonStore.
- This is the first playable mobile build. It does not require a server or account.


## Build APK automatically with GitHub Actions (Windows-friendly)

1. Create a GitHub repository and upload the project files, including the hidden
   `.github/workflows/build-android.yml` file.
2. Push the files to the `main` branch. GitHub Actions will start the APK build.
3. Open the repository's **Actions** tab and select the latest
   **Build Brain Blitz Android APK** run.
4. When it succeeds, download the `brain-blitz-android-apk` artifact.

You can also start a build manually from **Actions → Build Brain Blitz Android APK
→ Run workflow**. The build runs on a GitHub-hosted Ubuntu runner; Ubuntu is not
installed on your Windows laptop.

For a private repository, GitHub Actions usage is subject to your account's
included minutes and storage limits. Never commit passwords, signing keys, or
personal access tokens to the repository.
