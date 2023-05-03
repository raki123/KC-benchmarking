#!/usr/bin/env python3
import matplotlib
import matplotlib
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

import os
folders = [ "plots" ]

for folder in folders:
    if not os.path.exists(folder):
        os.mkdir(folder)

def MatplotlibClearMemory():
    allfignums = matplotlib.pyplot.get_fignums()
    for i in allfignums:
        fig = matplotlib.pyplot.figure(i)
        fig.clear()
        matplotlib.pyplot.close(fig)


paperheight = 11.7
paperwidth = 8.3
margin = 1.0
golden = (1 + 5 ** 0.5) / 2
fig_width = paperwidth - 2*margin
fig_height = fig_width/golden

#labels
TIME_LABEL = "runtime in seconds"
INSTANCES_LABEL = "number of instances"
# LABEL_SIZE = 12

markers = ['.',',','o','v','^','<','>','1','2','3','4','8','s','p','P','*','h','H','+','x','X','D','d','|','_']
descriptions = ['point', 'pixel', 'circle', 'triangle_down', 'triangle_up','triangle_left',
                'triangle_right', 'tri_down', 'tri_up', 'tri_left', 'tri_right', 'octagon',
                'square', 'pentagon', 'plus (filled)','star', 'hexagon1', 'hexagon2', 'plus',
                'x', 'x (filled)','diamond', 'thin_diamond', 'vline', 'hline']

class Instance(object):
    pass

setting_to_label = { 
                        "c2d" : "c2d", 
                        "d4" : "d4",
                        "sharpsat-td" : "sharpSAT-TD"
                    }
setting_to_plot_args = { 
                        "c2d" : {"marker" : "s", "markevery" : 5, "markerfacecolor" : "none"},
                        "d4" : {"marker" : "*", "markevery" : 5},
                        "sharpsat-td" : {"marker" : "x", "markevery" : 5}
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
                if instance.time >= 1800:
                    instance.time = 1850
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
    plt.plot(range(len(data)), data, label=setting_to_label[setting], **setting_to_plot_args[setting])
    print(sum(1 for t in data if t < 1800), setting)

plt.legend(loc="upper left")
plt.xlabel(INSTANCES_LABEL)
plt.ylabel(TIME_LABEL)
plt.ylim(0,1800)
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
            plt.plot([0.5,1850], [0.5,1850], color="red")
            plt.scatter(time_per_setting[setting], time_per_setting[setting2], s=1, color="blue")
            plt.xlabel(setting_to_label[setting])
            plt.ylabel(setting_to_label[setting2])
            plt.yscale('log')
            plt.xscale('log')
            plt.ylim(0.5,1850)
            plt.xlim(0.5,1850)
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
