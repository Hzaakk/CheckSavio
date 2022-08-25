
# first, create a function, which return the number of GPU you are expecting to
# find.
# - determine hostname, eg n0144.savio3
# - read /etc/slurm/gres.conf
# NodeName=n0[012-026,223-226].savio[2] Name=gpu Type=K80 File=/dev/nvidia[0-3] Count=4
# NodeName=n0[227-229,298-302].savio[2] Name=gpu Type=GTX1080TI File=/dev/nvidia[0-3] Count=4
# - match hostname to the config file, and find in this case that
# "I am supposed to have 8 GTX1080TI gpu(s)".  print this.

import os

def parseRange(rangeStr):
    """Parse a range string and return a list of integers."""
    result = []
    for x in rangeStr.split(','):
        if '-' in x:
            start, end = x.split('-')
            result.extend(range(int(start), int(end) + 1))
        else:
            result.append(int(x))
    return result

def parseGresConf():
    """Parse /etc/slurm/gres.conf and return a dictionary of gpu counts."""
    gresConf = {}
    with open('/etc/slurm/gres.conf', 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('NodeName='):
                continue
            fields = line.split()
            nodeName = fields[0].split('=')[1]
            gresConf[nodeName] = {}
            for field in fields[1:]:
                key, value = field.split('=')
                gresConf[nodeName][key] = value
            gresConf[nodeName]['Count'] = int(gresConf[nodeName]['Count'])

            gresConf[nodeName]['Nodes'] = set()
            prefix = nodeName[:nodeName.index('[')]
            suffix = nodeName[nodeName.index(']') + 1:]
            suffixPrefix = suffix[:suffix.index('[')]
            suffixSuffix = suffix[suffix.index(']') + 1:]
            suffixRange = suffix[suffix.index('[') + 1:suffix.index(']')]   
            nodeRange = nodeName[nodeName.index('[') + 1:nodeName.index(']')]
            for i in parseRange(nodeRange):
                for j in parseRange(suffixRange):
                    gresConf[nodeName]['Nodes'].add('%s%03d%s%s%s' % (prefix, i, suffixPrefix, suffixSuffix))
    return gresConf

def findExpectedGpu():
    # this function will parse /etc/slurm/gres.conf 
    # use the current hostname (machineName could be passed as fn argument)
    # return how many gpu this machine should have
    # node that have no gpu should return 0
    machineName = os.uname()[1]
    gresConf = parseGresConf()
    for nodeName in gresConf:
        if machineName in gresConf[nodeName]['Nodes']:
            return gresConf[nodeName]['Count']
    return 0

if __name__ == '__main__':
    print(findExpectedGpu())