import fibresem as fs
import os

baseDir = r"I:\Projekte\Projekte\121250_PolyKARD\5-Data\01_Electrospinning\SEM\SEM 2021.04.14\restinput"
fileExt = "*.tif"

for root, dirs, files in os.walk(baseDir):
    path = root.split(os.sep)
    print((len(path) - 1) * "---", os.path.basename(root))
    for i in range(len(files)):
        curFileName = files[i]
        fullFileName = os.path.join(root, curFileName)

        print(len(path) * "---", curFileName, end="")

        parts = curFileName.split(".")
        ext = parts[-1]

        if ext == "tif":

            img, tags = fs.read(fullFileName)

            img = fs.crop_square(img)

            print("  Cropped, ", end="")

            fs.annotate(img, tags, os.path.join(root, "cropped", curFileName))

        else:
            print("  Not a TIFF file")
