import subprocess
from logger import create_logger
from datetime import datetime
import sys
from collections import OrderedDict 
from timeit import default_timer as timer
from logging import getLogger
from glob import glob
from time import sleep
from threading import Thread
import os 
import json 
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
    def __init__(self, counters=None, command=None, name=None, log_handle=None):
        self.counters = counters
        self.command = command
        self.repeat_factor = 5
        # logname = "perf_{time}.log"
        # now = datetime.now()
        # logname = logname.format(time = now.strftime("%m_%d_%Y__%H_%M_%S"))
        # if log_handle is None:
        #     self.logger = create_logger(logname)
        # else:
        #     self.logger = log_handle
        self.logger = getLogger("main_log")
        self.name = name
        self.phase_dir = "phases"

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
            perf_command = ["perf", "stat", "-x", ";", "-r", str(self.repeat_factor), "-e",
                            ",".join(counters_to_measure)]

            perf_command.extend(self.command.split(" "))
            start = timer()
            return_value, output = run_command(perf_command, self.logger)
            end = timer()
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
            result["time"] = float(end - start) / self.repeat_factor
        return result
    
    def poll_output(self, process):
        print "Printing the lines"
        for stdout_line in iter(process.stdout.readline, ""):
           self.logger.debug(stdout_line.rstrip())
        for stderr_line in iter(process.stderr.readline, ""):
           self.logger.debug(stderr_line.rstrip())
        
        
    def parse_output(self, output, phase_name):
        output = output.split("\n")
        result = OrderedDict()
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
                    result[key] = value
        #result["time"] = float(end - start) / self.repeat_factor
        result["name"] = self.name
        result["phase"] = phase_name
        return result
        
    def set_phase_dir(self, directory):
        self.phase_dir = directory
        
    def get_phase_counters(self, cmd):
        total_phases = 0
        not_counted = False
        while cmd.poll() is None:
            self.logger.info("Checking file")
            while cmd.poll() is None and not glob(self.phase_dir+"/*"):
                sleep(1)
            if cmd.poll() is not None:
                break
            total_phases += 1
            
            phase_name = glob(self.phase_dir+"/*")[0]
            pid = open(phase_name,"r").read().strip()
            if not pid:
               pid = cmd.pid
            result = None
            if phase_name in self.result.keys():
                result = self.result[phase_name]
            else:
                result = OrderedDict()
                
            counters_left = [item for item in self.counters if item not in result.keys()]
            self.logger.info("File found")
            self.logger.info("Coutners measured are " + ",".join(result.keys()))
            self.logger.info("Measuring counters for the phase :" + phase_name)
            self.logger.info("counters left to measure are : " + ",".join(counters_left))
            cmd_start_perf = ["perf", "stat" ,"-x", ";", "-e", 
                              ",".join(counters_left), "-p", str(pid)]
            print " ".join(cmd_start_perf) 
            start = timer()
            perf = subprocess.Popen(cmd_start_perf, stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
                                    
            while cmd.poll() is None and glob(phase_name):
                sleep(1)
            #if cmd.poll() is not None:
            #    break
            self.logger.info("File deleted")
            end = timer()
            #perf.kill()
            os.system("pkill -2 perf")
            perf.wait()
            output = perf.stdout.read() + perf.stderr.read()
            print output
            output = output.split("\n")
            
            for counter in counters_left:
                for line in output:
                    if counter in line:
                        fields = line.split(";")
                        value = fields[0]
                        key = fields[2]
                        if "<not counted>" in line:
                            self.logger.info("Counter %s is not counted " % key)
                            not_counted = True
                            #result[key] = 0
                        else:
                            value = int(value.replace(",", ""))
                            result[key] = value
            #result["time"] = float(end - start) / self.repeat_factor
            result["name"] = self.name
            result["phase"] = phase_name
            result["time"] = float(end - start)
            self.result[phase_name] = result
            #self.result.append(self.parse_output(perf_out, phase_name))
        print json.dumps(self.result, indent=4)
        return not_counted

        
        
    def run_phased(self):
        self.result = {}
        not_counted = True
        while not_counted:
            self.logger.info("Executing phases")
            cmd = subprocess.Popen(self.command.split(" "), stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, 
                                     universal_newlines=True, bufsize=1)    
            poll = Thread(target=self.poll_output, args=(cmd,))
            poll.start()
            not_counted = self.get_phase_counters(cmd)
            cmd.wait()
        return self.result.values()

        
        
        

        
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
