#!/usr/bin/env python3

import argparse
import random
import socket
import struct
import sys
from time import sleep

from scapy.all import (
    IP,
    UDP,
    BitField,
    Ether,
    FieldLenField,
    IntField,
    Packet,
    PacketListField,
    ShortField,
    XByteField,
    bind_layers,
    get_if_hwaddr,
    sendp,
    sniff,
)


class InBandNetworkTelemetry(Packet):
    fields_desc = [
        BitField("switchID_t", 0, 31),
        BitField("ingress_port", 0, 9),
        BitField("egress_port", 0, 9),
        BitField("egress_spec", 0, 9),
        BitField("ingress_global_timestamp", 0, 48),
        BitField("egress_global_timestamp", 0, 48),
        BitField("enq_timestamp", 0, 32),
        BitField("enq_qdepth", 0, 19),
        BitField("deq_timedelta", 0, 32),
        BitField("deq_qdepth", 0, 19),
    ]
    """any thing after this packet is extracted is padding"""

    def extract_padding(self, s):
        return b"", s


class nodeCount(Packet):
    name = "nodeCount"
    fields_desc = [
        ShortField("count", 0),
        PacketListField(
            "INT", [], InBandNetworkTelemetry, count_from=lambda pkt: (pkt.count * 1)
        ),
    ]


def handle_pkt(pkt):
    pkt.show2()


def main():

    iface = "eth1"
    bind_layers(IP, nodeCount, proto=253)
    sniff(filter="ip proto 253", iface=iface, prn=lambda x: handle_pkt(x))


if __name__ == "__main__":
    main()
