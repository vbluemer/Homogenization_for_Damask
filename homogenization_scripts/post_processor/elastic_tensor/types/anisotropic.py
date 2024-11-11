# System packages
import numpy as np
from numpy.typing import NDArray

# Local packages

def initial_guess_anisotropic() -> list[float]:
    return np.squeeze(np.full((1,21), 1)).tolist()

def elastic_tensor_anisotropic(coefficients: list[float]) -> NDArray[np.float64]:
    C11 = coefficients[0]
    C12 = coefficients[1]
    C13 = coefficients[2]
    C14 = coefficients[3]
    C15 = coefficients[4]
    C16 = coefficients[5]
    C22 = coefficients[6]
    C23 = coefficients[7]
    C24 = coefficients[8]
    C25 = coefficients[9]
    C26 = coefficients[10]
    C33 = coefficients[11]
    C34 = coefficients[12]
    C35 = coefficients[13]
    C36 = coefficients[14]
    C44 = coefficients[15]
    C45 = coefficients[16]
    C46 = coefficients[17]
    C55 = coefficients[18]
    C56 = coefficients[19]
    C66 = coefficients[20]

    c11 = C11
    c12 = C12
    c13 = C13
    c14 = C14
    c15 = C15
    c16 = C16

    c21 = C12
    c22 = C22
    c23 = C23
    c24 = C24
    c25 = C25
    c26 = C26

    c31 = C13
    c32 = C23
    c33 = C33
    c34 = C34
    c35 = C35
    c36 = C36

    c41 = C14
    c42 = C24
    c43 = C34
    c44 = C44
    c45 = C45
    c46 = C46

    c51 = C15
    c52 = C25
    c53 = C35
    c54 = C45
    c55 = C55
    c56 = C56

    c61 = C16
    c62 = C26
    c63 = C36
    c64 = C46
    c65 = C56
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