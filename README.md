# nuclei quantification

Quantification of number of nuclei in fluorescently labeled images from cell culture. Uses [Stardist](https://github.com/stardist/stardist) for nuclei segmentation.

*Note*: The plate folders should only contain nuclei images. If they contain more channels those will be wrongly segmented as nuclei.


## Installation

1. Clone this repository to your local computer:
    * Navigate to the folder where you want to clone (download) this repository.
    * Clone the repo:
```
git clone https://github.com/aecon/nuclei.git
```

2. Install the package
```
cd nuclei
conda env create -f environment.yml
```

## Usage

1. Open `main.py` (in Linux, double-click on the file), modify the `basedir` path and **save** the file. This should be the path to the directory that contains all plate folders.  

2. Go inside the `nuclei/` folder and open a terminal window.

Activate the conda environment
```
conda activate nuclei
```

Run the code
```
python main.py
```

The output `.csv` files will be automatically saved inside the `basedir`.
