# 🃏 Custom Dobble Generator

| ![alt text](https://raw.githubusercontent.com/campio97/dobble-generator/refs/heads/main/docs/gui.png "Frontend GUI") | ![alt text](https://raw.githubusercontent.com/campio97/dobble-generator/refs/heads/main/docs/pdf.png "PDF Example") |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |

> **Create your own "Spot It\!" style matching card games using your personal images.**

## 📖 Overview

**Dobble Generator** is a desktop application that allows you to generate printable PDF cards for the popular game mechanics found in _Dobble_ (also known as _Spot It\!_).

Simply point the application to a folder containing images, and it will mathematically construct a deck where **every single card shares exactly one symbol** with every other card.

## ✨ Key Features

- **Modern GUI:** Built with `customtkinter` for a sleek, dark-mode friendly interface.

- **Smart Image Processing:**

- Automatically removes white/near-white backgrounds from images.

- Resizes images maintaining aspect ratio.

- Optional random rotation (±30°) for added difficulty.

- **Mathematical Precision:** Uses Finite Projective Plane logic to ensure perfect game balance.

- **Print-Ready Output:** Generates a formatted A4 PDF containing all cards.

## 📥 Installation

You can run this application by downloading the pre-built version or by running the source code.

### Method 1: 📦 Pre-compiled Release (Recommended)

Use this method if you want to play without installing Python.

1. Navigate to the [releases](https://github.com/campio97/dobble-generator/releases) page of this repository.

2. Download the executable for your operating system.

3. Extract the archive and run `DobbleGenerator.exe`.

### Method 2: 🐍 Build from Source (For Developers)

Use this method if you want to modify the code.

**Prerequisites:**

- Python 3.8 or higher.

**Steps:**

1.  **Clone the repository:**

```bash

git clone https://github.com/campio97/dobble-generator.git

cd dobble-generator

```

2.  **Install dependencies:**

```bash

pip install -r requirements.txt

```

3.  **Run the application:**

```bash

python dobble_generator_gui.py

```

## 🚀 How to Use

1.  **Prepare Images:** Gather your images (JPG/PNG) in a single folder.

- _Tip:_ Simple icons with white backgrounds work best.

2.  **Select Folder:** Open the app, click **"Browse..."**, and select your folder.

3.  **Check Requirements:** The app counts your images. Ensure you have enough images for your desired deck size (see the Math table below).

4.  **Configure:** Check **"Random Rotation"** if you want tilted symbols.

5.  **Generate:** Click **"Generate PDF"**.

6.  **Output:**

- `dobble_cards.pdf`: The printable sheet.

- `card_x.png`: Individual image files for each card (saved in your folder).

## 📐 The Math & Requirements

The game logic relies on **Finite Projective Planes**. To create a valid deck, you need a specific minimum number of images.

The algorithm uses the formula: $Total Symbols = S^2 - S + 1$ (where $S$ is symbols per card).

| Desired Symbols per Card | Minimum Images Required | Total Cards Generated |
| ------------------------ | ----------------------- | --------------------- |
| **3**                    | 7                       | 7                     |
| **4**                    | 13                      | 13                    |
| **5**                    | 21                      | 21                    |
| **6**                    | 31                      | 31                    |
| **7**                    | 43                      | 43                    |
| **8**                    | 57                      | 67                    |

_Note: If you provide 35 images, the app will use the "6 Symbols" setting (requiring 31 images) and ignore the extra 4._

## 🤝 Contributing

Contributions are welcome\! Please feel free to submit a Pull Request.

1. Fork the project

2. Create your feature branch (`git checkout -b feature/NewFeature`)

3. Commit your changes (`git commit -m 'Add NewFeature'`)

4. Push to the branch (`git push origin feature/NewFeature`)

5. Open a Pull Request
