class ReusedResults:
    general_settings_match: bool
    reasons_general_settings_refused: list[str]
    reused_values: dict[str, dict[str, bool]]
    reevaluated_simulation_type: dict[str, bool]
    reason_reevaluated_simulation_type: dict[str, list[str]]

    def __init__(self, results_found: bool):
        self.existing_results_found = results_found

    def general_settings(self, general_settings_match: bool, reasons_general_settings_refused: list[str]):
        self.general_settings_match = general_settings_match
        self.reasons_general_settings_refused = reasons_general_settings_refused
        self.reused_values = dict()
        self.reevaluated_simulation_type = dict()
        self.reason_reevaluated_simulation_type = dict()

    def add_reused_value(self, simulation_type: str, field_name: str):
        if self.reused_values.get(simulation_type) == None:
            self.reused_values[simulation_type] =  dict()
        self.reused_values[simulation_type][field_name] = True
    
    def add_reevaluated_simulation_type(self, simulation_type: str, reason: list[str]):
        self.reevaluated_simulation_type[simulation_type] = True
        self.reason_reevaluated_simulation_type[simulation_type] = reason