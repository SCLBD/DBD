import numpy as np
from PIL import Image


class BadNets(object):
    """The BadNets [paper]_ backdoor transformation. Inject a trigger into an image (ndarray with
    shape H*W*C) to get a poisoned image (ndarray with shape H*W*C).

    Args:
        trigger_path (str): The path of trigger image whose background is in black.

    .. rubric:: Reference

    .. [paper] "Badnets: Evaluating backdooring attacks on deep neural networks."
     Tianyu Gu, et al. IEEE Access 2019.
    """

    def __init__(self, trigger_path):
        with open(trigger_path, "rb") as f:
            trigger_ptn = Image.open(f).convert("RGB")
        self.trigger_ptn = np.array(trigger_ptn)
        self.trigger_loc = np.nonzero(self.trigger_ptn)

    def __call__(self, img):
        return self.add_trigger(img)

    def add_trigger(self, img):
        if not isinstance(img, np.ndarray):
            raise TypeError("Img should be np.ndarray. Got {}".format(type(img)))
        if len(img.shape) != 3:
            raise ValueError("The shape of img should be HWC. Got {}".format(img.shape))
        img[self.trigger_loc] = 0
        poison_img = img + self.trigger_ptn

        return poison_img


class Blend(object):
    """The Blended [paper]_ backdoor transformation. Inject a trigger into an image (ndarray with
    shape H*W*C) to get a poisoned image (ndarray with shape H*W*C) by alpha blending.

    Args:
        trigger_path (str): The path of trigger image.
        alpha (float): The interpolation factor.

    .. rubric:: Reference

    .. [paper] "Targeted backdoor attacks on deep learning systems using data poisoning."
     Xinyun Chen, et al. arXiv:1712.05526.
    """

    def __init__(self, trigger_path, alpha=0.1):
        with open(trigger_path, "rb") as f:
            self.trigger_ptn = Image.open(f).convert("RGB")
        self.alpha = alpha

    def __call__(self, img):
        return self.blend_trigger(img)

    def blend_trigger(self, img):
        if not isinstance(img, np.ndarray):
            raise TypeError("Img should be np.ndarray. Got {}".format(type(img)))
        if len(img.shape) != 3:
            raise ValueError("The shape of img should be HWC. Got {}".format(img.shape))
        img = Image.fromarray(img)
        trigger_ptn = self.trigger_ptn.resize(img.size)
        poison_img = Image.blend(img, trigger_ptn, self.alpha)

        return np.array(poison_img)
