#!/usr/bin/env python3
import sys
import tempfile
import os
import logging

from aspmc.compile.cnf import CNF
import aspmc.compile.dtree as dtree

import aspmc.signal_handling as my_signals
import aspmc.main

from aspmc.config import config

config["decot"] = "10"

logging.basicConfig(stream=sys.stdout, level="DEBUG")
logger = aspmc.main.logger
logger.setLevel("DEBUG")

cnf = CNF(sys.argv[2])

cnf_fd, cnf_tmp = tempfile.mkstemp()
my_signals.tempfiles.add(cnf_tmp)
my_signals.tempfiles.add(cnf_tmp + '.nnf')

if sys.argv[1] == "c2d":
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
elif sys.argv[1] == "c2d-g":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.to_stream(cnf_file)
    d3 = dtree.TD_dtree(cnf, solver = "flow-cutter", timeout = "10")
    d3.write(cnf_tmp + '.dtree')
    my_signals.tempfiles.add(cnf_tmp + '.dtree')
    with open(cnf_tmp + ".exist", 'w') as exist_file:
        exist_file.write(f"{len(cnf.auxilliary)} {' '.join( str(v) for v in cnf.auxilliary )}")
    my_signals.tempfiles.add(cnf_tmp + '.exist')
    CNF.compile_single(cnf_tmp, knowledge_compiler="c2d")
    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        logger.debug(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")
    os.remove(cnf_tmp + ".dtree")
    my_signals.tempfiles.remove(cnf_tmp + '.dtree')
    os.remove(cnf_tmp + ".exist")
    my_signals.tempfiles.remove(cnf_tmp + '.exist')
elif sys.argv[1] == "sharpsat-td":
    cnf.auxilliary = set()
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.write_kc_cnf(cnf_file)
    CNF.compile_single(cnf_tmp, knowledge_compiler="sharpsat-td")
    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        print(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")
elif sys.argv[1] == "sharpsat-td-mfg":
    with os.fdopen(cnf_fd, 'wb') as cnf_file:
        cnf.write_kc_cnf(cnf_file)
    CNF.compile_single(cnf_tmp, knowledge_compiler="sharpsat-td")
    with open(cnf_tmp + ".nnf") as ddnnf:
        _, v, e, n = ddnnf.readline().split()
        print(f"d-DNNF size: {v} nodes, {e} edges, {n} variables")



os.remove(cnf_tmp)
my_signals.tempfiles.remove(cnf_tmp)
os.remove(cnf_tmp + ".nnf")
my_signals.tempfiles.remove(cnf_tmp + '.nnf')
