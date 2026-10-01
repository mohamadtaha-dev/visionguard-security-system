# 🛡️ VisionGuard

VisionGuard is a Python-based computer vision security system designed for real-time webcam monitoring and intelligent security event detection.

It uses OpenCV and the YuNet face detection model to detect people, monitor presence, trigger security alerts, activate an audio alarm, capture security screenshots, record events, and generate security reports.

## ✨ Features

- 🎥 Real-time webcam monitoring
- 👤 Face detection
- 👁️ Eye detection
- 👥 People counting
- 🚨 Smart security alerts
- 🔊 Audio security alarm
- 📸 Automatic security screenshots
- ⏱️ Presence monitoring
- 📋 Event history and logging
- 📊 Security statistics
- 📈 Real-time security dashboard
- ⚡ Detection stabilization
- 🤖 YuNet AI face detection
- 📄 Automatic security reports

## 🧠 AI Model

VisionGuard uses the **YuNet** face detection model through OpenCV's `FaceDetectorYN` API.

The model provides:

- Face detection
- Face bounding boxes
- Facial landmarks
- Eye landmark positions

Model file:

```text
face_detection_yunet_2026may.onnx