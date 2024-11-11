# System packages
import numpy as np
from numpy.typing import NDArray

# Local packages

def initial_guess_orthotropic() -> list[float]:
    return np.squeeze(np.full((1,9), 1)).tolist()

def elastic_tensor_orthotropic(coefficients: list[float]) -> NDArray[np.float64]:
    C11 = coefficients[0]
    C12 = coefficients[1]
    C13 = coefficients[2]
    C22 = coefficients[3]
    C23 = coefficients[4]
    C33 = coefficients[5]
    C44 = coefficients[6]
    C55 = coefficients[7]
    C66 = coefficients[8]

    c11 = C11
    c12 = C12
    c13 = C13
    c14 = 0
    c15 = 0
    c16 = 0

    c21 = C12
    c22 = C22
    c23 = C23
    c24 = 0
    c25 = 0
    c26 = 0

    c31 = C13
    c32 = C23
    c33 = C33
    c34 = 0
    c35 = 0
    c36 = 0

    c41 = 0
    c42 = 0
    c43 = 0
    c44 = C44
    c45 = 0
    c46 = 0

    c51 = 0
    c52 = 0
    c53 = 0
    c54 = 0
    c55 = C55
    c56 = 0

    c61 = 0
    c62 = 0
    c63 = 0
    c64 = 0
    c65 = 0
    c66 = C66

    elastic_tensor: NDArray[np.float64] = np.array([ # type: ignore
        [c11, c12, c13, c14, c15, c16],
        [c21, c22, c23, c24, c25, c26],
        [c31, c32, c33, c34, c35, c36],
        [c41, c42, c43, c44, c45, c46],
        [c51, c52, c53, c54, c55, c56],
        [c61, c62, c63, c64, c65, c66]
    ])

    return elastic_tensor