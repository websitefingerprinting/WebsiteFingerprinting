from os.path import join

import numpy as np
from math import sqrt, pi, ceil
from scipy.stats import norm
from bisect import insort_left

import histograms as histo
from pparser import Flow, Packet

import constants as ct

# shortcuts
from constants import IN, OUT
from constants import WAIT, BURST, GAP, INF

import logging

# logging
logger = logging.getLogger('wtfpad')

# shortcut
ht = histo.Histogram


class AdaptiveSimulator(object):
    """Simulates adaptive padding's original design on real web data."""

    def __init__(self, config):
        # parse arguments
        self.interpolate = bool(config.get('interpolate', True))
        self.remove_tokens = config.get('remove_tokens', True)
        self.stop_on_real = config.get('stop_on_real', True)
        self.percentile = float(config.get('percentile', 0))

        # the distribution of packet lengths is fixed in Tor
        self.length_distrib = histo.uniform(ct.MTU)

        # initialize dictionary of distributions
        distributions = {k: v for k, v in config.items() if 'dist' in k}
        self.hist = self.initialize_distributions(distributions)

    def simulate(self, trace):
        """Adaptive padding simulation of a trace."""
        flows = {IN: Flow(IN), OUT: Flow(OUT)}


        for i, packet in enumerate(trace):
            logger.debug("Packet %s: %s" % (i, packet))

            # flow in the direction of the packet and the opposite
            flow = flows[packet.direction]
            oppflow = flows[-packet.direction]  # opposite direction

            # update state
            self.update_state(packet, flow)

            # run adaptive padding in the flow direction
            self.add_padding(i, trace, flow, 'snd')

            # run adaptive padding in the opposite direction,
            # as if the packet was received at the other side
            self.add_padding(i, trace, oppflow, 'rcv')

            # pad packet length
            packet.length = self.length_distrib.random_sample()

        # sort race by timestamp
        trace.sort(key=lambda x: x.timestamp)

        return trace

    def add_padding(self, i, trace, flow, on):
        """Generate a dummy packet."""
        packet = trace[i]

        if flow.state == WAIT:
            return

        timeout = INF
        histogram = self.hist[flow.state][flow.direction][on]
        if histogram is not None:
            timeout = histogram.random_sample()

        try:
            iat = self.get_iat(i, trace, flow.direction, on)
        except IndexError:
            self.pad_end_flow(flow)
            return

        # if iat <= 0 we do not have space for a dummy
        if not iat <= 0:
            if timeout < iat:
                logger.debug("timeout = %s  < %s = iat", timeout, iat)

                # timeout has expired
                flow.expired, flow.timeout = True, timeout

                # the timeout has expired, we send a dummy packet
                dummy = self.generate_dummy(packet, flow, timeout)

                # correct the timeout
                iat = timeout

                # add dummy to trace
                insort_left(trace, dummy)

            # remove the token from histogram
            if histogram is not None:
                histogram.remove_token(iat)

    def update_state(self, packet, flow):
        """Switch state accordingly to AP machine state."""
        if flow.state == WAIT and not packet.dummy:
            flow.state = BURST

        elif flow.state == BURST and flow.expired:
            flow.state = GAP

        elif flow.state == BURST and flow.timeout == INF:
            flow.state = WAIT

        elif flow.state == GAP and flow.timeout == INF:
            flow.state = BURST

        elif flow.state == GAP and not packet.dummy:
            if self.stop_on_real:
                flow.state = WAIT

        else:
            return False

        logger.debug("Flow = %s, new state: %s", flow.direction, flow.state)
        return True

    def get_iat(self, i, trace, direction, on):
        """Find previous and following packets to substract their timestamps."""
        packet_0 = trace[i]
        packet_1 = self.get_next_packet(trace, i, direction)
        return packet_1.timestamp - packet_0.timestamp

    def get_next_packet(self, trace, i, direction):
        """Get the packet following the packet in position i with the same
        direction.
        """
        return trace[trace.get_next_by_direction(i, direction)]

    def pad_end_flow(self, flow):
        # AP is supposed to run continuously. So, it cannot be fairly evaluated
        # with other classifiers f we implement this funciton.
        # TODO
        pass

    def generate_dummy(self, packet, flow, timeout):
        """Set properties for dummy packet."""
        ts = packet.timestamp + timeout
        l = self.length_distrib.random_sample()
        return Packet(ts, flow.direction, l, dummy=True)

    def sum_noinf_toks(self, h):
        return sum([v for k, v in h.items() if k != INF])

    def load_and_fit(self, histo_fpath, percentile=0.5, fit_distr='norm'):
        with open(histo_fpath) as fi:
            tss = map(float, fi.readlines())
        log_tss = [np.log(ts) for ts in tss if ts > 0]
        mu = np.mean(log_tss)
        sigma = np.std(log_tss)
        mu_prime = norm.ppf(percentile, mu, sigma)
        if percentile == 0.5:
            sigma_prime = sigma
        elif percentile < 0.5:
            pdf_mu_prime = norm.pdf(mu_prime, mu, sigma)
            sigma_prime = 1 / (sqrt(2 * pi) * pdf_mu_prime)
        else:
            raise ValueError("Skewing distrib toward longer inter-arrival times makes fake bursts distinguishable from real.")
        return ht.dict_from_distr(fit_distr, (mu_prime, sigma_prime), bin_size=30)

    def init_distrib(self, name, config_dist, drop=0, skew=0):
        # parse distributions parameters
        logger.debug("Configuration of distribution \'%s\': %s" % (name, config_dist))
        dist, params  = config_dist.split(',', 1)

        if dist == 'histo':
            histo_fpath = params.strip()
            logger.debug("Loading and fitting histogram from: %s" % histo_fpath)
            d = self.load_and_fit(histo_fpath, percentile=self.percentile)

        else:
            inf_config, dist_params = params.split(',', 1)
            inf_config = float(inf_config.strip())
            dist_params = map(float, [x.strip() for x in dist_params.split(',')])
            d = ht.dict_from_distr(name=dist, params=dist_params, bin_size=30)
            d = self.set_infinity_bin(d, name, inf_config)

        # drop first `drop` bins
        if drop > 0:
            d = ht.drop_first_n_bins(d, drop)

        # skew histograms
        if skew > 0:
            d = ht.skew_histo(d, skew)

        return d

    def initialize_distributions(self, distributions):
        on = {'snd': None, 'rcv': None}
        dirs = {IN: dict(on), OUT: dict(on)}
        hist = {BURST: dict(dirs), GAP: dict(dirs)}
        for k, v in distributions.items():
            endpoint, on, mode, _ = k.split('_')
            s = ct.MODE2STATE[mode]
            d = ct.EP2DIRS[endpoint]
            hist[s][d][on] = histo.new(self.init_distrib(k, v), self.interpolate, self.remove_tokens, name=k)
        return hist

    def set_infinity_bin(self, distrib, name, inf_config):
        '''Setting the histograms' infinity bins.'''
        assert len(distrib.keys()) > 1
        # GAPS
        # we want the expectation of the geometric distribution of consecutive
        # samples from histogram to be the average number of packets in a burst.

        # Therefore, the probability of falling into the inf bin should be:
        # p = 1/N, (note the variance is going to be high)
        # where N is the length of the burst in packets.

        # Then, the tokens in infinity value should be:
        #  p = #tokens in inf bin / #total tokens <=>
        #  #tokens in inf bin = #tokens in other bins / (N - 1)

        if 'gap' in name:
            burst_length = int(inf_config)
            other_toks = self.sum_noinf_toks(distrib)
            distrib[INF] = ceil(other_toks / (burst_length - 1))

        # BURSTS
        # IN (server)
        # 5% of the time we sample from inf bin
        # (95% of burst will be followed by a fake burst)
        #
        # OUT (client)
        # 10% of the time we sample from inf bin
        # (90% of burst will be followed by a fake burst)
        # less padding in the direction from client to server because there is
        # also less volume.
        elif 'burst' in name:
            prob_burst = inf_config
            other_toks = self.sum_noinf_toks(distrib)
            distrib[INF] = ceil(other_toks / prob_burst)

        return distrib
