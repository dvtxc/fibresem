"""
Test to see whether the simpoly steps can be converted to python.
"""
import os
import tifffile
import matplotlib.pyplot as plt
from lib import readtif
import skimage
from skimage import exposure
from skimage import morphology
from skimage.morphology import disk
from skimage.feature import canny
import math


def crop_square(tifimg):
    # Crop to Square and omit the SEM meta bar

    barheight = 0.11
    newHeight = round(tifimg.shape[0] * (1 - barheight))
    left = round((tifimg.shape[1] - newHeight) / 2)
    right = tifimg.shape[1] - left

    tifimg = tifimg[0:newHeight, left:right]

    return tifimg


def save(ax, image, name, maxval=1):
    ax.imshow(image, cmap="gray", vmin=0, vmax=maxval)
    ax.axis("off")

    name = name + "-py.png"
    pathout = os.path.join(os.getcwd(), "experimental", "conversion-out", name)
    plt.savefig(pathout, bbox_inches="tight", pad_inches=0, dpi=300)
    print("Exported " + name)


# MAIN CODE
if __name__ == "__main__":

    # Load image
    path = (
        r"C:\Dev\python\sem\fibresem\testfiles\originals\COLL.226_0200u_s1_img014.tif"
    )
    image, meta = readtif.importtif(path)
    print(
        "Loaded image {0} {1}/px.".format(
            meta["Pixel Size Value"], meta["Pixel Size Unit"]
        )
    )

    # Crop to square and remove SEM information bar
    image = crop_square(image)

    # Create Matplotlib figure
    f = plt.figure(figsize=(image.shape[1] / 300, image.shape[0] / 300))
    # Create axes
    ax = plt.axes((0, 0, 1, 1))

    save(ax, image, "00-original", maxval=255)

    # Enhance Contrast
    Ihist = skimage.exposure.equalize_adapthist(
        image, kernel_size=None, clip_limit=0.01, nbins=256
    )
    save(ax, Ihist, "01-enhance-contrast")

    # Enhance contrast 2
    # Replaces histeq()
    # Default nbins python: 256, default nbins matlab: 64
    Ihist = skimage.exposure.equalize_hist(Ihist, nbins=64, mask=None)
    save(ax, Ihist, "02-enhance-contrast")

    # Erode Grayscale
    # Structuring element disk in Matlab is actually an octagon
    # strel('disk', 5) --> corresponds to morphology.octagon(5, 2)
    strel = morphology.octagon(5, 2)
    marker = skimage.morphology.erosion(
        Ihist, strel, out=None, shift_x=False, shift_y=False
    )
    save(ax, marker, "03-erode")

    # Reconstruction
    Iobr = skimage.morphology.reconstruction(
        marker, Ihist, method="dilation", offset=None
    )
    save(ax, Iobr, "04-reconstruction")

    # Edge Finding

    # default sigma in MATLAB = sqrt(2), default in skimage = 1.0
    E = canny(
        Iobr, sigma=1.7, low_threshold=0.2, high_threshold=0.4, use_quantiles=False
    )
    save(ax, E, "05-canny-sig17")

    # Remove small objects with less than 20 pixels
    min_area = 20
    E = morphology.area_opening(E, area_threshold=min_area, connectivity=2)
    save(ax, E, "06-areaopen")

    E = morphology.dilation(E)
    save(ax, E, "07-thicken")

    print("success")
