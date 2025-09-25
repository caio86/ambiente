#!/usr/bin/env bash

# Test scenario duration in seconds, default = 60s
DURATION=60
SERVER_IP="192.168.56.102"
INTERFACE="eth1"
CAP_FILE="web_$(date +%s).pcap"

PCAP_DIR="/vagrant/pcap"
CAP_FILE_PATH="${PCAP_DIR}/${CAP_FILE}"

run_client() {
  local counter=0
  while true; do
    echo "Iteration $counter"
    curl -s $SERVER_IP >/dev/null 2>&1
    ((counter++))
    sleep 0.5
  done
}

mkdir -p $PCAP_DIR >/dev/null 2>&1
tcpdump -i $INTERFACE -w ${CAP_FILE_PATH} >/dev/null 2>&1 &
TCPDUMP_PID=$!

run_client &
CLIENT_PID=$!

clean_up() {
  if [[ ! -z "$CLIENT_PID" ]] && kill -0 $CLIENT_PID 2>/dev/null; then
    echo "Stopping client (PID: $CLIENT_PID)"
    kill $CLIENT_PID
    wait $CLIENT_PID 2>/dev/null
  fi

  if [[ ! -z "$TCPDUMP_PID" ]] && kill -0 $TCPDUMP_PID 2>/dev/null; then
    echo "Stopping tcpdump (PID: $TCPDUMP_PID)"
    kill $TCPDUMP_PID
    wait $TCPDUMP_PID 2>/dev/null
    echo "Packets saved to: ${CAP_FILE_PATH}"
  fi
}
trap clean_up EXIT INT TERM

sleep $DURATION
