class RobustScaleIntensity(Transform):
    """
    Scale intensity values using robust statistics (median and inter-quartile range).

    Applies ``(img - median) / (upper_percentile - lower_percentile)``, which is less
    sensitive to outliers than mean and standard deviation scaling.

    Args:
        lower_percentile: lower percentile for the scale factor, must be in ``[0, 100]``.
        upper_percentile: upper percentile for the scale factor, must be in ``[0, 100]``.
        channel_wise: if ``True``, compute statistics on each channel separately.
        dtype: output data type. if ``None``, same as input. defaults to ``float32``.
        eps: small value to avoid division by zero when the percentile range is zero.

    """

    backend = [TransformBackends.TORCH, TransformBackends.NUMPY]

    def __init__(
        self,
        lower_percentile: float = 25.0,
        upper_percentile: float = 75.0,
        channel_wise: bool = False,
        dtype: DtypeLike | None = np.float32,
        eps: float = 1e-6,
    ) -> None:
        if not 0.0 <= lower_percentile <= 100.0:
            raise ValueError(f"lower_percentile must be in [0, 100], got {lower_percentile}.")
        if not 0.0 <= upper_percentile <= 100.0:
            raise ValueError(f"upper_percentile must be in [0, 100], got {upper_percentile}.")
        if lower_percentile >= upper_percentile:
            raise ValueError(
                f"lower_percentile ({lower_percentile}) must be less than upper_percentile ({upper_percentile})."
            )
        self.lower_percentile = lower_percentile
        self.upper_percentile = upper_percentile
        self.channel_wise = channel_wise
        self.dtype = dtype
        self.eps = eps

    def _robust_stats(self, img: NdarrayOrTensor) -> tuple[NdarrayOrTensor, NdarrayOrTensor, NdarrayOrTensor]:
        if self.channel_wise and img.ndim > 1:
            flat = img.reshape(img.shape[0], -1)
            broadcast_shape = (img.shape[0],) + (1,) * (img.ndim - 1)
            med = percentile(flat, 50.0, dim=1, keepdim=True).reshape(broadcast_shape)
            low = percentile(flat, self.lower_percentile, dim=1, keepdim=True).reshape(broadcast_shape)
            high = percentile(flat, self.upper_percentile, dim=1, keepdim=True).reshape(broadcast_shape)
        else:
            flat = img.reshape(-1)
            med = percentile(flat, 50.0)
            low = percentile(flat, self.lower_percentile)
            high = percentile(flat, self.upper_percentile)
        return med, low, high

    def __call__(self, img: NdarrayOrTensor) -> NdarrayOrTensor:
        img = convert_to_tensor(img, track_meta=get_track_meta())
        med, low, high = self._robust_stats(img)
        scale = high - low
        img = img - med
        img = where(abs(scale) > self.eps, img / scale, img)
        if self.dtype is not None:
            img = convert_to_dst_type(img, img, dtype=self.dtype)[0]
        return img
