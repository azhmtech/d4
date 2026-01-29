import os
import subprocess
import argparse
import logging
import csv
import matplotlib.pyplot as plt

print("Signal Processing with FIR Filter")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)


## yesterday code Uad

class Uad():
    def __init__(self):
        self.inst = None

    def _exe(self):
        return os.path.join(SCRIPT_DIR, f"{self.inst}.exe")

    def reset(self):
        subprocess.check_call([self._exe(), "com", "--action", "reset"])

    def enable(self):
        subprocess.check_call([self._exe(), "com", "--action", "enable"])

    def read_CSR(self):
        out = subprocess.check_output(
            [self._exe(), "cfg", "--address", "0x0"]
        )
        return int(out, 0)

    def write_CSR(self, value):
        subprocess.check_call(
            [self._exe(), "cfg", "--address", "0x0", "--data", hex(value)]
        )

    def write_COEF(self, value):
        subprocess.check_call(
            [self._exe(), "cfg", "--address", "0x4", "--data", hex(value)]
        )

    def send_input(self, value):
        out = subprocess.check_output(
            [self._exe(), "sig", "--data", hex(value)]
        )
        if out.strip() == b"":
            return None
        return int(out, 0)



def read_vector_file(filename):
    with open(os.path.join(SCRIPT_DIR, filename)) as f:
        return [int(line.strip(), 0) for line in f if line.strip()]


def read_cfg_file(filename):
    """
    data format
    coef,en,value
    0,1,0x10
    1,1,0x10
    2,0,0x00
    3,0,0x00
    """
    cfg = {}
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            idx = int(row["coef"])
            cfg[idx] = {
                "en": int(row["en"]),
                "value": int(row["value"], 16)
            }
    return cfg


def pack_coef_register(cfg):
    """
    COEF register layout:
    [C3][C2][C1][C0] each 8 bits
    """
    val = 0
    for i in range(4):
        val |= (cfg[i]["value"] & 0xFF) << (8 * i)
    return val


def run_signal_processing(inst, cfg_files, vec_file, plot_enable):
    log = logging.getLogger("Day4")

    dut = Uad()
    dut.inst = inst

    log.info("Resetting IP")
    dut.reset()
    dut.enable()

    input_vec = read_vector_file(vec_file)
    log.info("Loaded %d input samples from %s", len(input_vec), vec_file)

    for cfg_file in cfg_files:
        log.info("===================================")
        log.info("Configuring FIR: %s", cfg_file)

        cfg = read_cfg_file(cfg_file)

        csr = dut.read_CSR()
        csr |= (1 << 5)
        dut.write_CSR(csr)

        coef_val = pack_coef_register(cfg)
        dut.write_COEF(coef_val)
        log.info("COEF = %s", hex(coef_val))

        csr = dut.read_CSR()
        for i in range(4):
            csr &= ~(1 << (1 + i))            # clear
            if cfg[i]["en"]:
                csr |= (1 << (1 + i))         # set CxEN
        dut.write_CSR(csr)

        csr = dut.read_CSR()
        dut.write_CSR(csr | (1 << 18))        # TCLR
        csr = dut.read_CSR()
        dut.write_CSR(csr & ~(1 << 18))

        csr = dut.read_CSR()
        csr &= ~(1 << 5)                      # HALT = 0
        dut.write_CSR(csr)

        csr = dut.read_CSR()
        csr |= (1 << 0)                       # FEN = 1
        dut.write_CSR(csr)

        log.info("CSR before streaming = %s", hex(dut.read_CSR()))

        outputs = []
        for x in input_vec:
            y = dut.send_input(x)
            outputs.append(y if y is not None else 0)

        if plot_enable:
            plt.figure()
            plt.plot(input_vec, label="Input")
            plt.plot(outputs, label="Output")
            plt.title(f"FIR Output – {cfg_file}")
            plt.xlabel("Sample")
            plt.ylabel("Value")
            plt.grid(True)
            plt.legend()

    if plot_enable:
        plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Day 4 – FIR Signal Processing")
    parser.add_argument("--impl", default="impl0")
    parser.add_argument("--vec", default="sqr.vec")
    parser.add_argument("--cfg", nargs="+",
                        default=["p0.cfg", "p4.cfg", "p7.cfg", "p9.cfg"])
    parser.add_argument("--plot", action="store_true")
    parser.add_argument("--loglevel", default="INFO")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.loglevel.upper()),
        format="%(asctime)s | %(levelname)s | %(message)s"
    )
    run_signal_processing(
        inst=args.impl,
        cfg_files=args.cfg,
        vec_file=args.vec,
        plot_enable=args.plot
    )
