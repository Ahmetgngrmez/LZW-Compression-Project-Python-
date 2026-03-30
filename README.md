# LZW Compression Project 🗜️

Hi there! 👋 Welcome to my LZW Compression tool. 

I built this project to explore how file compression works under the hood. It uses the **Lempel-Ziv-Welch (LZW)** algorithm to shrink down files intelligently without losing any data. 

### ✨ What can it do?
* **Compresses Texts & Images:** It doesn't just work on standard text files; you can compress images too!
* **Adjustable Levels:** You can choose how hard you want the algorithm to work (from Level 1 up to Level 6).
* **Easy-to-Use GUI:** You don't need to be a terminal wizard to use it. It comes with a simple, click-and-go visual interface.

### 🛠️ How to run it?
You just need a few standard Python libraries to get started. Open your terminal and run:

`pip install numpy pillow pyqt5`

After that, simply run the GUI file (`LZW_Level6_GUI.py`), select your file from the screen, and let the app do the rest!

### 📂 A quick look at the files
* `LZW.py` to `LZW_Level5.py`: The core algorithm getting smarter step by step.
* `LZW_Level6_GUI.py`: The main application with the visual interface.
* `image_tools.py`: A little helper that processes images.

Feel free to explore the code or try compressing some files yourself!