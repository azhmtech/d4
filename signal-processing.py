# signal-processing.py
# day 4 - signal processing assignment
# this script reads fir coefficients from config files,
# reads an input signal vector, applies fir filtering,
# logs execution steps, and visualizes the output

import argparse
import logging
import sys
import matplotlib.pyplot as plt


# configure logging format and default level
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# set up command line argument parsing
parser = argparse.ArgumentParser(
    prog="signal-processing",
    description="validate fir filter signal processing for impl0"
)

parser.add_argument(
    "--vector",
    required=True,
    help="input signal vector file (e.g. square.vec or sqr.vec)"
)

parser.add_argument(
    "--configs",
    nargs=4,
    required=True,
    help="four fir coefficient config files (e.g. p0.cfg p4.cfg p7.cfg p9.cfg)"
)

parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="enable verbose debug logging"
)

args = parser.parse_args()


# enable debug logging if verbose option is selected
if args.verbose:
    logger.setLevel(logging.DEBUG)
    logger.debug("verbose logging enabled")


def read_vector_file(filename):
    # read input signal vector from file
    signal = []
    try:
        logger.debug(f"opening vector file {filename}")
        with open(filename, "r") as file:
            for line in file:
                value = line.strip()
                if value:
                    # auto-detect base (decimal, hex, binary)
                    signal.append(int(value, 0))
        logger.info(f"loaded {len(signal)} samples from {filename}")
        return signal
    except Exception as e:
        logger.error(f"failed to read vector file {filename}: {e}")
        sys.exit(1)


def read_config_file(filename):
    # read fir coefficients from config file
    coeffs = []
    try:
        logger.debug(f"opening config file {filename}")
        with open(filename, "r") as file:
            lines = file.readlines()

            # skip header line
            for line in lines[1:]:
                parts = line.strip().split(",")

                # unpack columns
                coef_idx = parts[0]
                enable = int(parts[1], 0)
                value = parts[2]
                # only include enabled coefficients
                if enable == 1:
                    coeffs.append(int(value, 0))

        logger.info(f"loaded {len(coeffs)} enabled coefficients from {filename}")
        return coeffs

    except Exception as e:
        logger.error(f"failed to read config file {filename}: {e}")
        sys.exit(1)



def apply_fir_filter(input_signal, coefficients):
    # apply a simple fir filter implementation
    output_signal = []
    logger.debug("starting fir filtering")

    for i in range(len(input_signal)):
        acc = 0
        for j in range(len(coefficients)):
            if i - j >= 0:
                acc += input_signal[i - j] * coefficients[j]
        output_signal.append(acc)

    logger.debug("fir filtering completed")
    return output_signal


def main():
    # main program execution flow

    # read input vector
    input_signal = read_vector_file(args.vector)

    # set up plot
    plt.figure()

    # process each config file
    for cfg_file in args.configs:
        logger.info(f"processing config {cfg_file}")

        # read coefficients
        coeffs = read_config_file(cfg_file)

        # apply fir filter
        output_signal = apply_fir_filter(input_signal, coeffs)

        # plot output signal
        plt.plot(output_signal, label=cfg_file)

    # finalize plot
    plt.title("fir filter output for impl0")
    plt.xlabel("sample index")
    plt.ylabel("output value")
    plt.legend()
    plt.grid(True)

    logger.info("displaying plot")
    plt.show()


# ensure main only runs when script is executed directly
if __name__ == "__main__":
    main()
