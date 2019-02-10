import os
import sys
import numpy as np

from pparser import parse


def latency(trace):
    if len(trace) < 2:
        return 0.0
    return trace[-1].timestamp - trace[0].timestamp


def bandwidth(trace):
    total_bytes = sum([abs(p.length) for p in trace])
    return 1.0 * total_bytes / latency(trace)
    # return 1.0*total_bytes

def bandwidth_ovhd(new, old):
    bw_old = bandwidth(old)
    if bw_old == 0.0:
        return 0.0
    return 1.0 * bandwidth(new) / bw_old


def latency_ovhd(new, old):
    lat_old = latency(old)
    if lat_old == 0.0:
        return 0.0
    return 1.0 * latency(new) / lat_old


def main():
    bandwidths, latencies = [], []
    original_files, simulated_files = sys.argv[1], sys.argv[2]
    for fname in os.listdir(original_files):
        original_trace = parse(os.path.join(original_files, fname))
        simulated_trace = parse(os.path.join(simulated_files, fname))

        bandwidth = bandwidth_ovhd(simulated_trace, original_trace)
        latency = latency_ovhd(simulated_trace, original_trace)

        bandwidths.append(bandwidth)
        latencies.append(latency)

    print("Bandwidth overhead:", np.median([b for b in bandwidths if b > 0.0]))
    print("Latency overhead:", np.median([l for l in latencies if l > 0.0]))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(-1)
