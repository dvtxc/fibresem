import numpy as np
from skimage import io, filters
from quanfima import morphology as mrph
from quanfima import visualization as vis
from quanfima import utils
import matplotlib.pyplot as plt

img = io.imread("test.tif")
f = plt.figure(
    figsize=(img.shape[1] / 300, img.shape[0] / 300)
)  # figure with correct aspect ratio
ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
ax.imshow(img, cmap="gray")
plt.show()

th_val = filters.threshold_otsu(img)
img_seg = (img > th_val).astype(np.uint8)

# estimate porosity
pr = mrph.calc_porosity(img_seg)
for k, v in pr.items():
    print("Porosity ({}): {}".format(k, v))

f = plt.figure(
    figsize=(img_seg.shape[1] / 300, img_seg.shape[0] / 300)
)  # figure with correct aspect ratio
ax = plt.axes((0, 0, 1, 1))  # axes over whole figure
ax.imshow(img_seg, cmap="gray")
plt.show()

# prepare data and analyze fibers
data, skeleton, skeleton_thick = utils.prepare_data(img_seg)
cskel, fskel, omap, dmap, ovals, dvals = mrph.estimate_fiber_properties(data, skeleton)

# plot results
vis.plot_orientation_map(
    omap,
    fskel,
    min_label=u"0°",
    max_label=u"180°",
    figsize=(10, 10),
    name="2d_polymer",
    output_dir="/path/to/output/dir",
)
vis.plot_diameter_map(
    dmap,
    cskel,
    figsize=(10, 10),
    cmap="gist_rainbow",
    name="2d_polymer",
    output_dir="/path/to/output/dir",
)