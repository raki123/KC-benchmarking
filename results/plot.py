#!/usr/bin/env python3
from operator import mod
import matplotlib
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

def MatplotlibClearMemory():
    #usedbackend = matplotlib.get_backend()
    #matplotlib.use('Cairo')
    allfignums = matplotlib.pyplot.get_fignums()
    for i in allfignums:
        fig = matplotlib.pyplot.figure(i)
        fig.clear()
        matplotlib.pyplot.close( fig )
    #matplotlib.use(usedbackend) 


paperheight = 11.7
paperwidth = 8.3
margin = 1.0
golden = (1 + 5 ** 0.5) / 2
fig_width = paperwidth - 2*margin
fig_height = fig_width/golden

#labels
TIME_LABEL = "runtime in seconds"
INSTANCES_LABEL = "number of instances solved"
XWIDTH_LABEL = "X-width"
XDWIDTH_LABEL = "X/D-width"
LABEL_SIZE = 12


class Instance(object):
    pass

setting_to_label = { 
                        "c2d" : "c2d", 
                        "d4" : "d4",
                        "sharpsat-td" : "sharpSAT-TD",
                        "sharpsat-td-mfg" : u"\u2203sharpSAT-TD",
                        "c2d-g" : u"\u2203c2d"
                    }
instances_per_setting = {}
results_file = "KC_basic.xml"
tree = ET.parse(results_file)
root = tree.getroot()

timeout = float(root.find('pbsjob').get('timeout'))
settings = [ setting.get('name') for setting in root.find('system').findall('setting') ]
for setting in settings:
    instances_per_setting[setting] = []

for spec in root.find('project').findall('runspec'):
    for clas in spec:
        for inst in clas:
            for run in inst:
                instance = Instance()
                instance.time = float(run.find('.//measure[@name="time"]').get('val'))
                instance.setting = run.find('.//measure[@name="setting"]').get('val')
                instance.name = run.find('.//measure[@name="instance"]').get('val')
                try:
                    instance.edges = int(run.find('.//measure[@name="d-DNNF-size-edges"]').get('val'))
                    instance.nodes = int(run.find('.//measure[@name="d-DNNF-size-nodes"]').get('val'))
                except:
                    try:
                        cnt = int(run.find('.//measure[@name="unsat_dfour"]').get('val'))
                        if cnt == 0:
                            instance.edges = 0
                            instance.nodes = 0
                        else:
                            instance.edges = int(run.find('.//measure[@name="d-DNNF-size-edges_dfour"]').get('val'))
                            instance.nodes = int(run.find('.//measure[@name="d-DNNF-size-nodes_dfour"]').get('val'))
                    except:
                        instance.edges = 10**10
                        instance.nodes = 10**10

                instances_per_setting[instance.setting].append(instance)

for setting in settings:
    data = []
    for instance in instances_per_setting[setting]:
        data.append(instance.time)
    data.sort()
    plt.plot(range(len(data)), data, label=setting_to_label[setting])

plt.legend(loc="upper left")
plt.xlabel("number of instances")
plt.ylabel("runtime in seconds")
plt.ylim(0,1806)
plt.xlim(1000,1750)
plt.savefig("plots/overall.pdf")
MatplotlibClearMemory()

time_per_setting = { setting : [] for setting in settings }
size_per_setting = { setting : [] for setting in settings }
for setting in settings:
    for instance in instances_per_setting[setting]:
        time_per_setting[setting].append((instance.name, instance.time))
        size_per_setting[setting].append((instance.name, instance.edges))
    time_per_setting[setting].sort(key = lambda tup : tup[0])
    time_per_setting[setting] = [ tup[1] for tup in time_per_setting[setting] ]
    size_per_setting[setting].sort(key = lambda tup : tup[0])
    size_per_setting[setting] = [ tup[1] for tup in size_per_setting[setting] ]


for setting in settings:
    for setting2 in settings:
        if setting != setting2:
            plt.plot([0.5,1806], [0.5,1806], color="red")
            plt.scatter(time_per_setting[setting], time_per_setting[setting2], s=1, color="blue")
            plt.xlabel(setting_to_label[setting])
            plt.ylabel(setting_to_label[setting2])
            plt.yscale('log')
            plt.xscale('log')
            plt.ylim(0.5,1806)
            plt.xlim(0.5,1806)
            plt.savefig(f"plots/scatter_time_{setting}_{setting2}.pdf")
            MatplotlibClearMemory()
            plt.plot([1,10**10], [1,10**10], color="red")
            plt.scatter(size_per_setting[setting], size_per_setting[setting2], s=1, color="blue")
            plt.xlabel(setting_to_label[setting])
            plt.ylabel(setting_to_label[setting2])
            plt.yscale('log')
            plt.xscale('log')
            plt.ylim(1,10**10)
            plt.xlim(1,10**10)
            plt.savefig(f"plots/scatter_size_{setting}_{setting2}.pdf")
            MatplotlibClearMemory()
