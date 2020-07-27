import cv2
import logging
import pathlib
import os
from hashlib import md5

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import ImageColor, ImageDraw, ImageFont, Image

from datasetinsights.data.datasets.cityscapes import CITYSCAPES_COLOR_MAPPING

logger = logging.getLogger(__name__)
COLORS = list(ImageColor.colormap.values())
CUR_DIR = pathlib.Path(__file__).parent.absolute()


def decode_segmap(labels, dataset="cityscapes"):
    """Decode segmentation class labels into a color image.

    Args:
        labels (np.array): an array of size (H, W) with integer grayscale
        values denoting the class label at each spatial location.
        dataset (str): dataset name. Defaults to "cityscapes".

    Returns:
        A np.array of the resulting decoded color image in (H, W, C).

    .. note:: (H, W, C) stands for the (height, width, channel) of the 2D image.
    """
    if dataset == "cityscapes":
        color_mapping = CITYSCAPES_COLOR_MAPPING
    else:
        raise ValueError(f"Dataset '{dataset}' is not supported.")

    h, w = labels.shape
    rgb = np.zeros((h, w, 3))
    for id, color in color_mapping.items():
        color = np.array(color)
        select_mask = labels == id
        rgb[select_mask, :] = color / 255.0

    return rgb


def grid_plot(
    images, figsize=(3, 5), img_type="rgb", titles=None, folder="sim2real"
):
    """ Plot 2D array of images in grid.

    Args:
        images (list): 2D array of images.
        figsize (tuple): target figure size of each image in the grid.
        Defaults to (3, 5).
        img_type (string): image plot type ("rgb", "gray"). Defaults to "rgb".
        titles (list[str]): a list of titles. Defaults to None.

    Returns:
        matplotlib figure the combined grid plot.
    """
    n_rows = len(images)
    n_cols = len(images[0])

    figsize = (figsize[0] * n_cols, figsize[1] * n_rows)

    figure = plt.figure(figsize=figsize, constrained_layout=True)
    for i in range(n_rows):
        for j in range(n_cols):
            img = images[i][j]
            k = i * n_cols + j + 1
            plt.subplot(n_rows, n_cols, k)
            plt.xticks([])
            plt.yticks([])
            if titles:
                # plt.title(titles[k - 1])
                plt.title(titles)
            plt.grid(False)
            if img_type == "gray":
                plt.imshow(img, cmap="gray")
            else:
                plt.imshow(img, plt.cm.binary)
    if titles:
        if not os.path.isdir(folder):
            os.mkdir(folder)
        figure.savefig(f"{folder}/{titles}.png")

    figure = plt.figure(figsize=figsize, constrained_layout=True)
    for i in range(n_rows):
        for j in range(n_cols):
            img = images[i][j]
            k = i * n_cols + j + 1
            plt.subplot(n_rows, n_cols, k)
            plt.xticks([])
            plt.yticks([])
            plt.grid(False)
            if img_type == "gray":
                plt.imshow(img, cmap="gray")
            else:
                plt.imshow(img, plt.cm.binary)

    if titles:
        if not os.path.isdir(f"{folder}_notitles"):
            os.mkdir(f"{folder}_notitles")
        figure.savefig(f"{folder}_notitles/{titles}.png")

    plt.show()

    return figure


def plot_bboxes(
    image, boxes, label_mappings, colors=None, box_line_width=1, font_scale=50
):
    """ Plot an image with bounding boxes.

    Args:
        image (PIL Image): a PIL image.
        boxes (list): a list of BBox2D objects.
        colors (list): a color list for boxes. Defaults to None.
        If colors = None, it will randomly assign PIL.COLORS for each box.
        box_line_width (int): line width of the bounding boxes. Defaults to 1.
        font_scale (int): how many chars can be filled in the image
        horizontally. Defaults to 50.

    Returns:
        a PIL image with bounding boxes drawn.
    """
    combined = image.copy()
    combined = np.array(combined)
    # draw = ImageDraw.Draw(combined)
    # image_width = combined.size[0]

    for i, box in enumerate(boxes):

        # x0y0 = (box.x, box.y)
        # x1y1 = (box.x + box.w, box.y + box.h)
        # xcyc = (
        #     box.x + 0.5 * box.w - image_width // font_scale,
        #     box.y + 0.5 * box.h - image_width // font_scale,
        # )
        # if not colors:
        #     color_idx = i % len(COLORS)
        #     color = COLORS[color_idx]
        # else:
        #     color = colors[i]
        # draw.rectangle((x0y0, x1y1), outline=color, width=box_line_width)
        # font_file = str(CUR_DIR / "font" / "arial.ttf")
        # font = ImageFont.truetype(font_file, image_width // font_scale)
        # text = f"{box.label}\n{box.score:.2f}"
        # draw.multiline_text(xcyc, text, font=font, fill=color)
        left, top = (box.x, box.y)
        right, bottom = (box.x + box.w, box.y + box.h)
        label = label_mappings.iloc[box.label]["Label Name"]

        if not colors:
            add(combined, left, top, right, bottom, label=label, color=None)
        else:
            label = f"{label}: {box.score * 100: .2f}%"
            add(
                combined,
                left,
                top,
                right,
                bottom,
                label=label,
                color=colors[i],
            )

    return Image.fromarray(combined)


def bar_plot(
    df, x, y, title=None, x_title=None, y_title=None, x_tickangle=0, **kwargs
):
    """Create plotly bar plot

    Args:
        df (pd.DataFrame): A pandas dataframe that contain bar plot data.
        x (str): The column name of the data in x-axis.
        y (str): The column name of the data in y-axis.
        title (str, optional): The title of this plot.
        x_title (str, optional): The x-axis title.
        y_title (str, optional): The y-axis title.
        x_tickangle (int, optional): X-axis text tickangle (default: 0)

    This method can also take addition keyword arguments that can be passed to
    [plotly.express.bar](https://plotly.com/python-api-reference/generated/plotly.express.bar.html#plotly.express.bar) method.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [0, 1, 2], "name": ["a", "b", "c"],
        ...                    "count": [10, 20, 30]})
        >>> bar_plot(df, x="id", y="count", hover_name="name")
    """  # noqa: E501 URL should not be broken down into lines
    fig = px.bar(df, x=x, y=y, **kwargs)
    fig = fig.update_layout(
        xaxis=dict(title=x_title, tickangle=x_tickangle),
        yaxis=dict(title=y_title),
        title_text=title,
    )

    return fig


def histogram_plot(
    df, x, max_samples=None, title=None, x_title=None, y_title=None, **kwargs
):
    """Create plotly histogram plot

    Args:
        df (pd.DataFrame): A pandas dataframe that contain raw data.
        x (str): The column name of the raw data for histogram plot.
        title (str, optional): The title of this plot.
        x_title (str, optional): The x-axis title.
        y_title (str, optional): The y-axis title.

    This method can also take addition keyword arguments that can be passed to
    [plotly.express.histogram](https://plotly.com/python-api-reference/generated/plotly.express.histogram.html) method.

    Examples:
        >>> import pandas as pd
        >>> df = pd.DataFrame({"id": [0, 1, 2], "count": [10, 20, 30]})
        >>> histogram_plot(df, x="count")

        Histnorm plot using probability density:

        >>> histogram_plot(df, x="count", histnorm="probability density")
    """  # noqa: E501 URL should not be broken down into lines
    if max_samples and len(df) > max_samples:
        df = df.sample(n=max_samples)

    fig = px.histogram(df, x=x, **kwargs)
    fig = fig.update_layout(
        xaxis=dict(title=x_title), yaxis=dict(title=y_title), title_text=title,
    )

    return fig


def _convert_euler_rotations_to_scatter_points(
    df, x_col, y_col, z_col=None, max_samples=None
):
    """Turns euler rotations into a dataframe of points for plotting."""
    if max_samples is not None and len(df) > max_samples:
        df = df.sample(max_samples)

    for _, row in df.iterrows():
        v1 = np.array((0, 1, 0))

        theta_x = np.radians(row[x_col])

        rx = np.array(
            (
                (np.cos(theta_x), -np.sin(theta_x), 0),
                (np.sin(theta_x), np.cos(theta_x), 0),
                (0, 0, 1),
            )
        )
        v1 = rx.dot(v1)

        theta_y = np.radians(row[y_col])
        ry = np.array(
            (
                (1, 0, 0),
                (0, np.cos(theta_y), -np.sin(theta_y)),
                (0, np.sin(theta_y), np.cos(theta_y)),
            )
        )
        v1 = ry.dot(v1)

        if z_col is not None:
            theta_z = np.radians(row[z_col])
            rz = np.array(
                (
                    (np.cos(theta_z), 0, np.sin(theta_z)),
                    (0, 1, 0),
                    (-np.sin(theta_z), 0, np.cos(theta_z)),
                )
            )
            v1 = rz.dot(v1)

            text = """x: {x}°  y: {y}°  z: {z}°""".format(
                x=row[x_col], y=row[y_col], z=row[z_col]
            )
        else:
            text = """x: {x}°  y: {y}°""".format(x=row[x_col], y=row[y_col])

        ser = [v1[0], v1[1], v1[2], text]
        yield ser


def rotation_plot(df, x, y, z=None, max_samples=None, title=None, **kwargs):
    """Create a plotly 3d rotation plot
    Args:
        df (pd.DataFrame): A pandas dataframe that contains the raw data.
        x (str): The column name containing x rotations.
        y (str): The column name containing y rotations.
        z (str, optional): The column name containing z rotations.
        title (str, optional): The title of this plot.

    This method can also take addition keyword arguments that can be passed to
    [plotly.graph_objects.Scatter3d](https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scatter3d.html) method.

    Returns:
        A plotly.graph_objects.Figure containing the scatter plot
    """  # noqa: E501 URL should not be broken down into lines
    rot_plot_columns = ("x", "y", "z", "text")
    dfrot = pd.DataFrame(
        list(
            _convert_euler_rotations_to_scatter_points(df, x, y, z, max_samples)
        ),
        columns=rot_plot_columns,
    )
    fig = (
        go.Figure(
            data=[
                go.Scatter3d(
                    x=dfrot["x"],
                    y=dfrot["y"],
                    z=dfrot["z"],
                    text=dfrot["text"],
                    mode="markers",
                    hoverinfo="text",
                    marker=dict(size=5, opacity=0.5),
                    **kwargs,
                )
            ]
        )
        .update_xaxes(showticklabels=False)
        .update_layout(
            title_text=title,
            scene=dict(
                xaxis=dict(showticklabels=False, range=[-1, 1]),
                yaxis=dict(showticklabels=False, range=[-1, 1]),
                zaxis=dict(showticklabels=False, range=[-1, 1]),
            ),
        )
    )
    return fig


_LOC = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

_COLOR_NAME_TO_RGB = dict(
    navy=((0, 38, 63), (119, 193, 250)),
    blue=((0, 120, 210), (173, 220, 252)),
    aqua=((115, 221, 252), (0, 76, 100)),
    teal=((15, 205, 202), (0, 0, 0)),
    olive=((52, 153, 114), (25, 58, 45)),
    green=((0, 204, 84), (15, 64, 31)),
    lime=((1, 255, 127), (0, 102, 53)),
    yellow=((255, 216, 70), (103, 87, 28)),
    orange=((255, 125, 57), (104, 48, 19)),
    red=((255, 47, 65), (131, 0, 17)),
    maroon=((135, 13, 75), (239, 117, 173)),
    fuchsia=((246, 0, 184), (103, 0, 78)),
    purple=((179, 17, 193), (241, 167, 244)),
    gray=((168, 168, 168), (0, 0, 0)),
    silver=((220, 220, 220), (0, 0, 0)),
)

_COLOR_NAMES = list(_COLOR_NAME_TO_RGB)

_DEFAULT_COLOR_NAME = "green"

_FONT_PATH = str(CUR_DIR / "font" / "arial.ttf")
_FONT_HEIGHT = 100
_FONT = ImageFont.truetype(_FONT_PATH, _FONT_HEIGHT)


def _rgb_to_bgr(color):
    return list(color)


def _color_image(image, font_color, background_color):
    return background_color + (font_color - background_color) * image / 255


def _get_label_image(text, font_color_tuple_bgr, background_color_tuple_bgr):
    text_image = _FONT.getmask(text)
    shape = list(reversed(text_image.size))
    bw_image = np.array(text_image).reshape(shape)

    image = [
        _color_image(bw_image, font_color, background_color)[None, ...]
        for font_color, background_color in zip(
            font_color_tuple_bgr, background_color_tuple_bgr
        )
    ]

    return np.concatenate(image).transpose(1, 2, 0)


def add(image, left, top, right, bottom, label=None, color=None):
    if type(image) is not np.ndarray:
        raise TypeError("'image' parameter must be a numpy.ndarray")
    try:
        left, top, right, bottom = int(left), int(top), int(right), int(bottom)
    except ValueError:
        raise TypeError("'left', 'top', 'right' & 'bottom' must be a number")

    if label and type(label) is not str:
        raise TypeError("'label' must be a str")

    if label and not color:
        hex_digest = md5(label.encode()).hexdigest()
        color_index = int(hex_digest, 16) % len(_COLOR_NAME_TO_RGB)
        color = _COLOR_NAMES[color_index]

    # if not color:
    #     color = _DEFAULT_COLOR_NAME

    if type(color) is not str:
        raise TypeError("'color' must be a str")

    if color not in _COLOR_NAME_TO_RGB:
        msg = "'color' must be one of " + ", ".join(_COLOR_NAME_TO_RGB)
        raise ValueError(msg)

    colors = [_rgb_to_bgr(item) for item in _COLOR_NAME_TO_RGB[color]]
    color, color_text = colors

    cv2.rectangle(image, (left, top), (right, bottom), color, thickness=15)

    if label:
        _, image_width, _ = image.shape

        label_image = _get_label_image(label, color_text, color)
        label_height, label_width, _ = label_image.shape

        rectangle_height, rectangle_width = 1 + label_height, 1 + label_width

        rectangle_bottom = top
        rectangle_left = max(0, min(left - 1, image_width - rectangle_width))

        rectangle_top = rectangle_bottom - rectangle_height
        rectangle_right = rectangle_left + rectangle_width

        label_top = rectangle_top + 1

        if rectangle_top < 0:
            rectangle_top = top
            rectangle_bottom = rectangle_top + label_height + 1

            label_top = rectangle_top

        label_left = rectangle_left + 1
        label_bottom = label_top + label_height
        label_right = label_left + label_width

        rec_left_top = (rectangle_left, rectangle_top)
        rec_right_bottom = (rectangle_right, rectangle_bottom)

        cv2.rectangle(image, rec_left_top, rec_right_bottom, color, -1)

        image[label_top:label_bottom, label_left:label_right, :] = label_image
