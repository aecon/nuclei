# Nuclei Quantification

Counts nuclei in fluorescently labeled cell culture images using [StarDist](https://github.com/stardist/stardist).

**Important**: Plate folders should only contain nuclei images. Other channels will be incorrectly segmented.


## 1. Download

1. Using the File Explorer, navigate to the folder where you want to download the code (e.g. your home folder or Desktop).
2. Right-click on an empty area in the File Explorer window and select **Open in Terminal** (Linux).
3. In the terminal that opens, type the following and press Enter:

```bash
git clone https://github.com/aecon/nuclei.git
```

This will create a new folder called `nuclei` containing the code.


## 2. Install

1. In the same terminal, enter the `nuclei` folder:

```bash
cd nuclei
```

2. Create a new Python environment (this keeps the required packages separate from your other projects):

```bash
conda create -n nuclei python=3.11 -y
```

3. Activate the environment:

```bash
conda activate nuclei
```

You should see `(nuclei)` at the beginning of your terminal line.

4. Install the required packages:

```bash
pip install -r requirements.txt
```

This step may take a few minutes.


## 3. Usage

Every time you want to run the analysis:

1. Using the File Explorer, navigate into the `nuclei` folder (the one you downloaded in step 1).
2. Right-click on an empty area in the File Explorer window and select **Open in Terminal** (Linux).
3. Activate the environment:

```bash
conda activate nuclei
```

4. Start the application:

```bash
python gui.py
```

A browser window will open with the application. From there:

- Click **Browse** and select the folder that contains your plate folders.
- Optionally check **Skip already processed images** to resume an interrupted run.
- Click **Run** to start the analysis.


## 4. Output

- **CSV files** (`counts_*.csv`) are saved in the plates folder, with nuclei counts per image.
- **Label images** are saved in a `labels/` subfolder next to each original image.

CSV files are regenerated from scratch on every run. When "Skip already processed images" is checked, images with existing label files are not re-segmented — their counts are read from the saved labels.
