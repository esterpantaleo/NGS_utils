import shutil
import os
import argparse
import pandas as pd


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

    parser.add_argument("--hub_name", action="store",
                        metavar="HUB_NAME",
                        help="name of the track hub (it could contain a path, "
                        "in which case the path will be relative to the mountpoint). "
                        "this string can be set to any value", default="simulation"
)
    parser.add_argument("samplesheet", action="store",
                        metavar="SAMPLESHEET",
                        help="path to the samplesheet; the samplesheet "
                        "must contain a column with header bigWigPath "
                        "and a column with header Peaks")

    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    samples = pd.io.parsers.read_table(args.samplesheet, sep=" ")
    bigwig_files = samples['bigWigPath']
    hub_dir = os.path.join(args.mountpoint, args.hub_name)
    hub_name_string = args.hub_name.replace("/",".")
    if not os.path.exists(hub_dir):
        os.makedirs(hub_dir)
    assembly_dir = os.path.join(hub_dir, args.assembly)
    if not os.path.exists(assembly_dir):
        os.makedirs(assembly_dir)
    tissues = samples['Tissue'].unique()
    sampleids = samples['SampleID']

    #clean 
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

    #find ymax over all bigwig files
    bigWigM=0
    for bigwig_track in bigwig_files:
        cmd = "".join(["bigWigInfo -minMax ", bigwig_track])
        bigWigMax = int(float(os.popen(cmd).readlines()[0].split()[1]))
        bigWigM=max([bigWigM, bigWigMax])
    f = open(os.path.join(hub_dir, trackdb_file), 'w')
    f.write("".join(["track reads\n",
                     "shortLabel reads\n",
                     "longLabel reads\n",
                     "superTrack on none\n",
                     "priority 1\n",
                     "autoScale off\n",
                     "".join(["viewLimits 0:",str(bigWigM),"\n"]),
                     "dragAndDrop subtracks\n\n"]))
    counter=0
    for bigwig_track in bigwig_files:
        track_name = os.path.basename(bigwig_track)
        out_bigwig_track = os.path.join(assembly_dir, track_name)
        shutil.copy2(bigwig_track, out_bigwig_track)
        f.write(" ".join(["track", sampleids[counter]]))
        f.write("\n")
        f.write("type bigWig\n")
        f.write("parent reads\n")
        f.write("graphType points\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join(["bigDataUrl", track_name]))
        f.write("\n")
        f.write(" ".join(["shortLabel", sampleids[counter]]))
        f.write("\n")
        f.write(" ".join(["longLabel", hub_name_string, sampleids[counter]]))
        f.write("\n\n")
        counter+=1
        
    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(args.http_address, args.hub_name,  'hub.txt')
    print "center the genome browser on the region of interest"
    print "if the track is hidden click on show and then refresh"
main()
