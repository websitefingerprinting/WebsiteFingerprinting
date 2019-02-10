def str_to_sinste(fname):
    #given a file name fold/X-Y or fold/Z, returns (site, inst)
    #inst = -1 indicates open world
    #does not behave well with poorly formatted data

    fname = fname[fname.index("/")+1:]
    site = -1
    inst = -1
    if "-" in fname:
        fname = fname.split("-")
        site = int(fname[0])
        inst = int(fname[1])
    else:
        try:
            site = int(fname)
        except:
            site = -1
            inst = -1

    return (site, inst)

def load_cell(fname, time=0, ext=".cell"):
    #time = 0 means don't load packet times (saves time and memory)
    data = []
    starttime = -1
    try:
        f = open(fname, "r")
        lines = f.readlines()
        f.close()

        if ext == ".htor":
            #htor actually loads into a cell format
            for li in lines:
                psize = 0
                if "INCOMING" in li:
                    psize = -1
                if "OUTGOING" in li:
                    psize = 1
                if psize != 0:
                    if time == 0:
                        data.append(psize)
                    if time == 1:
                        time = float(li.split(" ")[0])
                        if (starttime == -1):
                            starttime = time
                        data.append([time - starttime, psize])

        if ext == ".cell":
            for li in lines:
                li = li.split("\t")
                p = int(li[1])
                if time == 0:
                    data.append(p)
                if time == 1:
                    t = float(li[0])
                    if (starttime == -1):
                        starttime = t
                    data.append([t-starttime, p])
        if ext == ".burst":
            #data is like: 1,1,1,-1,-1\n1,1,1,1,-1,-1,-1
            for li in lines:
                burst = [0, 0]
                li = li.split(",")
                data.append([li.count("1"), li.count("-1")])
                for l in li:
                    if l == "1":
                        burst[0] += 1
                    if l == "-1":
                        burst[1] += 1
                data.append(burst)

        if ext == ".pairs":
            #data is like: [[3, 12], [1, 24]]
            #not truly implemented
            data = list(lines[0])            
    except:
        print "Could not load", fname
    return data

def load_cellt(fname, ext=".cell"):
    return load_cell(fname, time=1, ext=ext)

def load_set(d, site=-1, inst=-1, time=0, ext=".cell"):
    #loads all data OR all of a specific site OR a specific inst of a site
    CLOSED_SITENUM = d["CLOSED_SITENUM"]
    CLOSED_INSTNUM = d["CLOSED_INSTNUM"]
    OPEN_INSTNUM = d["OPEN_INSTNUM"]
    DATA_LOC = d["DATA_LOC"]

    data = []
    #there's probably a better way to simplify this

    if (site == -1 and inst == -1):
        #load closed world
        for i in range(0, CLOSED_SITENUM):
            data.append([])
            for j in range(0, CLOSED_INSTNUM):
                fname = str(i) + "-" + str(j) + ext
                data[-1].append(load_cell(DATA_LOC + fname, time, ext))

        #load open world
        data.append([])
        for i in range(0, OPEN_INSTNUM):
            fname = str(i) + ext
            data[-1].append(load_cell(DATA_LOC + fname, time, ext))

    if (site != -1 and inst == -1):
        #load all insts of one site
        if (site == CLOSED_SITENUM):
            for i in range(0, OPEN_INSTNUM):
                fname = str(i) + ext
                data.append(load_cell(DATA_LOC + fname, time, ext))
        else:
            for j in range(0, CLOSED_INSTNUM):
                fname = str(site) + "-" + str(j) + ext
                data.append(load_cell(DATA_LOC + fname, time, ext))

    if (site != -1 and inst != -1):
        #load one particular inst
        if (site == CLOSED_SITENUM):
            fname = str(inst) + ext
            data = load_cell(DATA_LOC + fname, time, ext)
        else:
            fname = str(site) + "-" + str(inst) + ext
            data = load_cell(DATA_LOC + fname, time, ext)
                
    return data

def load_all(CLOSED_SITENUM, CLOSED_INSTNUM, OPEN_INSTNUM, INPUT_LOC, time=0):
    #deprecated; do not call
    print "deprecated: call load_set"
    sys.exit(0)

def kfold(data, fi, foldtotal):
    #input: full data set, current fi, total number of folds
    #output: traindata, testdata
    traindata = []
    testdata = []
    for cdata in data: #each class
        traindata.append([])
        testdata.append([])
        
        test_indices = []

        test_num_start = (len(cdata) * fi) / foldtotal
        test_num_end = test_num_start + max(len(cdata)/foldtotal, 1)
        for ti in range(0, len(cdata)):
            if ti < test_num_end and ti >= test_num_start:
                test_indices.append(ti)
        
        for inst in range(0, len(cdata)):
            if inst in test_indices:
                testdata[-1].append(cdata[inst])
            else:
                traindata[-1].append(cdata[inst])

    return traindata, testdata

def load_list(flist, time=0):
    #loads the list of files in flist
    data = []
    opendata = []
    datanames = []
    opendatanames = []
    f = open(flist, "r")
    fnames = f.readlines()
    f.close()
    for fname in fnames:
        fname = fname[:-1]
        relfname = fname.split("/")[-1]
        relfname = relfname.split(".")[0]
        if "-" in relfname:
            s = int(relfname.split("-")[0])
            i = int(relfname.split("-")[1])
            while s >= len(data):
                data.append([])
                datanames.append([])
            data[s].append(load_cell(fname))
            datanames[s].append(fname)
        else:
            i = int(relfname)
            opendata.append(load_cell(fname, time))
            opendatanames.append(fname)
    data.append(opendata)
    datanames.append(opendatanames)
    return data, datanames

def load_listn(flist):
    #loads the list of files in flist
    #only loads names. returns data as empty set.
    datanames = []
    opendatanames = []
    f = open(flist, "r")
    fnames = f.readlines()
    f.close()
    for fname in fnames:
        fname = fname[:-1]
        relfname = fname.split("/")[-1]
        relfname = relfname.split(".")[0]
        if "-" in relfname:
            s = int(relfname.split("-")[0])
            i = int(relfname.split("-")[1])
            while s >= len(datanames):
                datanames.append([])
            datanames[s].append(fname)
        else:
            i = int(relfname)
            opendatanames.append(fname)
    datanames.append(opendatanames)
    return [], datanames
    

def load_options(fname):
    d_options = {}
    f = open(fname, "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        ignore = 0
        if (len(line) > 0):
            if line[0] == "#":
                ignore = 1
        if (ignore == 0 and "\t" in line):
            line = line[:-1]
            li = line.split("\t")
            val = li[1]
            try:
                val = int(li[1])
            except:
                try:
                    val = float(li[1])
                except:
                    pass
            d_options[li[0]] = val
    return d_options

def write_options(fname, d_options):
    other = d_options.keys()
    order = ["CLOSED_SITENUM", "CLOSED_INSTNUM", "OPEN_INSTNUM", "OPEN",
             "INPUT_LOC", "OUTPUT_LOC", "DATA_LOC", "ATTACK_LOC", "DATA_TYPE",
             "LEV_METHOD", "LEV_LOC",
             "FOLD_MODE", "FOLD_NUM", "FOLD_TOTAL"]
    f = open(fname, "w")
    for opt in order:
        if opt in d_options.keys():
            f.write(str(opt) + "\t" + str(d_options[opt]) + "\n")
            other.remove(opt)
    for opt in other:
        f.write(str(opt) + "\t" + str(d_options[opt]) + "\n")
    f.close()

import pprint

def options_to_string(d_options):
    return pprint.saferepr(d_options)
