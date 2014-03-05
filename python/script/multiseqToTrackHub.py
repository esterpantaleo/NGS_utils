""" 
multiseqToTrackHub.py - plot multiseq output in a track hub in the UCSC genome browser
=========================================================================================

:Author: Ester Pantaleo
:Date: |today|
:Tags: Genomics NGS Intervals Plot multiseq trackHub

Purpose
-------

plot multiseq output in a track hub in the UCSC genome browser

The script requires the executables :file:`wigToBigWig` :file:`bedToBigBed` to be in the user's PATH 

Usage
-----

Type::

   python multiseqToTrackHub.py --assembly hg19  chr1:99614721-99745792

to read multiseq output at chr1:99614721-99745792

Type::
   
   python multiseqToTrackHub.py --help

for command line help.

Command line options
--------------------

"""

import os
import sys
import numpy as np
import argparse
import tempfile
import NGS_utils.utils
import shutil
#import subprocess
import warnings

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--assembly", action="store", 
                        help="genome assembly that reads "
                        "were mapped to (e.g. hg18)", default="hg19")

    parser.add_argument("--mountpoint", action="store",
                        help="path to the directory where "
                        "the track hub folder will be saved in. This directory should be "
                        "associated with an http address or an ftp address ",
                        default=os.environ['MOUNTPOINT_PATH'])

    parser.add_argument("--http_address", action="store", 
                        help="http or ftp address associated with the mountpoint ",
                        default=os.environ['MOUNTPOINT_HTTP_ADDRESS'])

    parser.add_argument("--hub_name", action="store",
                        metavar="HUB_NAME",
                        help="name of the track (it could contain a path, "
                        "in which case the path will be relative to the mountpoint). "
                        "this string can be set to any value", default="multiseq")

    parser.add_argument("--multiseq_folder", action="store",
                        metavar="MULTISEQ_FOLDER",
                        help="path to the folder containing results from multiseq; this script requires "
                        "output from multiseq to be in the format effect_mean_var.txt.gz where first "
                        "column is effect and second column variance", 
                        default="./results_run_multiseq/")

    parser.add_argument("region", action="store",
                        metavar="REGION", 
                        help="a locus (e.g. chr1:2345-234567) ")

    parser.add_argument("chrom_file", action="store",
                        metavar="CHROM_FILE",
                        help="path to the file containing chromosomes names and lengths")
    
    args = parser.parse_args()
    
    return args

def main():
    args = parse_args()
    ngs = NGS_utils.utils.NGS(assembly=args.assembly)

    split_region = args.region.replace(':',' ').replace('-',' ').split()
    if (len(split_region) != 3):
           sys.exit("invalid region: example of a valid region is chr1:2345-234567 ")
    chrom = split_region[0]
    locus_start = split_region[1]
    locus_end = split_region[2]
    hub_dir = os.path.join(args.mountpoint, args.hub_name)
    hub_name_string = args.hub_name.replace("/",".")     
    if not os.path.exists(hub_dir):
        os.makedirs(hub_dir)
    assembly_dir = os.path.join(hub_dir, args.assembly)
    if not os.path.exists(assembly_dir):
        os.mkdir(assembly_dir)
 
    tmpdir = tempfile.mkdtemp()

    multiseq_folder = os.path.join(args.multiseq_folder, ".".join([chrom,locus_start,locus_end]))
    multiseq_file = os.path.join(multiseq_folder, "effect_mean_var.txt.gz")
    #create bigWig file with mean
    mean_track = os.path.join(assembly_dir, "mean_track.bw")

    cmd = "".join(["(echo fixedStep chrom=",
                   chrom,
                   " start=",
                   locus_start,
                   " step=1 ; zcat ",
                   multiseq_file,
                   " | awk '{print $1}' ) | wigToBigWig stdin ",
                   args.chrom_file,
                   " ",
                   mean_track])
    #print cmd
    os.system(cmd)
    #retcode = subprocess.call(cmd.split(), shell=True)
    #if retcode != 0:
    #    warnings.warn("create bigWig file with mean: wigToBigWig terminated with signal: %i" % -retcode)


    #create bigWig file with mean+2sd
    mean_plus_2sd_track = os.path.join(assembly_dir, "mean_plus_2sd_track.bw")
    cmd = "".join(["(echo fixedStep chrom=",
                   chrom,
                   " start=",
                   locus_start,
                   " step=1 ; zcat ",
                   multiseq_file,
                   " | awk '{print $1+2*sqrt($2)}' ) | wigToBigWig stdin ",
                   args.chrom_file,
                   " ",
                   mean_plus_2sd_track])
    #print cmd
    os.system(cmd)
    #retcode = subprocess.call(cmd.split(), shell=True)
    #if retcode != 0:
    #    warnings.warn("wigToBigWig terminated with signal: %i" % -retcode)
        
        
    #create bigWig file with mean-2sd
    mean_minus_2sd_track = os.path.join(assembly_dir, "mean_minus_2sd_track.bw")
    cmd = "".join(["(echo fixedStep chrom=",
                   chrom,
                   " start=",
                   locus_start,
                   " step=1 ; zcat ",
                   multiseq_file,
                   " | awk '{print $1-2*sqrt($2)}' ) | wigToBigWig stdin ",
                   args.chrom_file,
                   " ",
                   mean_minus_2sd_track])
    #print cmd
    os.system(cmd)
    #retcode = subprocess.call(cmd.split(), shell=True)
    #if retcode != 0:
    #    warnings.warn("create bigWig file with mean-2sd: wigToBigWig terminated with signal: %i" % -retcode)
    
    #create bigBed file with significant regions
    multiseq_bed_file = os.path.join(multiseq_folder, "multiseq.effect.2sd.bed")
    #check if bed file is empty
    no_bed=True
    if (os.path.getsize(multiseq_bed_file) > 0):
    #retcode = subprocess.call(cmd.split(), shell=True)
    #if retcode != 0:  
    #    warnings.warn("conversion of effect file into bed file terminated with signal: %i" % -retcode)
        no_bed=False
        multiseq_peaks_track = os.path.join(assembly_dir, "multiseq_bed_file.bb")
        cmd = " ".join(["bedToBigBed",
                        multiseq_bed_file,
                        args.chrom_file,
                        multiseq_peaks_track])
        #print cmd
        os.system(cmd)
        #retcode = subprocess.call(cmd.split(), shell=True)
        #if retcode != 0:
        #    warnings.warn("create bigBed file with significant regions : bedToBigBed terminated with signal: %i" % -retcode)
        
    #clean
    shutil.rmtree(tmpdir)

    #make track hub
    #write genomes file
    trackdb_file = os.path.join(assembly_dir, 'trackDbFile.txt')
    f = open(os.path.join(hub_dir, 'genomes.txt'), 'w')
    f.write(" ".join(['genome', args.assembly]))
    f.write("\n")
    f.write("".join(['trackDb ', args.assembly, "/trackDbFile.txt"]))
    f.write("\n")
    f.close()
    #write hub file
    f = open(os.path.join(hub_dir, 'hub.txt'), 'w')
    f.write(" ".join(['hub', hub_name_string]))
    f.write("\n")
    f.write(" ".join(['shortLabel', hub_name_string]))
    f.write("\n")
    f.write(" ".join(['longLabel', hub_name_string]))
    f.write("\n")
    f.write("genomesFile genomes.txt\n")
    f.write("email esterpantaleo@gmail.com\n")
    f.close()
    #write trackdb_file
    f = open(os.path.join(hub_dir, trackdb_file), 'w')
    #plot effect size
    f.write("".join(["track SuperTrack\n",
                     "shortLabel multiseq\n",
                     "longLabel Plot of multiseq effect 2 sd\n",
                     "superTrack on none\n",
                     "priority 1\n\n"]))
    f.write("".join(["track CompositeTrack\n",
                     "container multiWig\n",
                     "configurable on\n",
                     "shortLabel Effect\n",
                     "longLabel multiseq\n",
                     "visibility full\n",
                     "type bigWig\n",
                     "autoScale on\n",
                     "aggregate transparentOverlay\n",
                     "windowingFunction mean\n",
                     "superTrack SuperTrack full\n",
                     "showSubtrackColorOnUi on\n",
                     "smoothingWindow off\n",
                     "dragAndDrop subtracks\n\n"]))
    shortLabel=["Mean", "MeanPlus2Sd", "MeanMinus2Sd"]
    longLabel=["multiseq mean effect", "multiseq effect mean - 2 * se", "multiseq effect mean + 2 * se"]
    bigDataUrl=["mean_track.bw", "mean_plus_2sd_track.bw", "mean_minus_2sd_track.bw"]
    color=["0,0,0", "0,255,0", "0,255,0"]
    for i in [0,1,2]:
        f.write("".join(["track Subtrack", str(i), "\n"]))
        f.write("type bigWig\n")
        f.write(" ".join(["shortLabel", shortLabel[i]]))
        f.write("\n")
        f.write(" ".join(["longLabel", longLabel[i]]))
        f.write("\n")
        f.write("parent CompositeTrack\n")
        f.write("graphType points\n")
        f.write("visibility full\n")
        f.write(" ".join(["bigDataUrl", bigDataUrl[i]]))
        f.write("\n")
        f.write(" ".join(["color", color[i]]))
        f.write("\n\n")

    #plot significant region
    if (no_bed==False):
        f.write("track SuperTrackBed\n")
        f.write("shortLabel multiseq_signal\n")
        f.write("longLabel multiseq signal\n")
        f.write("superTrack on none\n")
        f.write("priority 2\n\n")
        
        f.write("track signal1\n")
        f.write("type bigBed\n")
        f.write("shortLabel multiseq_signal\n")
        f.write("longLabel multiseq signal 2sd\n")
        f.write("parent SuperTrackBed\n")
        f.write("visibility full\n")
        f.write("bigDataUrl multiseq_bed_file.bb\n")
        f.write("color 255,0,0\n")
    f.close()

    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(args.http_address, args.hub_name, 'hub.txt')
    print "note: center your genome browser around %s and make track visible" %args.region

main()
