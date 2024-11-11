

# Local packages
from ....common_classes.problem_definition import ProblemDefinition

def read_manual_stress_states(problem_definition: ProblemDefinition) -> dict[str, dict[str, bool]]:

    required_results: dict[str, dict[str, bool]] = dict()
    required_results["yield_surface"] = dict()

    stress_states_xx = problem_definition.yield_surface.stress_x_x
    stress_states_yy = problem_definition.yield_surface.stress_y_y
    stress_states_zz = problem_definition.yield_surface.stress_z_z
    stress_states_xy = problem_definition.yield_surface.stress_x_y
    stress_states_xz = problem_definition.yield_surface.stress_x_z
    stress_states_yz = problem_definition.yield_surface.stress_y_z

    for state in range(len(stress_states_xx)):
        stress_xx = stress_states_xx[state]
        stress_yy = stress_states_yy[state]
        stress_zz = stress_states_zz[state]
        stress_xy = stress_states_xy[state]
        stress_xz = stress_states_xz[state]
        stress_yz = stress_states_yz[state]

        stress_xx_string = "xx=" + str(stress_xx).replace(".", "-")
        stress_yy_string = "yy=" + str(stress_yy).replace(".", "-")
        stress_zz_string = "zz=" + str(stress_zz).replace(".", "-")
        stress_xy_string = "xy=" + str(stress_xy).replace(".", "-")
        stress_xz_string = "xz=" + str(stress_xz).replace(".", "-")
        stress_yz_string = "yz=" + str(stress_yz).replace(".", "-")

        field_name = "stress" + "_" + stress_xx_string + "_" + stress_yy_string + "_" + stress_zz_string + "_" + stress_xy_string + "_" + stress_xz_string + "_" + stress_yz_string

        required_results["yield_surface"][field_name] = True

    return required_results