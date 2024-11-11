# System packages
import numpy as np
from numpy.typing import NDArray

# Local packages

def initial_guess_isotropic() -> list[float]:
    return [1, 1]

def elastic_tensor_isotropic(coefficients: list[float]) -> NDArray[np.float64]:
    C11 = coefficients[0]
    C12 = coefficients[1]

    c11 = C11
    c12 = C12
    c13 = C12
    c14 = 0
    c15 = 0
    c16 = 0

    c21 = C12
    c22 = C11
    c23 = C12
    c24 = 0
    c25 = 0
    c26 = 0

    c31 = C12
    c32 = C12
    c33 = C11
    c34 = 0
    c35 = 0
    c36 = 0

    c41 = 0
    c42 = 0
    c43 = 0
    c44 = (C11 - C12) /2
    c45 = 0
    c46 = 0

    c51 = 0
    c52 = 0
    c53 = 0
    c54 = 0
    c55 = (C11 - C12) /2
    c56 = 0

    c61 = 0
    c62 = 0
    c63 = 0
    c64 = 0
    c65 = 0
    c66 = (C11 - C12) /2

    elastic_tensor: NDArray[np.float64] = np.array([ # type: ignore
        [c11, c12, c13, c14, c15, c16],
        [c21, c22, c23, c24, c25, c26],
        [c31, c32, c33, c34, c35, c36],
        [c41, c42, c43, c44, c45, c46],
        [c51, c52, c53, c54, c55, c56],
        [c61, c62, c63, c64, c65, c66]
    ])

    return elastic_tensor