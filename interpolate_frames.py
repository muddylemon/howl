import numpy as np
import imageio
from scipy.interpolate import interp2d

def interpolate_frames(img1, img2, num_frames):
    im1 = imageio.imread(img1)
    im2 = imageio.imread(img2)

    x = np.linspace(0, 1, im1.shape[1])
    y = np.linspace(0, 1, im1.shape[0])

    f1_r = interp2d(x, y, im1[:, :, 0].astype(np.float64), kind='linear')
    f1_g = interp2d(x, y, im1[:, :, 1].astype(np.float64), kind='linear')
    f1_b = interp2d(x, y, im1[:, :, 2].astype(np.float64), kind='linear')

    f2_r = interp2d(x, y, im2[:, :, 0].astype(np.float64), kind='linear')
    f2_g = interp2d(x, y, im2[:, :, 1].astype(np.float64), kind='linear')
    f2_b = interp2d(x, y, im2[:, :, 2].astype(np.float64), kind='linear')

    interpolated_frames = []
    for t in np.linspace(0, 1, num_frames + 2)[1:-1]:
        im_interpolated = np.zeros_like(im1)
        im_interpolated[:, :, 0] = f1_r(x, y) * (1 - t) + f2_r(x, y) * t
        im_interpolated[:, :, 1] = f1_g(x, y) * (1 - t) + f2_g(x, y) * t
        im_interpolated[:, :, 2] = f1_b(x, y) * (1 - t) + f2_b(x, y) * t
        interpolated_frames.append(im_interpolated.astype(np.uint8))

    return interpolated_frames
