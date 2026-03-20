# Nuclei Quantification

Counts nuclei in fluorescently labeled cell culture images using [StarDist](https://github.com/stardist/stardist).

**Important**: Plate folders should only contain nuclei images. Other channels will be incorrectly segmented.


## Installation

```bash
git clone https://github.com/aecon/nuclei.git
cd nuclei
conda create -n nuclei python=3.11 -y
conda activate nuclei
pip install -r requirements.txt
```

To verify GPU support: `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`


## Usage

### GUI (recommended)

```bash
conda activate nuclei
python gui.py
```

A browser window will open. Select your plates folder, optionally check "Skip already processed images", and click Run.

### Command line

Edit `basedir` in `main.py`, then:

```bash
conda activate nuclei
python main.py
python main.py --skip-existing   # to resume an interrupted run
```


## Output

- `labels/` subfolder next to each image, containing segmentation masks.
- `counts_*.csv` files in the plates folder with nuclei counts per image.

CSV files are regenerated from scratch on every run. When using `--skip-existing` (or the GUI checkbox), images with existing label files are not re-segmented — their counts are read from the saved labels.
