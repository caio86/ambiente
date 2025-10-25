#!/usr/bin/env python3

import argparse
import csv
import random
import socket
import struct
import sys
from datetime import datetime
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


def handle_pkt(pkt, csv_writer: csv.DictWriter):
    ip_layer = pkt[IP]
    payload = bytes(ip_layer.payload)
    int_fields = struct.unpack(">IHHHQQQIII", payload[:46])

    int_data = {
        "timestamp": datetime.now().isoformat(),
        "src_ip": ip_layer.src,
        "dst_ip": ip_layer.dst,
        "switchID_t": int_fields[0],
        "ingress_port": int_fields[1],
        "egress_port": int_fields[2],
        "egress_spec": int_fields[3],
        "ingress_global_timestamp": int_fields[4],
        "egress_global_timestamp": int_fields[5],
        "enq_timestamp": int_fields[6],
        "enq_qdepth": int_fields[7],
        "deq_timedelta": int_fields[8],
        "deq_qdepth": int_fields[9],
    }

    csv_writer.writerow(int_data)
    # print(int_data)
    # pkt.show2()


FIELDNAMES = [
    "timestamp",
    "src_ip",
    "dst_ip",
    "switchID_t",
    "ingress_port",
    "egress_port",
    "egress_spec",
    "ingress_global_timestamp",
    "egress_global_timestamp",
    "enq_timestamp",
    "enq_qdepth",
    "deq_timedelta",
    "deq_qdepth",
]


def main():
    output_file = "/vagrant/metrics/telemetry.csv"
    iface = "eth1"
    bind_layers(IP, nodeCount, proto=253)
    with open(output_file, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        try:
            sniff(
                filter="ip proto 253", iface=iface, prn=lambda x: handle_pkt(x, writer)
            )
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
