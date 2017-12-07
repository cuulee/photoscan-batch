import os,re,sys
import os.path
import datetime

def usage():
    print("Usage:")
    print("")
    print("photoscan.sh -platform offscreen -r process.py <path to project folder>")
    print("")
    print("photoscan.sh is the main Agisoft PhotoScan executable")
    print("If you remove -platform offscreen, the application will run with GUI")
    print("Project folder should containt the folder 'photos' with DNG or JPG files inside")
    exit()

try:
    import PhotoScan
except:
    print("Cannot import module PhotoScan")
    print("You shouldn't run this script by python interpreter. Use Agisoft PhotoScan instead.")
    usage()

logfile = open("log.txt", "a")

def logAction(text):
    print(text)
    logfile.write("{} {}\n".format(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), text))
    logfile.flush()

# get the photo list in specified folder
def getPhotoList(root_path, photoList):
    pattern = re.compile('(\.dng|\.jpg)$', re.IGNORECASE)
    for root, dirs, files in os.walk(root_path + '/photos'):
        for name in files:
            if pattern.search(name):
                cur_path = os.path.join(root, name)
                photoList.append(cur_path)

def progress(p):
    print("Progress: {0}".format(p))

def createOrOpenProject(root_path):
    doc = PhotoScan.app.document
    psxfile = root_path + '/ortho.psx'
    if os.path.isfile(psxfile):
        doc.open( psxfile )
        logAction('Opened: ' + psxfile)
    else:
        doc.save( psxfile )
        logAction('New project saved to: ' + psxfile)
    return doc

def saveProject(doc):
    t = datetime.datetime.now()
    doc.save()
    logAction("Saved the project ({})".format(datetime.datetime.now()-t))

def addPhotos(chunk, root_path):
    photoList = []
    getPhotoList(root_path, photoList)
    #print (photoList)
    
    chunk.addPhotos(photoList)

def alignPhotos(chunk):
    ## Perform image matching for the chunk frame.
    # matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000[, progress])
    # - Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
    # - Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
    chunk.matchPhotos(
        accuracy=PhotoScan.HighestAccuracy,
        preselection=PhotoScan.ReferencePreselection,
        filter_mask=False,
        keypoint_limit=40000,
        tiepoint_limit=0,
        progress=progress)
    chunk.alignCameras()

def buildDenseCloud(chunk):
    ## Generate depth maps for the chunk.
    # buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
    # - Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
    # - Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
    chunk.buildDenseCloud(
        quality=PhotoScan.HighQuality,
        filter=PhotoScan.ModerateFiltering,
        progress=progress)

def buildDEM(chunk):
    ### build DEM (before build dem, you need to save the project into psx) ###
    ## Build elevation model for the chunk.
    # buildDem(source=DenseCloudData, interpolation=EnabledInterpolation[, projection ][, region ][, classes][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    chunk.buildDem(
        source=PhotoScan.DenseCloudData,
        interpolation=PhotoScan.EnabledInterpolation,
        projection=chunk.crs,
        progress=progress)

def buildOrtho(chunk):
    ## Build orthomosaic for the chunk.
    # buildOrthomosaic(surface=ElevationData, blending=MosaicBlending, color_correction=False[, projection ][, region ][, dx ][, dy ][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    # - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
    chunk.buildOrthomosaic(
        surface=PhotoScan.ElevationData,
        blending=PhotoScan.DisabledBlending,
        color_correction=True,
        projection=chunk.crs,
        progress=progress)

def exportOrtho(chunk, root_path):
    chunk.exportOrthomosaic(
    root_path + '/ortho.tif',
    image_format=PhotoScan.ImageFormatTIFF,
    tiff_compression=PhotoScan.TiffCompressionNone,
    tiff_big=True,
    progress=progress)

def photoscanProcess(root_path):                
    #PhotoScan.app.messageBox('hello world! \n')
    # PhotoScan.app.console.clear()
    # PhotoScan.app.gpu_mask = 1

    doc = createOrOpenProject(root_path)

    chunk = PhotoScan.Chunk
    if len(doc.chunks)>0:
        chunk = doc.chunk
        logAction("Using the existing chunk '{}'".format(chunk.label))
    else:
        chunk = doc.addChunk()
        chunk.crs = PhotoScan.CoordinateSystem("EPSG::4326")
        logAction("Created the new chunk '{}'".format(chunk.label))
    ################################################################################################

    if len(chunk.cameras)>0:
        logAction("Skipping adding photos and aligning cameras because chunk already has {} cameras".format(len(chunk.cameras)))
    else:
        logAction("Started adding photos")
        t = datetime.datetime.now()
        addPhotos(chunk, root_path)
        logAction("Added photos ({})".format(datetime.datetime.now()-t))

        logAction("Started photos alignment")
        t = datetime.datetime.now()
        alignPhotos(chunk)
        logAction("Aligned photos ({})".format(datetime.datetime.now()-t))
        saveProject(doc)

    ################################################################################################
    if chunk.dense_cloud is None:
        logAction("Started buildling dense cloud")
        t = datetime.datetime.now()
        buildDenseCloud(chunk)
        logAction("Built dense cloud ({})".format(datetime.datetime.now()-t))
        saveProject(doc)
    else:
        logAction("Skipping dense cloud build because chunk already has {}".format(chunk.dense_cloud))

    ################################################################################################
    logAction("Started buildling DEM")
    t = datetime.datetime.now()
    buildDEM(chunk)
    logAction("Built DEM ({})".format(datetime.datetime.now()-t))
    saveProject(doc)

    ################################################################################################
    logAction("Started buildling orthomosaic")
    t = datetime.datetime.now()
    buildOrtho(chunk)
    logAction("Built orthomosaic ({})".format(datetime.datetime.now()-t))
    saveProject(doc)

    logAction("Started exporting orthomosaic")
    t = datetime.datetime.now()
    exportOrtho(chunk, root_path)
    logAction("Exported orthomosaic ({})".format(datetime.datetime.now()-t))

if len(sys.argv) < 2:
    usage()

project_folder = sys.argv[1]
project_folder = re.sub(r"[\/]+$", "", project_folder)

# main
photoscanProcess(project_folder)
