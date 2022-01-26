#! /usr/bin/env python
"""
 graph.py       A small tool that allows you to generate a visual representation of your devices and links using discovery
                protocols from the links table of Observium

 Author:        Mathieu Poussin <mathieu.poussin@oxalide.com>
 Date:          01/2015

 Usage:         This program accepts many arguments :
                --debug : Debug mode, write one image per step
                HOSTNAME : The first device hostname


 Ubuntu Linux:  apt-get install python-mysqldb
 RHEL/CentOS:   yum install MySQL-python (Requires the EPEL repo!)
 FreeBSD:       cd /usr/ports/*/py-MySQLdb && make install clean

 Tested on:     Python 2.7.5 / Ubuntu 13.10

"""
import subprocess, sys, os, json
import MySQLdb, MySQLdb.cursors, pydot, colour

"""
    Parse Arguments
    Attempt to use argparse module.  Probably want to use this moving forward
    especially as more features want to be added to this wrapper.
    and
    Take the amount of threads we want to run in parallel from the commandline
    if None are given or the argument was garbage, fall back to default of 16
"""
try:
    import argparse
    parser = argparse.ArgumentParser(description='Network graph generator')
    parser.add_argument('hostname', nargs='?', type=str, help='The first device hostname')
    parser.add_argument('--debug', help="Enable step by step debugging", action="store_true", default=False)
    args = parser.parse_args()
    hostname = args.hostname
    debug_mode = args.debug
except ImportError:
    print "WARNING: missing the argparse python module:"
    print "On Ubuntu: apt-get install libpython2.7-stdlib"
    print "On RHEL/CentOS: yum install python-argparse"
    print "On Debian: apt-get install python-argparse"
    sys.exit(2)


"""
    Fetch configuration details from the config_to_json.php script
"""

ob_install_dir = os.path.dirname(os.path.realpath(__file__))
config_file = ob_install_dir + '/config.php'

def get_config_data():
    config_cmd = ['/usr/bin/env', 'php', '%s/config_to_json.php' % ob_install_dir]
    try:
        proc = subprocess.Popen(config_cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    except:
        print "ERROR: Could not execute: %s" % config_cmd
        sys.exit(2)
    return proc.communicate()[0]

try:
    with open(config_file) as f: pass
except IOError as e:
    print "ERROR: Oh dear... %s does not seem readable" % config_file
    sys.exit(2)

try:
    config = json.loads(get_config_data())
except:
    print "ERROR: Could not load or parse observium configuration, are PATHs correct?"
    sys.exit(2)

db_username  = config['db_user']
db_password  = config['db_pass']
db_server    = config['db_host']
db_dbname    = config['db_name']

try:
    db = MySQLdb.connect (host=db_server, user=db_username , passwd=db_password, db=db_dbname)
    cursor = db.cursor(MySQLdb.cursors.DictCursor)
except:
    print "ERROR: Could not connect to MySQL database!"
    sys.exit(2)

def sizeof_fmt(num, suffix='bps'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


colors_scale = list(colour.Color("green").range_to(colour.Color("yellow"), 50))+list(colour.Color("yellow").range_to(colour.Color("red"), 50))

exit

query_template = """
SELECT
  d.device_id AS local_device_id,
  rd.device_id AS remote_device_id,
  UPPER(d.hostname) AS local_hostname,
  p.port_id AS local_port_id,
  p.ifName AS local_port,
  p.ifSpeed/1000000 as local_port_speed,
  l.remote_port_id AS remote_port_id,
  rp.ifName AS remote_port,
  UPPER(l.remote_hostname) AS remote_hostname,
  d.hardware AS hardware,
  rd.hardware AS remote_hardware,
  s.ifInErrors_rate AS local_in_errors_rate,
  s.ifOutErrors_rate AS local_out_errors_rate,
  s.ifInOctets_rate*8 AS local_in_octets_rate,
  s.ifOutOctets_rate*8 AS local_out_octets_rate,
  s.ifInOctets_perc AS local_in_octets_perc,
  s.ifOutOctets_perc AS local_out_octets_perc
FROM
  `devices` AS d,
  `devices` as rd,
  `ports` AS p,
  `ports` as rp,
  `neighbours` AS l,
  `ports` AS s
WHERE
  p.port_id = l.port_id AND
  p.device_id = d.device_id AND
  rp.port_id = l.remote_port_id AND
  rp.device_id = rd.device_id AND
  p.port_id = s.port_id AND
  UPPER(d.hostname) = UPPER('%s');
"""

scanned_ports = []
scanned_devices = []
graph = pydot.Dot(graph_type='digraph', rankdir='LR', fontname="helvetica", bgcolor="black")
debug_id = 0
this_device = hostname

def discover_links(graph, this_device):
    global debug_id
    cursor.execute(query_template % this_device)
    data = cursor.fetchall()
    for link in data:
        if((not [link["local_hostname"],link["local_port"]] in scanned_ports) and (not [link["remote_hostname"],link["remote_port"]] in scanned_ports)):
            sys.stdout.write(">")
            sys.stdout.flush()
            from_label = """<<B>{device}</B><BR/><U>{hardware}</U>>""".format(device=link["local_hostname"], hardware=link["hardware"])
            to_label = """<<B>{device}</B><BR/><U>{hardware}</U>>""".format(device=link["remote_hostname"], hardware=link["remote_hardware"])
            from_node = pydot.Node(link["local_hostname"], label=from_label, style="filled", fillcolor="#323232", color="#646464", fontcolor="white", fontname="helvetica", href="https://obs.example.net/device/device={device_id}/".format(device_id=link["local_device_id"]))
            graph.add_node(from_node)
            to_node = pydot.Node(link["remote_hostname"], label=to_label, style="filled", fillcolor="#323232", color="#646464", fontcolor="white", fontname="helvetica", href="https://obs.example.net/device/device={device_id}/".format(device_id=link["remote_device_id"]))
            graph.add_node(to_node)
            usage_perc = max(link["local_in_octets_perc"],link["local_out_octets_perc"])
            if usage_perc <= 100:
              color = "%s" % colors_scale[usage_perc]
            else:
              color = "purple"

            if link["local_port_speed"] == 10000:
              size = 8
            elif link["local_port_speed"] == 1000:
              size = 3
            else:
              size = 1

            edge = pydot.Edge(from_node, to_node, color=color, fontcolor="white", fontsize=10, fontname="helvetica", penwidth=size, label="{from_if} -> {to_if}; Rx: {rx}, Tx: {tx}".format(from_if=link["local_port"], to_if=link["remote_port"], rx=sizeof_fmt(link["local_in_octets_rate"]), tx=sizeof_fmt(link["local_out_octets_rate"])), href="https://obs.example.net/device/device={device_id}/tab=port/port={port_id}/".format(device_id=link["local_device_id"], port_id=link["local_port_id"]))
            graph.add_edge(edge)
            scanned_ports.append([link["local_hostname"],link["local_port"]])
            scanned_ports.append([link["remote_hostname"],link["remote_port"]])
            scanned_devices.append(link["local_hostname"])
            global debug_mode
            if debug_mode:
                debug_id = debug_id + 1
                print("Wrote debug_%05d.png" % (debug_id))
                graph.write_png("debug_%05d.png" % (debug_id))
            new_graph = discover_links(graph, link["remote_hostname"])
            if new_graph is not None:
                graph = new_graph
            else:
                print("GRAPH IS NULL %s" % this_device)
    sys.stdout.write("<")
    sys.stdout.flush()
    return graph

sys.stdout.write("\nGenerating graph : ")
sys.stdout.flush()
graph = discover_links(graph, this_device)
sys.stdout.write("\nWriting PNG : ")
sys.stdout.flush()
graph.write_raw('%s_map.dot' % (this_device))
graph.write_png('%s_map.png' % (this_device))
sys.stdout.write("Ok ! \n")
db.close()
