class RobustScaleIntensity(Transform):
    """
    Scale the intensity of the input image robustly using the median and the
    inter-percentile range (default: interquartile range, IQR):

    ``v = (v - median) / (p_upper - p_lower)``

    Robust intensity scaling is resistant to outliers compared with mean/std
    normalization, which helps stabilize training on medical images with bright
    artifacts or a few extreme voxels. When the inter-percentile range is zero
    (e.g. a constant image), the median-subtracted image is returned to avoid
    dividing by zero.
    """

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(
        self,
        lower: float = 25.0,
        upper: float = 75.0,
        channel_wise: bool = False,
        dtype: DtypeLike = np.float32,
    ) -> None:
        """
        Args:
            lower: lower percentile of the range. Defaults to 25.0.
            upper: upper percentile of the range. Defaults to 75.0.
            channel_wise: if True, scale on each channel separately. Please ensure
                that the first dimension represents the channel of the image if True.
            dtype: output data type, if None, same as input image. defaults to float32.

        Raises:
            ValueError: When ``lower`` is not less than ``upper``.
        """
        if lower >= upper:
            raise ValueError(f"lower must be less than upper, got lower={lower}, upper={upper}.")
        self.lower = lower
        self.upper = upper
        self.channel_wise = channel_wise
        self.dtype = dtype

    def _normalize(self, img: NdarrayOrTensor) -> NdarrayOrTensor:
        median = percentile(img, 50.0)
        scale = percentile(img, self.upper) - percentile(img, self.lower)
        if scale == 0:
            return img - median
        return (img - median) / scale

    def __call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor:
        """Apply the transform to `img`."""
        img = convert_to_tensor(img, track_meta=get_track_meta())
        img_t = convert_to_tensor(img, track_meta=False)
        if self.channel_wise:
            ret = torch.stack([self._normalize(d) for d in img_t])  # type: ignore
        else:
            ret = self._normalize(img_t)
        ret = convert_to_dst_type(ret, dst=img, dtype=self.dtype or img_t.dtype)[0]
        return ret
