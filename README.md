# Automated Video Editor

Automated Video Editor simplifies the process of video editing by using a mix of frame analysis and audio signal processing. This tool intelligently detects key moments in a video based on visual markers and audio amplitudes, then trims and compiles these moments into a cohesive final video. Ideal for creating highlights, skipping silence, or streamlining lengthy footage.

## Features

- **Automatic Frame Detection**: Uses OpenCV to identify start, end, and clear points in video frames based on customizable colors and positions.
- **Audio-Driven Edits**: Applies Librosa to analyze audio amplitude, marking segments for trimming or inclusion based on predefined thresholds.
- **Flexible Video Format Support**: Compatible with various video formats (MP4, MKV, AVI, MOV, FLV).
- **Efficient Video Compilation**: Uses MoviePy to concatenate video subclips into a smoothly edited final output.
- **Configurable Parameters**: Customize frame buffer, audio thresholds, and frame connection limits for tailored video edits.

## Setup

1. **Install Required Libraries**:
    ```bash
    pip install tkinter moviepy opencv-python librosa
    ```

2. **Run the Editor**:
    ```bash
    python autoEditor.py
    ```
    *A file dialog will prompt you to select a video file to process.*

## Usage

1. **Frame and Color Settings**:  
   Adjust frame-based parameters to define keyframes, including `START_COLOUR`, `END_COLOUR`, `CLEAR_COLOUR`, and verification color coordinates.

2. **Audio Analysis Settings**:  
   - `AMPLITUDE_THRESHOLD`: Minimum amplitude level for detecting audio activity.
   - `CLIP_BEGINNING_FRAME_BUFFER` and `CLIP_ENDING_FRAME_BUFFER`: Extend or contract detected frames to adjust cut-in or cut-out timing.

3. **Render Options**:  
   Customize FPS (`FPS`) and output paths (`OUTPUT_VIDEO_NAME`, `OUTPUT_AUDIO_NAME`) to control output quality and location.

## Example Workflow

1. The script analyzes the chosen video to find keyframes based on frame colors and positions.
2. Extracts audio and evaluates amplitude per frame to locate sound-based cuts.
3. Compiles marked frames into a final, edited video file in the specified output directory.

## File Structure

- **`temp/`**: Intermediate files for video (`video.mp4`) and audio (`audio.wav`) storage.
- **`output/`**: Final edited files with video (`output.mp4`) and audio (`output.wav`) results.

## Requirements

- Python 3.6+

## Notes
- Adjusting threshold values can help better capture specific video scenes or silence.
