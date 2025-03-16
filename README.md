# Video Converter

Welcome to Video Converter. This application allows you to easily convert your videos into various formats while offering advanced customization options. With its user-friendly, dark-themed interface built on PyQt5, you can convert your media with precision and efficiency.

## Features

- **Format Conversion:** Convert videos to popular formats like MP4, AVI, MKV, and MOV.
- **Advanced Options:**  
  - **Resolution Adjustment:** Change video resolution (e.g., 1920x1080).
  - **Bitrate Control:** Set custom video bitrate for optimal quality.
  - **Codec Selection:** Choose between different codecs such as libx264, libx265, or copy.
  - **GPU Acceleration:** Enable GPU encoding (e.g., NVENC) for faster conversions.
- **Batch Processing:** Process multiple files simultaneously with ease.
- **Drag-and-Drop Support:** Quickly add files by dragging and dropping them into the application.
- **Real-Time Logging & Progress Updates:** Monitor conversion progress and view detailed logs.
- **Automated ffmpeg Management:** The application checks for ffmpeg on startup and downloads it if necessary, ensuring a smooth setup.

## Download the Executable

You can download a ready-to-run executable (EXE) version of Video Converter from the following link:

[Download Video-Converter.exe](https://github.com/jemmonsss/Video-Converter/releases/download/Video-Converter/Video-Converter.exe)

## How to Run the Application

There are two ways to launch Video Converter:

### 1. Using the Provided Batch File (run.bat)
1. **Download and extract** the Video Converter package.
2. **Double-click** on the `run.bat` file to launch the application.
3. **Follow the on-screen instructions** to add your video files, choose output settings, and start the conversion process.

### 2. Using the Command Line
1. **Open your Command Prompt** and navigate to the folder containing `Video-Converter.exe`.
2. **Run the executable** by typing:
   ```
   Video-Converter.exe
   ```
3. The application’s GUI will launch, allowing you to add files, adjust settings, and convert your videos.

## Usage Instructions

1. **Add Video Files:**  
   Use the "Add Files" button or drag-and-drop your files into the file list.
2. **Select Output Directory:**  
   Choose a folder where the converted files will be saved.
3. **Configure Settings:**  
   - Select the desired output format from the drop-down menu.
   - Optionally, adjust resolution, bitrate, codec, and GPU acceleration settings.
4. **Start Conversion:**  
   Click the "Convert" button to begin. Monitor progress with the progress bar and view detailed logs in the log area.
5. **Completion:**  
   Once the conversion is complete, a notification will appear.

## Additional Information

- **Dependency Management:**  
  The application includes built-in logic to ensure that ffmpeg is installed. If ffmpeg is not found, it will automatically download and install the necessary files.
- **Advanced Customization:**  
  For users who require more control over the conversion process, the application offers several advanced options that can be tailored to meet specific needs.
- **Cross-Platform Considerations:**  
  Although this version is designed for Windows, the code can be adapted for macOS or Linux environments with some modifications.

---
