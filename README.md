# CSV Cleaner GUI

A desktop Python app to clean messy CSV and Excel files - no code required.
Built with Tkinter and Pandas. Designed for data analysts and non-technical clients.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat)
![Pandas](https://img.shields.io/badge/Pandas-2.0-orange?style=flat)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green?style=flat)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat)

---

## Screenshot

Add a screenshot or demo GIF here after running the app.

---

## What It Does

- Removes duplicate rows automatically
- Fills missing values - choose Median, Mean, or a fixed value per column
- Detects and handles outliers using IQR (interquartile range) method
- Previews the cleaned data before saving
- Exports as a new clean CSV file

---

## Install

```bash
git clone https://github.com/BrightNodeAI/csv-cleaner-gui.git
cd csv-cleaner-gui
pip install pandas numpy
python csv_cleaner_gui.py
```

---

## Usage

1. Click Browse to select your messy CSV file
2. Choose a fill strategy for missing values: Median, Mean, or Custom
3. Choose outlier handling: Remove, Cap, or Ignore
4. Click Preview to see the cleaned result
5. Click Save As to export the cleaned file

---

## Project Structure

```
csv-cleaner-gui/
    csv_cleaner_gui.py      - Main application (Tkinter UI + logic)
    cleaner.py              - Core cleaning functions (Pandas)
    requirements.txt        - pip dependencies
    screenshot.png          - App screenshot
    README.md
```

---

## Requirements

```
pandas>=1.5.0
numpy>=1.23.0
```

---

## Skills Demonstrated

Python, Pandas, NumPy, Tkinter, IQR outlier detection, argparse, GUI development, data cleaning

---

## Freelance Applications

This type of tool is used in:

- E-commerce product catalogue cleaning
- HR data preprocessing before analysis
- Survey data preparation for reporting
- Finance reconciliation workflows

---

Built by [BrightNode AI](https://www.freelancer.pk/u/BrightNodeAI) - Python Data Science and AI specialists
