import sys

from rtman import RTman

if __name__ == "__main__":
    config_file = sys.argv[1] if len(sys.argv)>1 else "../orchestrate/topology.json"
    wireshark_script = sys.argv[2] if len(sys.argv)>2 else None
    RTman.run_from_config_file(config_file, (wireshark_script, config_file))
    # fixme: use argparse instead of sys.argv, and don't use a config file; instead, read config file and hand over via argparse
