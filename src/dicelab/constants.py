"""Engine-wide tuning constants."""

EXPLODE_EPSILON: float = 1e-12
MAX_EXPLODE_DEPTH: int = 100
DEFAULT_PERCENTILES: tuple[int, ...] = (5, 25, 50, 75, 95)
