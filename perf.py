import subprocess
from logger import create_logger
from datetime import datetime
import sys
from collections import OrderedDict 

class ReturnException(Exception):
    def __init__(self, return_value):
        self.return_value = return_value


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line
    for stderr_line in iter(popen.stderr.readline, ""):
        yield stderr_line
    popen.stdout.close()
    return_code = popen.wait()
    raise ReturnException(return_code)


def run_command(command, logger=None):
    if logger is None:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process.returncode, process.stdout.read() + process.stderr.read()
    else:
        output = ""
        logger.info("------Executing command " + " ".join(command) + "------")
        try:
            for line in execute(command):
                logger.debug(line.rstrip())
                output += line
        except ReturnException as re:
            logger.info("------Finished command " + " ".join(command) + "-------")
            return re.return_value, output


class Perf:
    """
        Class to measure performance counters using the perf command in linux
    """
    def __init__(self, counters=None, command=None, log_handle=None):
        self.counters = counters
        self.command = command
        self.repeat_factor = 5
        logname = "perf_{time}.log"
        now = datetime.now()
        logname = logname.format(time = now.strftime("%m_%d_%Y__%H_%M_%S"))
        if log_handle is None:
            self.logger = create_logger(logname)
        else:
            self.logger = log_handle

    def set_counters(self, counters):
        self.counters = counters
    
    def set_command(self, command):
        self.command = command

    def set_logger(self, logger):
        self.logger = logger

    def set_repeat_factor(self, repeat_factor):
        self.repeat_factor = repeat_factor

    def run(self):
        counters_to_measure = list(self.counters)
        result = OrderedDict()

        while counters_to_measure:
            perf_command = ["perf", "stat", "-x", ";", "-r", "5", "-e",
                            ",".join(counters_to_measure)]

            perf_command.extend(self.command.split())
            return_value, output = run_command(perf_command, self.logger)
            if return_value != 0:
                return None
            output = output.split("\n")

            for counter in self.counters:
                for line in output:
                    if counter in line:
                        fields = line.split(";")
                        value = fields[0]
                        key = fields[2]
                        if "<not counted>" in value:
                            self.logger.info("Counter %s is not counted " % key)
                        else:
                            value = int(value.replace(",", ""))
                            counters_to_measure.remove(key)
                        result[key] = value
        return result
if __name__ == "__main__":
    p = Perf([  'L1-dcache-load-misses', 
                'LLC-load-misses',
                'l2_rqsts.miss',
                'dtlb_load_misses.miss_causes_a_walk',
                'dtlb_load_misses.stlb_hit',
                'dtlb_load_misses.walk_active', 
                'dtlb_load_misses.walk_completed'],
                "ls")
    result = p.run()
    print(result)
