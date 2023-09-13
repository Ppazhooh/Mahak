import numpy as np
import os
import time
import sys
import subprocess

def trace_generator (begin_bw, step, end_bw):
    save_name = 'traces/'+str(begin_bw) + '_' + str(step) + '.trace'
    num_packets1 = int(float(begin_bw) * 1000)
    ts_list1 = np.linspace(0, 12000, num=num_packets1, endpoint=False)

    num_packets2 = int(float(end_bw) * 1000)
    ts_list2 = np.linspace(0, 12000, num=num_packets2, endpoint=False) + 12000
    ts_list = np.concatenate((ts_list1, ts_list2), axis=None)

    with open(save_name, 'w') as trace:
        for ts in ts_list:
            trace.write('%d\n' % ts)
    return str(begin_bw) + '_' + str(step) + '.trace'

def open_port_finder (port):
    while True:
        try:
            # Run netstat and grep commands and capture the output
            result = subprocess.check_output(['netstat', '-at'],\
                                                stderr=subprocess.STDOUT,\
                                                text=True)
            grep_result = subprocess.run(['grep', str(port)],\
                                         input=result, stdout=subprocess.PIPE,\
                                         stderr=subprocess.PIPE, text=True)
            
            if grep_result.returncode != 0 or not grep_result.stdout:
                # If grep didn't find a match, the port is free, so break out of the loop
                break
            
            # Increment the port by 10 for the next iteration
            port += 10
        except subprocess.CalledProcessError as e:
            # Handle any errors, such as if the commands return a non-zero exit code
            print(f"Error: {e}")
    return port



# Oracle Query
def oracle_query(X, metric, CC):
    """
    Gets network paramter (X) and desired metric and returns the result metric
    of target CC on the specific paramter set.
    """
    result = np.zeros([1])
    mm_buffer = int(X[0])
    mm_delay = int(X[1])
    mm_bw = int(X[2])
    mm_step = float(X[3])

    # Create a Mahimahi Trace with Specified Bandwidth and Step Size
    trace_dir = trace_generator (mm_bw, mm_step, mm_step*mm_bw )
    # Run the emulation
    initial_port = 45000
    port = open_port_finder (initial_port)
    finish_time = 20
    log_file_name = 'log'
    current_directory = os.getcwd()
    cmd = f"./server-mahimahi {port} {current_directory} {CC} {trace_dir} \
                              {trace_dir} {mm_delay} {log_file_name} \
                              {finish_time} {mm_buffer}"
    os.system(cmd)
    cmd = "sudo killall -9 orca-server-mahimahi client iperf iperf3"
    os.system(cmd)

    # Clean the log file and analyse it
    cmd = "sed -i '$ d' logs/down-log"
    os.system(cmd)
    cmd = './mm-th-delay 500 logs/down-log 1>fig.svg 2>result.txt'
    os.system(cmd)

    # Read the analysis file and convert to desired metrics
    with open("result.txt") as file:
        lines = [line.rstrip() for line in file]

    utilization = float (lines [0])
    delay = float (lines [1])
    mm_delay = float (mm_delay)
    if metric == 'utilization':
        result[0] = utilization
    elif metric == 'first_power':
        a = np.array (delay/mm_delay)
        b = np.array (utilization)
        result[0] = (b)/(a)
    elif metric == 'delay':
        result[0] = np.array (delay/mm_delay)
    else:
        error_message = metric + "is not supported as a metric"
        exit_code = 1
        print("An error occurred:", error_message)
        sys.exit(exit_code)

    return result



# Query Mechanism ( Mahak uses uncertainty)
def GP_regression_std(regressor, X):
    _, std = regressor.predict(X, return_std=True)
    return np.argmax(std)


# Get Regression Result from Trained Regressor
def GP_regression_result(regressor, X):
    mean = regressor.predict(X)
    return mean