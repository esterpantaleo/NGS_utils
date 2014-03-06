#! /usr/bin/env python                                                                                  
"""
h52bigwig.py - convert hdf5file to bigwig file
==============================================

:Author: Ester Pantaleo
:Date: |today|
:Tags: Genomics NGS Intervals Conversion HDF5 WIGGLE

Purpose
-------

convert an hdf5 file in genome_db to a bigwig file.   

The script requires the executable :file:`wigToBigWig` to be in the user's PATH

Usage
-----

Type::

   python h52bigwig.py in.h5 out.bigwig

to convert the :term:`hdf5` file file:`in.h5` to :term:`bigwig` format 
and save the result in :file:`out.bigwig`.

Type::

   python h52bigwig.py --help

for command line help.

Command line options
--------------------

""" 

import os
import numpy as np
import NGS_utils.utils 
import sys
import re
import argparse
import subprocess
import warnings

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--assembly", help="genome assembly that reads "
                        "were mapped to (e.g. hg18)", default="hg19")

    parser.add_argument("h5_track", action="store",
                        metavar="H5_TRACK",
                        help="path to the hdf5 track (relative to genome_db)")

    parser.add_argument("chrom_file", action="store",
                        metavar="CHROM_FILE", 
                        help="path to the file containing chromosomes names and lengths") 

    parser.add_argument("bigWig_track", metavar="BIGWIG_TRACK", action="store",
                        help="name of new bigWig track")

    args = parser.parse_args()

    return args

def main():
    args = parse_args()

    ngs = NGS_utils.utils.NGS(assembly=args.assembly)
    mytrack = ngs.open_track(args.h5_track)
 
    chromosomes = np.loadtxt(args.chrom_file)
    dim=chromosomes.shape
    #write wiggle file
    tmpfile_wig = "".join([args.bigWig_track, "_tmp"])
    f = open(tmpfile_wig, 'w')
    for i in range(1, dim[1]):
        myvalues = mytrack.get_nparray(chromosomes[i,1], 1, chromosomes[i,2])
        print "processing chromosome %s" % chromosomes[i,1]
        #wiggle files are 0 based
        f.write("fixedStep chrom=%s start=1 step=1\n" % chromosomes[i,1])
        f.write("\n".join(map(str, myvalues)))
        f.write("\n")
        break
    f.close()
        
    #convert wiggle file into bigWig
    retcode = subprocess.call(" ".join(("wigToBigWig",
                                         tmpfile_wig,
                                         args.chrom_file,
                                         args.bigWig_track)),
                              shell=True)
    if retcode != 0:
        warnings.warn("wigToBigWig terminated with signal: %i" % -retcode)
    else:
        os.remove(tmpfile_wig) 
 
main()
