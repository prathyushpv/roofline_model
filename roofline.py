import matplotlib.pyplot as plt
import pylab
import numpy as np
from matplotlib.ticker import ScalarFormatter
import matplotlib.ticker as ticker
import logging
from perf import run_command
from perf import Perf
import json 
from logger import create_logger
from datetime import datetime

# https://stackoverflow.com/questions/21920233/matplotlib-log-scale-tick-label-number-formatting

class Roofline:
    def __init__(self, peak_flops, peak_bandwidth):
        self.peak_flops = peak_flops
        self.peak_bandwidth = peak_bandwidth
        self.commands = []
        self.prereqs = []
        self.logger = logging.getLogger("main_log")
        self.logger.propagate = False

        self.data = []

        # plt.plot([self.peak_flops/self.peak_bandwidth, 10],[self.peak_flops, self.peak_flops])
        # plt.ylabel('some numbers')

        fig = plt.figure()
        self.ax = fig.add_subplot(1, 1, 1)
        self.ax.set_yscale('log', basey=2)
        self.ax.set_xscale('log', basex=2)
        

        self.ax.axis([0.25, 4000, 0.5, 128])
        for axis in [self.ax.xaxis, self.ax.yaxis]:
            formatter = ScalarFormatter()
            formatter.set_scientific(False)
            axis.set_major_formatter(formatter)


        self.ax.yaxis.grid()
        self.ax.plot([self.peak_flops/self.peak_bandwidth, 4000],[self.peak_flops, self.peak_flops], color='red', lw=2)
        # TODO Memory line correction
        self.ax.plot([0, self.peak_flops/self.peak_bandwidth],[0, self.peak_flops], color='red', lw=2)

    def add_command(self, command, name):
        self.commands.append({"command":command, "name":name})

    def add_prereq(self, command):
        self.prereqs.append(command)

    def run(self):
        counters = ['instructions', 
                    'L1-dcache-loads', 
                    'L1-dcache-stores', 
                    'LLC-load-misses', 
                    'LLC-store-misses',
                    ]

        for prereq in self.prereqs:
            self.logger.info("Running prereq %s" % prereq)
            run_command(prereq.split(), self.logger)

        for task in self.commands:
            name = task["name"]
            command = task["command"]
            self.logger.info("Running command %s" % name)
            p = Perf()
            p.set_command(command)
            p.set_counters(counters)
            p.set_repeat_factor(1)
            result = p.run()
            if result is not None:
                result["name"] = name
            self.data.append(result)

    def add_data(self, filename):
        with open(filename) as fp:
            self.data = json.load(fp)
        self.logger.info("Got data " + json.dumps(self.data, indent=4))

    def dump_data(self):
         filename = "data_%s.json" % datetime.now().strftime('%Y_%m_%d__%H_%M_%S')
         with open(filename, "w") as fp:
             json.dump(self.data, fp, indent=4)

    def plot_workloads(self):
        for workload in self.data:
            name = workload["name"]

            operations = workload["instructions"] - workload["L1-dcache-loads"] - workload["L1-dcache-stores"] 
            data_transfer = (workload["LLC-load-misses"] + workload["LLC-store-misses"]) * 64
            operational_intensity = float(operations) / float(data_transfer)

            gflops = (operations / float(workload["time"]))/1000000000
            print (name, operational_intensity, gflops)
            print json.dumps(workload)
            self.ax.plot(operational_intensity, gflops, "bo")
            self.ax.annotate(name, (operational_intensity, gflops))



    def show(self):
        plt.show()
    

# logger = create_logger()
# r = Roofline(64, 15)
# r.add_data("data.json")
# r.add_prereq("ls -ltr")
# r.add_command("/home/prathyushpv/work/High_Performance_GEMM/mmm", "mmm")
# # r.add_command("/home/prathyushpv/work/High_Performance_GEMM/mmm", "mmm")
# r.run()
# r.dump_data()
# r.plot_workloads()
# r.show()
