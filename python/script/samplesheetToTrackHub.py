#! /usr/bin/env python

import os
import argparse
import pandas as pd
import shutil

def parse_args():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--assembly", help="genome assembly that reads "
                        "were mapped to (e.g. hg18)", default="hg19")

    parser.add_argument("--mountpoint", help="path to the directory where "
                        "the track hub folder will be saved in. This directory should be "
                        "associated with an http address or an ftp address", 
                        default=os.environ['MOUNTPOINT_PATH'])

    parser.add_argument("--http_address", action="store",
                        help="http or ftp address associated with the mountpoint",
                        default=os.environ['MOUNTPOINT_HTTP_ADDRESS'])

    parser.add_argument("samplesheet", action="store",
                        metavar="SAMPLESHEET",
                        help="path to the samplesheet; the samplesheet "
                        "must contain a column with header sampleID, a column "
                        "with header h5RelPath "
                        "or a column with header bigWigPath containing "
                        "the relative path to the hdf5 files or the bigWig files, "
                        "respectively. "
                        "The samplesheet might have a column with header Peaks (in "
                        "which case it must also have a column with header Tissue)."
                        "Depending on the size of the h5 files "
                        "this code might require a lot of memory")

    parser.add_argument("hub_name", action="store",
                        metavar="HUB_NAME",
                        help="name of the track hub (it could contain a path, "
                        "in which case the path will be relative to the mountpoint). "
                        "This string can be set to any value")

    parser.add_argument("chrom_file", action="store", 
                        metavar="CHROM_FILE", 
                        help="path to the file containing chromosome names and lengths")
    
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    #to do: #sep=r"\s*" 
    samples = pd.io.parsers.read_table(args.samplesheet, sep=" ")
    hub_dir = os.path.join(args.mountpoint, args.hub_name)
    hub_name_string = args.hub_name.replace("/",".")
    if not os.path.exists(hub_dir):
        os.makedirs(hub_dir)
    assembly_dir = os.path.join(hub_dir, args.assembly)
    if not os.path.exists(assembly_dir):
        os.makedirs(assembly_dir)
    sampleids = samples['SampleID']
 
    bigwig_tracks = []
    if 'bigWigPath' in samples.columns.values:
        for bigwig_track in samples['bigWigPath']:
            track_name = os.path.basename(bigwig_track)
            shutil.copy2(bigwig_track, os.path.join(assembly_dir, track_name))
            bigwig_tracks.append(track_name)
    elif 'h5RelPath' in samples.columns.values:
        #convert hdf5 files into bigWig
        for h5_track in samples['h5RelPath']:
            track_name = os.path.basename(h5_track) + '.bw' 
            cmd = " ".join(["python h52bigwig.py",
                            "--assembly",
                            args.assembly,
                            h5_track,
                            args.chrom_file,
                            os.path.join(assembly_dir, track_name)])
            os.system(cmd)  
            bigwig_tracks.append(track_name)
    trackdb_file = os.path.join(args.assembly, 'trackDbFile.txt')
    f = open(os.path.join(hub_dir, 'genomes.txt'), 'w')
    f.write(" ".join(['genome', args.assembly]))
    f.write("\n")
    f.write("".join(['trackDb ', args.assembly, "/trackDbFile.txt"]))
    f.write("\n")
    f.close()
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
    f = open(os.path.join(hub_dir, trackdb_file), 'w')
    f.write("".join(["track reads\n"
                     "shortLabel reads\n",
                     "longLabel reads\n",
                     "superTrack on none\n",
                     "priority 1\n"]))
    #if bigwig files cover a region smaller than 2^20
    #use viewLimits
    cmd = "".join(["bigWigInfo ", os.path.join(assembly_dir,bigwig_tracks[0]), " | grep basesCovered | tr -d \",\"" ])
    bigWigLength = int(os.popen(cmd).readlines()[0].split()[1])
    if bigWigLength<2**20:
        #find ymax over all bigwig files
        bigWigM=0
        for bigwig_track in bigwig_tracks:
            cmd = "".join(["bigWigInfo -minMax ", os.path.join(assembly_dir,bigwig_track)])
            bigWigMax = int(float(os.popen(cmd).readlines()[0].split()[1]))
            bigWigM = max([bigWigM, bigWigMax])
        f.write("".join(["autoScale off\n",
                         "viewLimits 0:",str(bigWigM),"\n"]))
    else:
        f.write("autoScale on\n")
    f.write("dragAndDrop subtracks\n\n")

    counter=0
    for bigwig_track in bigwig_tracks:
        f.write(" ".join(["track", sampleids[counter], "\n"]))
        f.write("parent reads\n")
        f.write("type bigWig\n")
        f.write("graphType points\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join(["bigDataUrl", bigwig_track, "\n"]))
        f.write(" ".join(["shortLabel", sampleids[counter], "\n"]))
        f.write(" ".join(["longLabel", hub_name_string, sampleids[counter], "\n\n"]))
        counter+=1

    #if bed files are available in the samplesheet
    #convert bed files into bigBed                                                        
    if 'Peaks' in samples.columns.values:
        peaks_files = samples['Peaks'].unique()
        if not peaks_files[0]=="-":
            tissues = samples['Tissue'].unique() 
            bigbed_tracks = []
            for peaks_track in peaks_files:
                track_name = os.path.basename(peaks_track)
                if peaks_track.endswith('.bb'):
                    shutil.copy2(peaks_track, os.path.join(assembly_dir, track_name))
                    bigbed_tracks.append(track_name)
                else:
                    #convert bed file into bigBed file
                    bigbed_track = "".join([track_name, '.bb'])
                    cmd = " ".join(["bedToBigBed -type=bed6+4",
                                    peaks_track,
                                    args.chrom_file,
                                    os.path.join(hub_dir, bigbed_track)])
                    os.system(cmd)
                    bigbed_tracks.append(bigbed_track) 
            #write the track hub
            f.write("".join(["track peaks\n",
                             "shortLabel peaks\n",
                             "longLabel peaks\n",
                             "superTrack on none\n",
                             "priority 2\n",
                             "autoScale on\n",
                             "dragAndDrop subtracks\n\n"]))
            counter=0
            for bigbed_track in bigbed_tracks:
                f.write(" ".join(["track", tissues[counter], "\n"]))
                f.write("parent peaks\n")
                f.write("type bigBed\n")
                f.write("visibility full\n")
                f.write("color 0,0,0\n")
                f.write(" ".join(["bigDataUrl", bigbed_track, "\n"]))
                f.write(" ".join(["shortLabel", tissues[counter], "\n"]))
                f.write(" ".join(["longLabel", hub_name_string, tissues[counter], "\n\n"]))
                counter+=1

    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(args.http_address, args.hub_name, 'hub.txt')
    print "center the genome browser on the region of interest"
    print "if the track is hidden click on show and then refresh"
    print "(track has been saved in folder %s)" %hub_dir
main()
