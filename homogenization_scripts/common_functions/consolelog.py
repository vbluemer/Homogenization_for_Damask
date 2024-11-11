import sys
import os
# from ..common_classes import problem_definition

# Suppressing stdout keeps messages writen to stdout (most information you get back in the console) to be shown.
# This helps to keep the console window clean from unnecessary information.
# stderr remains unaffected: errors should still be shown!
# Suppression can be bypassed by enabling the debug option in the problem definition.
def suppress_console_logging():
    debugging_mode = False

    if not(debugging_mode):
        sys.stdout = open(os.devnull, 'w')

def restore_console_logging():
    sys.stdout = sys.__stdout__