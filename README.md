# Team Robosky

# Sketch to PCB Converter

This project aims to automate the process of converting hand-drawn circuit diagrams into PCB (Printed Circuit Board) layouts. By leveraging the YOLOv4 object detection model, the system can identify circuit components and connections in hand-drawn images and generate a machine-readable format for PCB design.

---

## Features

- **Circuit Component Detection**: Uses YOLOv4 to identify components like resistors, capacitors, diodes, etc.
- **Image Processing**: Supports `.jpg` and `.bmp` formats for hand-drawn circuit images.
- **Component Annotation**: Outputs the detected components and their confidence levels.
- **PCB Layout Generation**: Provides the detected components in a structured format to aid in PCB design.

---

## Prerequisites

Ensure the following software and libraries are installed:

- Python 3.7+
- Google Colab (or local GPU setup with CUDA)
- OpenCV
- TensorFlow (for GPU verification)
- Darknet (compiled with GPU and OpenCV support)

---

## Setup

### Clone Repository

```bash
git clone https://github.com/Lawan-Poudyal/Robosky.git
cd Robosky
```
