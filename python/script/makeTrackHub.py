import os
import argparse

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

    parser.add_argument("hub_name", action="store",
                        metavar="HUB_NAME",
                        help="name of the track hub directory")

    parser.add_argument('-bb', action='append', dest='bb',
                        default=[],
                        help='Add paths of bigBed files to plot')

    parser.add_argument("-bw", action='append', dest='bw',
                        default=[],
                        help="Add paths of bigWig files to plot")
    
    args = parser.parse_args()

    return args 

def main():
    args = parse_args()

    hub_dir = os.path.join(mountpoint, hub_name)
    trackdb_file = os.path.join(args.assembly, 'trackDbFile.txt')
    f = open(os.path.join(hub_dir, 'genomes.txt'), 'w')
    f.write(" ".join('genome', args.assembly))
    f.write("\n")
    f.write("".join(['trackDb ', args.assembly, "/trackDbFile.txt"]))
    f.write("\n")
    f.close()
    f = open(os.path.join(hub_dir, 'hub.txt'), 'w')
    f.write(" ".join('hub', hub_name))
    f.write("\n")
    f.write(" ".join('shortLabel', hub_name))
    f.write("\n")
    f.write(" ".join('longLabel', hub_name))
    f.write("\n")
    f.write(" ".join(genomesFile, 'genomes.txt'))
    f.write("\nemail esterpantaleo@gmail.com\n")
    f.close()
    f = open(os.path.join(hub_dir, trackdb_file), 'w')
    f.write("track reads\nshortLabel reads\nlongLabel reads\nsuperTrack on none\npriority 1\n\n")
    
                
    for bigwig_track in bw:
        track_name = os.path.basename(bigwig_track)
        f.write(" ".join("track", track_name))
        f.write("\n")
        f.write("parent reads\n")
        f.write("type bigWig\n")
        f.write("graphType points\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join("bigDataUrl", track_name))
        f.write("\n")
        f.write(" ".join("shortLabel", track_name))
        f.write("\n")
        f.write(" ".join("longLabel", track_name))
        f.write("\n")
    f.write("track peaks\nshortLabel peaks\nlongLabel peaks\nsuperTrack on none\npriority 2\n\n")
    for bigbed_track in bb:
        track_name = os.path.basename(bigbed_track)
        f.write(" ".join("track", track_name))
        f.write("\n") 
        f.write("parent peaks\n")
        f.write("type bigBed\n")
        f.write("visibility full\n")
        f.write("color 0,0,0\n")
        f.write(" ".join("bigDataUrl", track_name))
        f.write("\n")
        f.write(" ".join("shortLabel", track_name))
        f.write("\n")
        f.write(" ".join("longLabel", track_name))
        f.write("\n") 

    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(args.http_address, args.hub_name, 'hub.txt')
    
main()
