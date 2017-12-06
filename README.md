# photoscan-batch
Python script to create orthophoto using Agisoft Photoscan

## Usage:

```photoscan.sh -platform offscreen -r process.py <path to project folder>```

* photoscan.sh is the main Agisoft PhotoScan executable
* If you remove -platform offscreen, the application will run with GUI
* Project folder should containt the folder 'photos' with DNG or JPG files inside

## Example:
Let's imagine that Agisoft Photoscan is installed to ~/soft/photoscan and all photos are in the folder ~/osm/2017.04.27/photos

```
tree ~/osm/2017.04.27
~/osm/2017.04.27
└── photos
    ├── DJI_0252.jpg
    ├── DJI_0253.jpg
    ├── DJI_0254.jpg
    ├── DJI_0255.jpg
    ├── DJI_0256.jpg
    ├── ............
```

So, to create an orthophoto we should cd to the dir of this repo and run the following command:
```~/soft/photoscan/photoscan.sh -platform offscreen -r process.py ~/osm/2017.04.27```

After the start of the script we will see very verbose log in STDOUT output of the script and minimalistic log in the log.txt.

After the finish of the script the project tree should look like this:
```
tree ~/osm/2017.04.27
~/osm/2017.04.27
├── ortho.files
│   ├── ..........
│   └── ..........
├── ortho.psx
├── ortho.tif
└── photos
    ├── DJI_0252.jpg
    ├── DJI_0253.jpg
    ├── DJI_0254.jpg
    ├── DJI_0255.jpg
    ├── DJI_0256.jpg
    ├── ............
```
ortho.psx and ortho.files are the Agisoft Photoscan project files.
ortho.tif is your orthophoto, enjoy!
