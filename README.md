# nuclei quantification

Note: The plate folders should only contain nuclei images. If they contain more channels those will be wrongly segmented as nuclei.


## Installation
1. Download the nuclei code. Go to the folder where you wish to download the code, and open in Terminal
```
git clone https://github.com/aecon/nuclei.git
```


2. Go inside the `nuclei/` folder.  
3. Open a Terminal window inside the nuclei folder.  
    In Lunix: Right click - Open in Terminal.

```
conda env create -f environment.yml
```

## Usage

1. Open `main.py` (in Linux, double-click on the file) and modify the `basedir` path. This should be the path to the directory that contains all plate folders.  

2. Go inside the `nuclei/` folder and open a terminal window.
```
conda activate nuclei
python main.py
```

The output `.csv` files will be automatically saved inside the `basedir`.
