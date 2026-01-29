
"""
What we want visualizer.py to do:

- Accept arguments for source filename (e.g. validation_results_1.csv)
  and verbose option from command-line interface

- Read source filename and convert contents into
  2 lists, chip_indices and chip_hold

- Plot a graph of chip_indices (x-axis) and chip_hold (y-axis) using
  one of the popular third-party libraries, matplotlib
  
- Log verbose debug messages if user enabled it (-v/--verbose)

"""

# use command line arguments for source filename with -v/--verbose option
import argparse
# add logging. later, if verbose mode,  then adjust level to "debug"
import logging
# exit if unable to properly locate or read file
import sys
# visualize the data the program has read from the file
import matplotlib.pyplot as plt

# configure the log format to our liking
logging.basicConfig(
    level = logging.INFO, # default
    format = '%(asctime)s - %(levelname)s - %(message)s',
    datefmt = '%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# set up parser so that we can parse filename and --verbose option
parser = argparse.ArgumentParser(
    prog = "Visualizer",       # program name
    description = "Visualize chip validation results",
    epilog = "Example usage: visualize.py --source results.csv"
)

# add argument for source filename (positional argument)
parser.add_argument(
    "source",
    help="Filename for source of data to be visualized.")

# add argument (keyword argument)
parser.add_argument(
    "-v", "--verbose",
    action="store_true",
    help="Enable verbose debug logging.")

args = parser.parse_args()
# print(args.source)

# if user chose --verbose option, adjust logging level accordingly
# if user didn't choose the --verbose option, the logging level would've stayed at INFO
# which meant the DEBUG level messages would not be logged 
if args.verbose:
    logger.setLevel(logging.DEBUG)
    logger.debug("Verbose logging enabled")

# main program, which will only be executed if visualizer.py is run directly
# (as opposed to being imported as a module)
def main():

    # anticipate failure to locate the file
    try:
        logger.debug(f"Attempting to open file {args.source}")

        # read and iterate through file
        chip_indices = []
        chip_hold = []
        with open(args.source, 'r') as file:
            
            logger.debug(f"Reading file {args.source}")

            # ignore first line
            for line in file.readlines()[1:]:
                chip_data = line.split(",")

                chip_indices.append(chip_data[0])
                chip_hold.append(int(chip_data[1]))

            logger.debug(f"Finished reading file {args.source}, found {len(chip_indices)} items.")
        
        #print(chip_indices)
        #print(chip_hold)

    except:
        logger.error(f"Unable to locate or read {args.source}, exiting.")
        sys.exit(1)

    # visualize using matplotlib
    plt.plot(chip_indices, chip_hold)
    plt.show()


# make it so that if visualizer.py is imported as a module by another Python program
# (as opposed to directly running it), the main() program doesn't run automatically
if __name__ == "__main__":
    main()