import sys
import tempfile
import os
import logging
import psutil
import subprocess

from aspmc.compile.cnf import CNF, src_path
import aspmc.compile.dtree as dtree

import aspmc.signal_handling as my_signals
import aspmc.main

from aspmc.config import config

config["decot"] = "1"

logging.basicConfig(stream=sys.stdout, level="DEBUG")
logger = aspmc.main.logger
logger.setLevel("DEBUG")

cnf = CNF(sys.argv[2])

cnf_fd, cnf_tmp = tempfile.mkstemp()
my_signals.tempfiles.add(cnf_tmp)
my_signals.tempfiles.add(cnf_tmp + '.nnf')

if sys.argv[1] == "d4":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.to_stream(cnf_file)
    CNF.compile_single(cnf_tmp, knowledge_compiler="d4")
elif sys.argv[1] == "c2d":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.to_stream(cnf_file)
    d3 = dtree.TD_dtree(cnf, solver = "flow-cutter", timeout = "10")
    d3.write(cnf_tmp + '.dtree')
    my_signals.tempfiles.add(cnf_tmp + '.dtree')
    CNF.compile_single(cnf_tmp, knowledge_compiler="c2d")
    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        logger.debug(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")
    os.remove(cnf_tmp + ".dtree")
    my_signals.tempfiles.remove(cnf_tmp + '.dtree')
elif sys.argv[1] == "sharpsat-td":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.write_kc_cnf(cnf_file)
    CNF.compile_single(cnf_tmp, knowledge_compiler="sharpsat-td")
    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        print(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")
elif sys.argv[1] == "sharpsat-td-e":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.write_kc_cnf(cnf_file)
    available_memory = max(psutil.virtual_memory().available//1024**2 - 125, 1000)
    decot = 10
    p = subprocess.Popen(["./sharpSAT_E", "-dDNNF", "-decot", str(decot), "-decow", "10000", "-cs", str(available_memory//2), cnf_tmp, "-dDNNF_out", cnf_tmp + ".nnf"], cwd=os.path.join(src_path, "sharpsat-td/bin/"), stdout=subprocess.PIPE)
    for line in iter(p.stdout.readline, b''):
        line = line.decode()
        print(line[:-1])
    p.wait()
    p.stdout.close()

    if p.returncode != 0:
        logger.error(f"Knowledge compilation failed with exit code {p.returncode}.")
        exit(-1) 

    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        print(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")


os.remove(cnf_tmp)
my_signals.tempfiles.remove(cnf_tmp)
os.remove(cnf_tmp + ".nnf")
my_signals.tempfiles.remove(cnf_tmp + '.nnf')
