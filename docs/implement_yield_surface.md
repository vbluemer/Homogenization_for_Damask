## Implementation of an additional yield surface

- [Implementation of an additional yield surface](#implementation-of-an-additional-yield-surface)
  - [Create a class for the yield surface](#create-a-class-for-the-yield-surface)
  - [Add the yield surface to the workflow](#add-the-yield-surface-to-the-workflow)
    - [Create a workflow for `my_yield_surface`](#create-a-workflow-for-my_yield_surface)
    - [Add `my_yield_surface` to the list of options in the `fit_yield_surface()` function](#add-my_yield_surface-to-the-list-of-options-in-the-fit_yield_surface-function)


The yield surfaces in this project are implemented with an object-oriented approach in mind. This makes it possible to add additional yield surfaces with relative ease. However, this does require the user to write some functions in the source code of this project. This guide exists to show all the adjustments one should make.

### Create a class for the yield surface
The yield surface to be added must be made in the form of a class. For this class to be compatible as a yield surface, it must implement the `YieldSurfaces` `Protocol`. 

This is to say; A `Protocol` in Python is like a blue print of functions a class should contain, and the specific protocol to use in this case is the `YieldSurfaces`. This protocol can be found under `homogenization_scripts/post_processor/yield_surfaces/yield_surface_template.py`, or through [`this link`](../homogenization_scripts/post_processor/yield_surfaces/yield_surface_template.py). This file contains plenty of documentation by itself, the reader is advised to read this thoroughly. 

As an example, a simple imaginative yield surface has been added as well. This example implementation can be found under `homogenization_scripts/post_processor/yield_surfaces/example_yield_surface.py`, or through [`this link`](../homogenization_scripts/post_processor/yield_surfaces/example_yield_surface.py).

This simple yield surface is models the following yield criterion:
$$1 = A * c * | \sigma |^2$$
Here, $\sigma$ is the homogenized stress in Voigt notation,$A$ some constant that does not change during the data fitting process and $c$ a coefficient that needs to be fitted. 

An additional requirement of this imaginative yield surface is that c should be larger then 0.

The implementation of the ExampleYieldSurface will be given per function:

**Import the needed functions and packages**

The `numpy` function is used for matrix manipulation and the general_functions.py provides a generalized implementation of the mean square error calculation. It is found in the same folder as the ExampleYieldSurface, hence, it is advised to add a new yield surface in the same folder as well. Import of `pandas` only used for the optional type checker in this case.
```
# System packages
from pandas import DataFrame
import numpy as np

# Local packages
from .general_functions import calculate_MSE_stress

```

**Define the class**

The yield surface must be given a name. By adding some `[variable_name]: [type]` statements a Python editor can help with correction the code:

```
class ExampleYieldSurface():
    mean_square_error_stress: float
    some_constant: float
    coefficient_1: float
```

**Define the constructor**

The `__init__` function defines how a class can be initiated. In case, it can be used as `example_yield_surface = ExampleYieldSurface(some_constant = 5.3)` which makes it accessible with `self.some_constant` within the class structure. 

Adding this function is only needed if the yield surface needs to programmable constants.
```
class ExampleYieldSurface():
    ...

    def __init__(self, some_constant: float) -> None:
        # some_constant is setup before the optimization process starts.
        # This is used as: example_yield_surface = ExampleYieldSurface(some_constant = 5)
        self.some_constant = some_constant
        return
```
**Assign the tuneable coefficients**

The optimization process needs to be able to change the coefficients in the yield surface for fitting purposes. It also needs information on how many tuneable coefficients exist. 

The `set_coefficients_from_list` needs to assign the coefficients to some stored variables from a list it is provided. `number_optimization_coefficients` reflects that there is just one tuneable coefficient in this case.
```
class ExampleYieldSurface():
    ...

    def set_coefficients_from_list(self, coefficients_list: list[float]) -> None:
        self.coefficient_1 = coefficients_list[0]
        return
    
    def number_optimization_coefficients(self) -> int:
        number_of_coefficients = 1
        return number_of_coefficients

```
**Add display and unit conversion**

The yield surface needs a name that can be used for displaying purposes, this name should be defined with the `display_name` function. 

The data of DAMASK is given in Pascal, however, other units can be used for use in the yield surface. `unit_conversion` makes sure this is done consistently and `unit_name` is used to add the right the unit information to the plot and fit.

```
class ExampleYieldSurface():
    ...
    
    def display_name(self) -> str:
        display_name = "Example yield surface"
        return display_name
    
    def unit_conversion(self) -> float:
        # The yield point data is in Pascal, this translates the stresses to another unit
        Pa_to_MPa = 1/1E3
        return Pa_to_MPa
    
    def unit_name(self) -> str:
        unit_name = "kPa"
        return unit_name
```
**Evaluation of the function**

The fitting process assumes that the yield surface function will equate to 0 at yielding. This requires the yield function as given before to be rewritten:

$$0 \approx 1 -  A * c * | \sigma |^2$$

Normalization of the coefficients is also a good practice to improve the data fitting process. This can be applied by adjusting the $1$ term to be normalized with the `unit_conversion()` function:

$$0 \approx \frac{1}{\textrm{self.unit-conversion()}} -  A * c * | \sigma |^2$$

```
class ExampleYieldSurface():
    ...
  
    def evaluate(self, stress_Voigt: list[float]) -> float:
        
        stress_numpy = np.array(stress_Voigt)

        # Non-physical example: only take stress magnitude into account.
        stress_magnitude: float = float(np.linalg.norm(stress_numpy))

        # Get the constants and coefficients from memory:
        some_constant = self.some_constant
        coefficient_1 = self.coefficient_1
        unit_conversion = self.unit_conversion()

        # Calculate the yield surface value:
        yield_surface_value = -1/unit_conversion - some_constant * coefficient_1 * stress_magnitude**2

        return yield_surface_value
```

**Apply conditions set on coefficients**

In this example case the condition was set that the `c` coefficient should be larger then `0`. In this framework, this is expected to be added with a barrier function ([Wiki](https://en.wikipedia.org/wiki/Barrier_function)). By adding a positive value to the penalty when `c` is smaller then 0, the will adhere to the constraint.

```
class ExampleYieldSurface():
    ...

    def penalty_sum(self) -> float:
        # Suppose coefficient_1 needs to be larger then 0
        coefficient_1 = self.coefficient_1

        penalty = 1000000*min([0, coefficient_1])**2
        return penalty
```

**Write the yield surface to a file**

The yield surface must be able to be written to a file. This function can be as simple or elaborate as needed.
```
class ExampleYieldSurface():
    ...
    def write_to_file(self, path:str, MSE: float | None = None) -> None:
        print("")
        print(f"Writing {self.display_name()} fit to .csv file: {path}")
        with open(path, "w") as file:
            if MSE == None:
                file.write(f"coefficient_1 = {self.coefficient_1}, unit_stress = {self.unit_name()}")
            else:
                file.write(f"coefficient_1 = {self.coefficient_1}, MSE = {MSE}, unit_stress = {self.unit_name()}")

        return
```

**Find the mean square error**

The mean square error can be found with the generic implementation, with `from .general_functions import calculate_MSE_stress`, the following functions can be copied directly from the `YieldSurfaces Protocol`:
```
class ExampleYieldSurface():
    ...
    
    # Functions copied over without any change.

    def get_MSE(self, data_set: DataFrame) -> float:
        # Calculate the mean square error of over/under estimation of yield stresses
        mean_square_error = calculate_MSE_stress(self, data_set) # type: ignore
        return mean_square_error
    
    def set_MSE(self, mean_square_error_stress: float) -> None:
        # Store the mean square error of over/under estimation of yield stresses
        self.mean_square_error_stress = mean_square_error_stress
        return
    
    def get_and_set_MSE(self, data_set: DataFrame) -> float:
        mean_square_error_stress = self.get_MSE(data_set)
        self.set_MSE(mean_square_error_stress)
        return mean_square_error_stress
```

**General note**
It is advised to keep the custom implemented yield surface in the `homogenization_scripts/post_processor/yield_surfaces` for simpler imports of files. However, do keep a copy of the script in a separate location to prevent it getting lost. 

Using a symbolic link (in Linux) can make such a structure manageable:
```
ln -s /home/my_user/my_yield_surface.py homogenization_scripts/post_processor/yield_surfaces/my_yield_surface.py
```
In this case, the actual copy of the file is stored in the users home directory (run this command from the root folder of the code).
### Add the yield surface to the workflow
Beside creating the yield surface itself, a workflow for the yield surface must be created so that when `my_yield_surface` is entered as the `yield_criterion`, the right yield surface is used. This is done by adjusting the `homogenization_scripts/post_processor/fit_yield_surface.py` file. Two adjustments needs to be made here:

1. Create a workflow for `my_yield_surface`
2. Add `my_yield_surface` to the list of options in the `fit_yield_surface()` function

#### Create a workflow for `my_yield_surface`
When a yield surface is chosen, the right steps must be taken to complete the fitting and writing process. As the steps are not always the same for each yield surface, these have to setup manually. In this case the example already provided for the `example_yield_surface` will be used which is also found in the `homogenization_scripts/post_processor/fit_yield_surface.py` file. Making a copy of this function is a good starting point for implementing a yield surface.

The steps taken in the workflow will be dissected for explanation:

**Function definition**

The function can be adjusted in any way, but atleast having the path for the dataset, output path and plot path is recommended.
```
def fit_example_yield_surface(dataset_path: str, output_path: str, plot_path: str) -> ExampleYieldSurface:
```

**Read the dataset of yield points**

The `read_data_points()` function can be used to read the dataset in the expected format.
```
def fit_example_yield_surface(dataset_path: str, output_path: str, plot_path: str) -> ExampleYieldSurface:
    data_set = read_yield_points(dataset_path)
```

**Initialize an empty yield surface and optimize it**

In the `example_yield_surface`, `some_constant` needs to be set when initializing it. Replace `ExampleYieldSurface` with the class name of the new yield surface (i.e. `MyYieldSurface`)
```
def fit_example_yield_surface(dataset_path: str, output_path: str, plot_path: str) -> ExampleYieldSurface:
    ...
    
    yield_surface_to_fit = ExampleYieldSurface(some_constant = 5)

    example_yield_surface = fit_surface(yield_surface_to_fit, data_set)
```
If no constants need to be set, the initialization would just be `MyYieldSurface()`

`fit_yield_surface()` will handle the entire process of fitting the coefficients in the yield surface.

**Write the fitted coefficients to a file and plot the surface**

```
def fit_example_yield_surface(dataset_path: str, output_path: str, plot_path: str) -> ExampleYieldSurface:
    ...

    example_yield_surface.write_to_file(output_path, example_yield_surface.mean_square_error_stress)

    make_plot_yield_surface(example_yield_surface, data_set, plot_path)
```

#### Add `my_yield_surface` to the list of options in the `fit_yield_surface()` function
Finally, the only thing left to do is adding the new yield surface to the list of options.

This is done by adding the name of `my_yield_surface` to the `match`/`case` block inside of the `fit_yield_surface()` function and referring to the workflow that was created in the previous step. For the case of the `ExampleYieldSurface` this is done in the following way:
```
def fit_yield_surface(yield_surface_name: str, dataset_path: str, output_path: str, plot_path: str) -> YieldSurfaces:
    ...

    match yield_surface_name:
        ...
        case "example_yield_surface":
            return fit_example_yield_surface(dataset_path, output_path, plot_path)

```

With this, the yield surface should now be correct working.
