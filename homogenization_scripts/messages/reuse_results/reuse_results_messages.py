# system packages
import textwrap
import click 

class Reuse:

    class Banners:
        def start_resuse_section():
            print("")
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print(f"                     Reuse of existing simulation results                      ")
            print(f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("")

    def invalid_results_database_detected(self, reasons_invalid) -> None: # type: ignore
        print("There exists a results database file but it does not seem to be valid!")
        print("")
        reading_errors_dict: str = reasons_invalid # type: ignore
        for reading_error_section in reading_errors_dict: # type: ignore
            for reading_error_entry in range(len(reading_errors_dict[reading_error_section])): # type: ignore
                if isinstance(reading_errors_dict[reading_error_section][reading_error_entry], dict):  # type: ignore
                    value_error_dict = reading_errors_dict[reading_error_section][reading_error_entry]   # type: ignore
                    for value in value_error_dict:   # type: ignore
                        print(textwrap.fill(f"In the section {reading_error_section}, for setting {value} the stored result does not match the expectation: {''.join(value_error_dict[value])}", width=80))   # type: ignore
                else:
                    print(textwrap.fill(f"The section {reading_error_section} is not valid: {''.join(reading_errors_dict[reading_error_section][reading_error_entry])}", width=80)) # type: ignore

    def general_section_settings_compatible(self) -> None:
        print(textwrap.fill("The simulation settings have been compared against already existing results (grid_file path, material_file path, N_increments, etc) and these results seem compatible.",width=80))

    def general_section_settings_changed(self, reasons_general_mismatch: list[str]) -> None:
        print(textwrap.fill(f"Settings from the general section have been changed. The settings that have been changed: {"".join(reasons_general_mismatch)}.", width=80))

    def detected_incompatible_settings_simulation_type(self, simulation_type: str, mismatch_list: bool | list[str]):
        print(textwrap.fill(f"Existing results for the simulation type {simulation_type} are not compatible with current simulation settings: {mismatch_list}", width=80))

    def moved_results_to_backup_folder(self, backup_folder_path: str) -> None:
        print(f"Moved the stored results to a backup folder at: {backup_folder_path}")
        print(textwrap.fill("Moving this folder back to the results folder restores the previous state.", width=80))

    def ask_to_reuse_existing_results(self, simulation_type: str, reuseable_results: list[str]) -> bool:
        print("")
        print(textwrap.fill(f"Results exist for [{simulation_type}] that seem to have been created under similar settings.", width=80))
        print(textwrap.fill(f"Fields that can be reused: {reuseable_results}.", width=80))
        print("")
        print(textwrap.fill("This check is does not chatch all the ways the simulations settings can change, make sure important settings did not actually change.", width=80))
        print("")
        ask_to_reuse_simulation_results = "Do you want to reuse these simulation results? Default = Yes"
        reuse_simulation_results = click.confirm(ask_to_reuse_simulation_results, default=True)
        print("")
        return reuse_simulation_results

    def ask_to_move_single_or_all_values_in_simulation_type(self, simulation_type: str, removed_fields: list[str]) -> bool:
        print("The stored results that are not reused will be moved to a backup folder.")
        print(f"Should all results of the {simulation_type} type be moved to the backup folder?")
        print(textwrap.fill(f"If you answer no, only the fields: {removed_fields} will be moved",width=80))
        move_all_results_question = f"Move all {simulation_type} results? Default = Yes "
        move_all_results = click.confirm(move_all_results_question, default=True)
        print("")
        return move_all_results