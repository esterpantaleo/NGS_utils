DEFAULT_ASSEMBLY = "hg18"

def writeTrackHubSkeleton(hub_dir, assembly, hub_name_string, email):
    """Write genomes.txt and hub.txt files"""
    assembly_dir = os.path.join(hub_dir, assembly)

    #write genomes file
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
    f.write(" ".join(['email', email]))
    f.write("\n")
    f.close()
    


def writeBedSuperTrack(track, shortLabel, longLabel, tracks, shortLabels, longLabels, color, priority=2):
    """Write a superTrack with BigBed files in the Track Hub trackdb_file"""
    f.write(" ".join(['track', track]))
    f.write("\n")
    f.write(" ".join(['shortLabel', shortLabel]))
    f.write("\n")
    f.write(" ".join(['longLabel', longLabel]))
    f.write("\n")
    f.write("superTrack on none\n")
    f.write(" ".join(['priority', priority]))
    f.write("\n")
    f.write("dragAndDrop subtracks\n\n")

    #for loop on list tracks
    for i in range(0, len(tracks)):
        f.write("".join(['track signal', shortLabels[i]]))
        f.write("\n")
        f.write("type bigBed\n")
        f.write(" ".join(['shortLabel', shortLabels[i]])) 
        f.write("\n")
        f.write(" ".join(['longLabel', longLabels[i]]))
        f.write("\n")
        f.write(" ".join(['parent', track]))
        f.write("\n")
        f.write("visibility full\n")
        f.write(" ".join(['bigDataUrl', tracks[i]]))
        f.write("\n")
        f.write(" ".join(['color', color]))
        f.write("\n") 

    
def printGoToMessage(hub_name, hub_dir, http_address, region=None):
    print "go to http://genome.ucsc.edu/cgi-bin/hgHubConnect and click on the My Hubs window"
    print "copy paste the following string in the URL field"
    print "%s/%s/%s" %(http_address, hub_name, 'hub.txt')
    if region is not None:
        print "note: center your genome browser around %s and make track visible" %region
    else:
        print "center the genome browser on the region of interest"
    print "(track has been saved in folder %s)" %hub_dir
