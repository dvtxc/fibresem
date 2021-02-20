import matplotlib.pyplot as plt

from scipy import ndimage as ndi
from skimage.morphology import disk
from skimage.segmentation import watershed
from skimage import data
from skimage.filters import rank
from skimage.util import img_as_ubyte

from skimage import io, segmentation, color
from skimage.future import graph
import numpy as np


def seg_watershed(inputimg, disk1, disk2, grad_thresh, merge_thresh):
    image = img_as_ubyte(inputimg)

    # denoise image
    denoised = rank.median(image, disk(disk1))

    # find continuous region (low gradient -
    # where less than 10 for this image) --> markers
    # disk(5) is used here to get a more smooth image
    markers = rank.gradient(denoised, disk(disk2)) < grad_thresh
    markers = ndi.label(markers)[0]

    # local gradient (disk(2) is used to keep edges thin)
    gradient = rank.gradient(denoised, disk(disk1))

    # process the watershed
    labels = watershed(gradient, markers)

    merged_labels = merge_labels(labels, markers, inputimg, merge_thresh)

    # display results
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(8, 8), sharex=True, sharey=True)
    ax = axes.ravel()

    ax[0].imshow(image, cmap=plt.cm.get_cmap("gray"))
    ax[0].set_title("Original")

    ax[1].imshow(gradient, cmap=plt.cm.nipy_spectral)
    ax[1].set_title("Local Gradient")

    # ax[2].imshow(
    #    rank.gradient(denoised, disk(disk2)) < thresh, cmap=plt.cm.nipy_spectral
    # )
    # ax[2].set_title("Marker below thresh")

    # ax[3].imshow(markers, cmap=plt.cm.nipy_spectral)
    # ax[3].set_title("Markers")

    ax[2].imshow(labels, cmap=plt.cm.nipy_spectral, alpha=1)
    ax[2].set_title("Labels")

    ax[3].imshow(merged_labels, cmap=plt.cm.nipy_spectral, interpolation="nearest")
    ax[3].set_title("Merged Labels")

    # ax[5].imshow(image, cmap=plt.cm.gray)
    # ax[5].imshow(labels, cmap=plt.cm.nipy_spectral, alpha=0.5)
    # ax[5].set_title("Segmented")

    for a in ax:
        a.axis("off")

    fig.tight_layout()
    plt.show()


def merge_labels(labels, markers, inputimg, threshold):
    markersInFibres = markers * (inputimg > threshold)

    merged_labels = np.zeros_like(labels)
    minlbl = np.min(labels)
    maxlbl = np.max(labels)

    for i in range(minlbl, maxlbl + 1):
        if any(markersInFibres[labels == i]):
            merged_labels = np.logical_or(merged_labels, labels == i)

    return merged_labels


def _weight_mean_color(graph, src, dst, n):
    """Callback to handle merging nodes by recomputing mean color.

    The method expects that the mean color of `dst` is already computed.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    n : int
        A neighbor of `src` or `dst` or both.

    Returns
    -------
    data : dict
        A dictionary with the `"weight"` attribute set as the absolute
        difference of the mean color between node `dst` and `n`.
    """

    diff = graph.nodes[dst]["mean color"] - graph.nodes[n]["mean color"]
    diff = np.linalg.norm(diff)
    return {"weight": diff}


def merge_mean_color(graph, src, dst):
    """Callback called before merging two nodes of a mean color distance graph.

    This method computes the mean color of `dst`.

    Parameters
    ----------
    graph : RAG
        The graph under consideration.
    src, dst : int
        The vertices in `graph` to be merged.
    """
    graph.nodes[dst]["total color"] += graph.nodes[src]["total color"]
    graph.nodes[dst]["pixel count"] += graph.nodes[src]["pixel count"]
    graph.nodes[dst]["mean color"] = (
        graph.nodes[dst]["total color"] / graph.nodes[dst]["pixel count"]
    )


def rag_seg(inputimg):
    img = img_as_ubyte(inputimg)
    labels = segmentation.slic(
        img, compactness=30, n_segments=400, start_label=1, multichannel=False
    )

    plt.imshow(labels)
    plt.show()

    g = graph.rag_mean_color(img, labels)

    labels2 = graph.merge_hierarchical(
        labels,
        g,
        thresh=35,
        rag_copy=False,
        in_place_merge=True,
        merge_func=merge_mean_color,
        weight_func=_weight_mean_color,
    )

    out = color.label2rgb(labels2, img, kind="avg", bg_label=0)
    out = segmentation.mark_boundaries(out, labels2, (0, 0, 0))
    io.imshow(out)
    io.show()