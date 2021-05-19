from anomaly_detection.utilities.custom_print import print_ts as print
import os

def run_shell(command,log_command=True):
    if log_command:
        print(command)
    retval = os.system(command)
    if retval!=0:
        print('Unexpected return value "%d" from command:' % retval)
        print(command)
        print('Main process will exit now.')
        exit() 
