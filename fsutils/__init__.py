# See file COPYING distributed with fsutils for copyright and license.

import numpy
import PIL.Image

class FSUtilsError(Exception):

    """base class for fsutils exceptions"""

def read_color_palette(fname):
    """read_color_palette(fname) -> palette

    Reads a FreeSurfer-formatted color table and return a list of 256 (r, g, b) 
    triples (0-255).
    """
    colors = {}
    fo = open(fname)
    for line in fo:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        (index, name, r, g, b, a) = line.split()
        colors[int(index)] = (int(r), int(g), int(b))
    fo.close()
    palette = []
    for i in xrange(256):
        if i in colors:
            palette.extend(colors[i])
        else:
            palette.extend((0, 0, 0))
    return palette

def slice(base_vol, overlay=None):
    """slice(base_vol[, overlay]) -> PIL image

    Slices the nibabel volume base_vol and returns a PIL image instance.  The 
    base volume must be 256x256x256 and have type uint8.

    If overlay is given, it must be a (nibabel volume, palette) tuple.  The 
    overlay volume is subject to the same constraints as the base volume, and 
    the palette is of the form returned by read_color_palette().
    """

    base_data = base_vol.get_data()
    if base_data.shape != (256, 256, 256):
        raise ValueError('bad base volume shape')
    if base_data.dtype != 'uint8':
        raise TypeError('bad base volume type')

    full_im = PIL.Image.new('RGB', (1536, 512))

    base_im = PIL.Image.fromarray(base_data[:,:,128].transpose(), 'L')
    base_im = base_im.resize((512, 512), PIL.Image.BILINEAR)
    full_im.paste(base_im, (0, 0))

    arr = numpy.fliplr(base_data[:,128,:]).transpose()
    base_im = PIL.Image.fromarray(arr, 'L')
    base_im = base_im.resize((512, 512), PIL.Image.BILINEAR)
    full_im.paste(base_im, (512, 0))

    base_im = PIL.Image.fromarray(base_data[128,:,:], 'L')
    base_im = base_im.resize((512, 512), PIL.Image.BILINEAR)
    full_im.paste(base_im, (1024, 0))

    if overlay:

        (overlay_vol, palette) = overlay

        overlay_data = overlay_vol.get_data()
        if overlay_data.shape != (256, 256, 256):
            raise ValueError('bad base volume shape')
        if overlay_data.dtype != 'uint8':
            raise TypeError('bad base volume type')

        full_overlay_im = PIL.Image.new('P', (1536, 512))
        full_overlay_im.putpalette(palette)

        full_overlay_mask_im = PIL.Image.new('1', (1536, 512))

        arr = overlay_data[:,:,128].transpose()
        overlay_im = PIL.Image.fromarray(arr, 'P')
        overlay_im = overlay_im.resize((512, 512))
        full_overlay_im.paste(overlay_im, (0, 0))
        mask_arr = arr.copy()
        mask_arr[mask_arr>0] = 255
        overlay_mask_im = PIL.Image.fromarray(mask_arr, 'L')
        overlay_mask_im = overlay_mask_im.resize((512, 512), PIL.Image.NEAREST)
        full_overlay_mask_im.paste(overlay_mask_im, (0, 0))

        arr = numpy.fliplr(overlay_data[:,128,:]).transpose()
        overlay_im = PIL.Image.fromarray(arr, 'L')
        overlay_im = overlay_im.resize((512, 512))
        full_overlay_im.paste(overlay_im, (512, 0))
        mask_arr = arr.copy()
        mask_arr[mask_arr>0] = 255
        overlay_mask_im = PIL.Image.fromarray(mask_arr, 'L')
        overlay_mask_im = overlay_mask_im.resize((512, 512), PIL.Image.NEAREST)
        full_overlay_mask_im.paste(overlay_mask_im, (512, 0))

        arr = overlay_data[128,:,:]
        overlay_im = PIL.Image.fromarray(arr, 'L')
        overlay_im = overlay_im.resize((512, 512))
        full_overlay_im.paste(overlay_im, (1024, 0))
        mask_arr = arr.copy()
        mask_arr[mask_arr>0] = 255
        overlay_mask_im = PIL.Image.fromarray(mask_arr, 'L')
        overlay_mask_im = overlay_mask_im.resize((512, 512), PIL.Image.NEAREST)
        full_overlay_mask_im.paste(overlay_mask_im, (1024, 0))

        full_im.paste(full_overlay_im, mask=full_overlay_mask_im)

    return full_im

# eof
