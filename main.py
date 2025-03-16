import sys
import os
import subprocess
import urllib.request
import zipfile
import shutil
import re

from PyQt5 import QtWidgets, QtGui, QtCore

# Custom dark theme stylesheet with black and purple accents
STYLE_SHEET = """
QWidget {
    background-color: #121212;
    color: #e0e0e0;
    font-family: Arial;
}
QPushButton {
    background-color: #5d00ff;
    border: none;
    color: #ffffff;
    padding: 10px;
    border-radius: 5px;
}
QPushButton:hover {
    background-color: #7a33ff;
}
QLineEdit, QComboBox {
    background-color: #1e1e1e;
    border: 1px solid #5d00ff;
    padding: 5px;
    border-radius: 3px;
}
QProgressBar {
    border: 1px solid #5d00ff;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #5d00ff;
    width: 20px;
}
QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #5d00ff;
    border-radius: 3px;
}
QTextEdit {
    background-color: #1e1e1e;
    border: 1px solid #5d00ff;
    border-radius: 3px;
    color: #e0e0e0;
}
"""

def ensure_ffmpeg():
    """
    Ensure that ffmpeg is available locally. If not, download and extract it.
    Returns the path to the ffmpeg executable.
    """
    current_dir = os.getcwd()
    ffmpeg_exe = os.path.join(current_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')
    
    if os.path.exists(ffmpeg_exe):
        print("ffmpeg found.")
        return ffmpeg_exe
    else:
        print("ffmpeg not found, downloading ffmpeg...")
        url = 'https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip'
        zip_filename = 'ffmpeg.zip'
        
        try:
            print("Downloading ffmpeg from:", url)
            urllib.request.urlretrieve(url, zip_filename)
            print("Download complete. Extracting files...")
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Download Error", f"Error downloading ffmpeg: {e}")
            sys.exit(1)
        
        temp_dir = "ffmpeg_temp"
        os.makedirs(temp_dir, exist_ok=True)
        try:
            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Extraction Error", f"Error extracting ffmpeg: {e}")
            sys.exit(1)
        
        try:
            extracted_folders = [f for f in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, f))]
            if not extracted_folders:
                QtWidgets.QMessageBox.critical(None, "Error", "No folder found in the downloaded zip.")
                sys.exit(1)
            folder_name = extracted_folders[0]
            dest_path = os.path.join(current_dir, 'ffmpeg')
            if os.path.exists(dest_path):
                shutil.rmtree(dest_path)
            shutil.move(os.path.join(temp_dir, folder_name), dest_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(None, "Error", f"Error moving ffmpeg files: {e}")
            sys.exit(1)
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            if os.path.exists(zip_filename):
                os.remove(zip_filename)
        
        print("ffmpeg has been installed.")
        return os.path.join(current_dir, 'ffmpeg', 'bin', 'ffmpeg.exe')

class ConversionThread(QtCore.QThread):
    progress_update = QtCore.pyqtSignal(int)
    log_update = QtCore.pyqtSignal(str)
    conversion_finished = QtCore.pyqtSignal()

    def __init__(self, ffmpeg_path, input_files, output_dir, output_format, options):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.input_files = input_files
        self.output_dir = output_dir
        self.output_format = output_format
        self.options = options  # dictionary containing resolution, bitrate, codec, gpu

    def run(self):
        total_files = len(self.input_files)
        for index, input_file in enumerate(self.input_files, start=1):
            basename = os.path.splitext(os.path.basename(input_file))[0]
            output_file = os.path.join(self.output_dir, f"{basename}.{self.output_format}")
            cmd = [self.ffmpeg_path, "-i", input_file]

            # Add advanced options if provided
            if self.options.get("resolution"):
                cmd += ["-s", self.options["resolution"]]
            if self.options.get("bitrate"):
                cmd += ["-b:v", self.options["bitrate"]]
            if self.options.get("codec"):
                cmd += ["-c:v", self.options["codec"]]
            # GPU acceleration (example for NVENC; additional options may be required)
            if self.options.get("gpu") and self.options["gpu"] != "None":
                if self.options["gpu"] == "NVENC":
                    cmd += ["-c:v", "h264_nvenc"]
                # Add other GPU options here

            cmd.append(output_file)

            self.log_update.emit(f"Starting conversion: {input_file} -> {output_file}\nCommand: {' '.join(cmd)}\n")
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
            # Note: Real progress parsing from ffmpeg is nontrivial; here we simulate progress.
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_update.emit(output)
                    # A simple heuristic: try to extract time progress and estimate percent (advanced parsing needed)
                    match = re.search(r'time=(\d+:\d+:\d+\.\d+)', output)
                    if match:
                        # In a real implementation, you'd compare time against the total duration.
                        self.progress_update.emit(int(100 * index / total_files))
            process.wait()
        self.conversion_finished.emit()

class VideoConverter(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ffmpeg_path = ensure_ffmpeg()
        # Ensure ffmpeg bin folder is in PATH for the current session
        os.environ["PATH"] = os.path.join(os.getcwd(), "ffmpeg", "bin") + os.pathsep + os.environ["PATH"]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Advanced Video Converter")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet(STYLE_SHEET)
        
        # Layouts
        main_layout = QtWidgets.QVBoxLayout()
        file_layout = QtWidgets.QHBoxLayout()
        options_layout = QtWidgets.QGridLayout()
        output_layout = QtWidgets.QHBoxLayout()
        log_layout = QtWidgets.QVBoxLayout()

        # Input file list with drag & drop support
        self.file_list = QtWidgets.QListWidget(self)
        self.file_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.file_list.setAcceptDrops(True)
        self.file_list.dragEnterEvent = self.dragEnterEvent
        self.file_list.dropEvent = self.dropEvent
        
        add_btn = QtWidgets.QPushButton("Add Files", self)
        add_btn.clicked.connect(self.add_files)
        clear_btn = QtWidgets.QPushButton("Clear Files", self)
        clear_btn.clicked.connect(self.clear_files)
        file_layout.addWidget(add_btn)
        file_layout.addWidget(clear_btn)

        # Output directory selection
        self.output_dir_line = QtWidgets.QLineEdit(self)
        self.output_dir_line.setPlaceholderText("Select output directory")
        out_btn = QtWidgets.QPushButton("Browse", self)
        out_btn.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.output_dir_line)
        output_layout.addWidget(out_btn)

        # Format selection
        self.format_combo = QtWidgets.QComboBox(self)
        self.format_combo.addItems(["mp4", "avi", "mkv", "mov"])

        # Advanced options
        self.resolution_edit = QtWidgets.QLineEdit(self)
        self.resolution_edit.setPlaceholderText("e.g., 1920x1080")
        self.bitrate_edit = QtWidgets.QLineEdit(self)
        self.bitrate_edit.setPlaceholderText("e.g., 1000k")
        self.codec_combo = QtWidgets.QComboBox(self)
        self.codec_combo.addItems(["libx264", "libx265", "copy"])
        self.gpu_combo = QtWidgets.QComboBox(self)
        self.gpu_combo.addItems(["None", "NVENC"])

        options_layout.addWidget(QtWidgets.QLabel("Output Format:"), 0, 0)
        options_layout.addWidget(self.format_combo, 0, 1)
        options_layout.addWidget(QtWidgets.QLabel("Resolution:"), 1, 0)
        options_layout.addWidget(self.resolution_edit, 1, 1)
        options_layout.addWidget(QtWidgets.QLabel("Bitrate:"), 2, 0)
        options_layout.addWidget(self.bitrate_edit, 2, 1)
        options_layout.addWidget(QtWidgets.QLabel("Codec:"), 3, 0)
        options_layout.addWidget(self.codec_combo, 3, 1)
        options_layout.addWidget(QtWidgets.QLabel("GPU Acceleration:"), 4, 0)
        options_layout.addWidget(self.gpu_combo, 4, 1)

        # Convert button and progress bar
        self.convert_btn = QtWidgets.QPushButton("Convert", self)
        self.convert_btn.clicked.connect(self.start_conversion)
        self.progress_bar = QtWidgets.QProgressBar(self)
        self.progress_bar.setValue(0)

        # Log area
        self.log_area = QtWidgets.QTextEdit(self)
        self.log_area.setReadOnly(True)

        # Assemble main layout
        main_layout.addWidget(QtWidgets.QLabel("Input Files:"))
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(file_layout)
        main_layout.addLayout(output_layout)
        main_layout.addLayout(options_layout)
        main_layout.addWidget(self.convert_btn)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(QtWidgets.QLabel("Log:"))
        main_layout.addWidget(self.log_area)
        self.setLayout(main_layout)

    # Drag and drop handlers for file_list
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.file_list.addItem(file_path)
        event.accept()

    def add_files(self):
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Video Files")
        for f in files:
            self.file_list.addItem(f)

    def clear_files(self):
        self.file_list.clear()

    def browse_output_dir(self):
        dir_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_dir_line.setText(dir_path)

    def start_conversion(self):
        if self.file_list.count() == 0:
            QtWidgets.QMessageBox.warning(self, "No Files", "Please add at least one input file.")
            return
        if not self.output_dir_line.text():
            QtWidgets.QMessageBox.warning(self, "No Output Directory", "Please select an output directory.")
            return

        input_files = [self.file_list.item(i).text() for i in range(self.file_list.count())]
        output_dir = self.output_dir_line.text()
        output_format = self.format_combo.currentText()

        # Gather advanced options
        options = {
            "resolution": self.resolution_edit.text().strip(),
            "bitrate": self.bitrate_edit.text().strip(),
            "codec": self.codec_combo.currentText(),
            "gpu": self.gpu_combo.currentText()
        }

        self.convert_btn.setEnabled(False)
        self.thread = ConversionThread(self.ffmpeg_path, input_files, output_dir, output_format, options)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.log_update.connect(self.update_log)
        self.thread.conversion_finished.connect(self.conversion_done)
        self.thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_log(self, text):
        self.log_area.append(text)

    def conversion_done(self):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        QtWidgets.QMessageBox.information(self, "Conversion Complete", "All files have been converted successfully!")

def main():
    app = QtWidgets.QApplication(sys.argv)
    converter = VideoConverter()
    converter.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
