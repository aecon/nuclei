# Nuclei Quantification

Counts the number of nuclei in fluorescently labeled cell culture images using [StarDist](https://github.com/stardist/stardist) for segmentation.

**Important**: The plate folders should only contain nuclei images. If they contain additional channels, those will be incorrectly segmented as nuclei.


## Installation

### 1. Clone this repository

Open a terminal and navigate to the folder where you want to download the code. Then run:

```bash
git clone https://github.com/aecon/nuclei.git
cd nuclei
```

### 2. Create a conda environment

This creates a new Python environment called `nuclei` so that the required packages don't interfere with your other projects:

```bash
conda create -n nuclei python=3.11 -y
```

### 3. Activate the environment

```bash
conda activate nuclei
```

You should see `(nuclei)` appear at the beginning of your terminal prompt. This means the environment is active.

### 4. Install the required packages

This installs all dependencies including GPU support (CUDA/cuDNN) automatically:

```bash
pip install -r requirements.txt
```

To verify that your GPU is detected, run:

```bash
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```

If successful, you should see something like:

```
[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU')]
```

If the list is empty (`[]`), the code will still work but will run on the CPU (slower).


## Usage

### 1. Set the input folder

Open `main.py` in a text editor and change the `basedir` variable to point to the folder that contains your plate folders:

```python
basedir = '/path/to/your/plates/folder'
```

Save the file.

### 2. Run the analysis

Open a terminal, navigate to the `nuclei/` folder, activate the environment, and run the script:

```bash
conda activate nuclei
python main.py
```

### 3. Output

The script will:
- Process all `.tif` images found inside `basedir` (including subfolders).
- Print progress to the terminal (e.g., `Processing image 1/100: ...`).
- Save a `labels/` folder next to each image, containing the segmentation masks.
- Save `.csv` files in `basedir` with nuclei counts per image.
