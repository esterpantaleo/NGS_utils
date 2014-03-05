#! /usr/bin/env python

import NGS_utils.utils
import os
import argparse
import warnings
import pandas as pd
import subprocess
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--assembly", help="genome assembly that reads "
                        "were mapped to (e.g. hg18)", default="hg19")

    parser.add_argument("--mountpoint", help="path to the directory where "
                        "the track hub folder will be saved in. This directory should be "
                        "associated with an http address or an ftp address", 
                        default=os.environ['MOUNTPOINT_PATH'])

    parser.add_argument("--http_address", action="store",
                        help="http or ftp address associated with the mountpoint ",
                        default=os.environ['MOUNTPOINT_HTTP_ADDRESS'])

    parser.add_argument("samplesheet", action="store",
                        metavar="SAMPLESHEET",
                        help="path to the samplesheet; the samplesheet "
                        "must contain a column with header h5RelPath "
                        "and a column with header Peaks; "
                        "depending on the size of h5 files "
                        "this code might require a lot of memory")

    parser.add_argument("hub_name", action="store",
                        metavar="HUB_NAME",
                        help="name of the track hub (it could contain a path, "
                        "in which case the path will be relative to the mountpoint). "
                        "this string can be set to any value")

    parser.add_argument("chromosome", action="store",
                        metavar="CHROMOSOME",
                        help="extract data from this chromosome")

    parser.add_argument("chrom_file", action="store", 
                        metavar="CHROM_FILE", 
                        help="path to the file containing chromosomes names and lengths")
    
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    ngs = NGS_utils.utils.NGS(assembly=args.assembly)
    samples = pd.io.parsers.read_table(args.samplesheet, sep=" ")
    h5_files = samples['h5RelPath']
    peaks_files = samples['Peaks'].unique()
    hub_dir = os.path.join(args.mountpoint, args.hub_name)
    if not os.path.exists(hub_dir):
        os.makedirs(hub_dir)
    assembly_dir = os.path.join(hub_dir, args.assembly)
    if not os.path.exists(assembly_dir):
        os.makedirs(assembly_dir)
    tissues = samples['Tissue'].unique()
    sampleids = samples['SampleID']
 
    #convert hdf5 files into bigWig
    bigwig_tracks = []
    for h5_track in h5_files:
        bigwig_track = os.path.join(assembly_dir, os.path.basename(h5_track) + '.bw') 
        cmd = " ".join(["python h52bigwig.py",
                        "--assembly",
                        args.assembly,
                        h5_track,
                        args.chrom_file,
                        bigwig_track])
        #print cmd
        os.system(cmd)  
        bigwig_tracks.append(bigwig_track)
 
    #convert bed files into bigBed
    bigbed_tracks = []
    for peaks_track in peaks_files:
        bigbed_track = os.path.join(assembly_dir, os.path.basename(peaks_track) + '.bb')
        cmd = " ".join(["bedToBigBed -type=bed6+4",
                        peaks_track,
                        "/mnt/lustre/home/epantaleo/src/stat45800/data/chromosome.lengths.hg19.txt", #tmpfile_sizes,
                        bigbed_track])
        os.system(cmd)
        #if retcode != 0:
        #    warnings.warn("bedToBigBed terminated with signal: %i" % -retcode)
        bigbed_tracks.append(bigbed_track)                              

    trackdb_file = os.path.join(args.assembly, 'trackDbFile.txt')
    f = open(os.path.join(hub_dir, 'genomes.txt'), 'w')
    f.write(" ".join(['genome', args.assembly]))
    f.write("\n")
    f.write("".join(['trackDb ', args.assembly, "/trackDbFile.txt"]))
    f.write("\n")
    f.close()
    f = open(os.path.join(hub_dir, 'hub.txt'), 'w')
    f.write(" ".join(['hub', args.hub_name]))
    f.write("\n")
    f.write(" ".join(['shortLabel', args.hub_name]))
    f.write("\n")
    f.write(" ".join(['longLabel', args.hub_name]))
    f.write("\n")
    f.write("genomesFile genomes.txt\n")
    f.write("email esterpantaleo@gmail.com\n")
    f.close()
    f = open(os.path.join(hub_dir, trackdb_file), 'w')
    f.write("track reads\nshortLabel reads\nlongLabel reads\nsuperTrack on none\npriority 1\nautoScale on\ndragAndDrop subtracks\n\n")
    counter=0
    for bigwig_track in bigwig_tracks:
        track_name = os.path.basename(bigwig_track)
        f.write(" ".join(["track", sampleids[counter]]))
        f.write("\n")
        f.write("parent reads\n")
        f.write("type bigWig\n")
        f.write("graphType points\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join(["bigDataUrl", track_name]))
        f.write("\n")
        f.write(" ".join(["shortLabel", sampleids[counter]]))
        f.write("\n")
        f.write(" ".join(["longLabel", sampleids[counter]]))
        f.write("\n\n")
        counter+=1
    f.write("track peaks\nshortLabel peaks\nlongLabel peaks\nsuperTrack on none\npriority 2\nautoScale on\ndragAndDrop subtracks\n\n")
    counter=0
    for bigbed_track in bigbed_tracks:
        track_name = os.path.basename(bigbed_track)
        f.write(" ".join(["track", tissues[counter]]))
        f.write("\n")
        f.write("parent peaks\n")
        f.write("type bigBed\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join(["bigDataUrl", track_name]))
        f.write("\n")
        f.write(" ".join(["shortLabel", tissues[counter]]))
        f.write("\n")
        f.write(" ".join(["longLabel", tissues[counter]]))
        f.write("\n\n")
        counter+=1

    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(args.http_address, args.hub_name, 'hub.txt')
    print "center the genome browser on the region of interest"
    print "if the track is hidden click on show and then refresh"
main()
