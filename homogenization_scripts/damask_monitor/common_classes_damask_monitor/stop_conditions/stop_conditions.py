
class StopCondition:
    name: str
    yield_condition : str
    yield_value     : float

    

    class Yielding:
        def __init__(self, yield_condition: str, yield_value: float):
            self.name = 'yielding'
            self.yield_condition = yield_condition
            self.yield_value = yield_value

        def __str__(self ):
            return f"Stop condition: stop when yielding is detected, defined by {self.yield_condition} at value {self.yield_value}"
    
    class NoConditions:
        def __init__(self):
            self.name = 'no_conditions'
            self.yield_condition = None
            self.yield_value = None
        def __str__(self ):
            return f"Stop condition: no stopping condition set."
