import serial
import sys

# notes:
# '\r', '\n', and '+' are control characters that must be escaped in binary data
#
# Prologix commands:
# ++addr [1-29]
# ++auto [0 | 1 | 2 | 3]
# ++clr
# ++eoi [0 | 1]
# ++eos [0 | 2 | 3 | 4]
# ++eot_enable [0 | 1]
# ++eot_char [<char>]
# ++help (unsupported)
# ++ifc
# ++llo [all]
# ++loc [all]
# ++lon (unsupported)
# ++mode [0 | 1]
# ++read [eoi | <char>]
# ++read_tmo_ms <time>
# ++rst
# ++savecfg
# ++spoll [<PAD> | all | <PAD1> <PAD2> <PAD3> ...]
# ++srq
# ++status [<byte>]
# ++trg [PAD1 ... PAD15]
# ++ver [real]
#
# Custom AR488 commands:
# ++allspoll
# ++dl
# ++default
# ++macro [1-9]
# ++ppoll
# ++setvstr [string]
# ++srqauto [0 | 1]
# ++repeat count delay cmdstring
# ++tmbus [value]
# ++verbose


class AR488(object):
    """Class to represent AR488 USB-GPIB adapter.

    The AR488 is an Arduino-based USB-GPIB adapter.
    For details see: https://github.com/Twilight-Logic/AR488
    """

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, timeout=1):
        try:
            self.ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        except:
            sys.exit("error opening serial port {}".format(port))

    def __del__(self):
        self.ser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.ser.close()

    # Raw GPIB read/write commands
    def write(self, message):
        """Write message to GPIB bus."""
        self.ser.write("{}\r".format(message).encode("ASCII"))

    def read(self):
        """Read from GPIB bus."""
        return self.ser.readline().decode("UTF-8")

    def query(self, message):
        "Write message to GPIB bus and read results."""
        self.write(message)
        return self.read()

    # Prologix commands
    def set_address(self, address):
        """Specify address of GPIB device with which to communicate.

        When the AR488 is in device mode rather than controller mode, this
        instead sets the address of the AR488.
        """

        self.write("++addr {}".format(address))

    def get_current_address(self):
        "Return the currently specified address."""
        return self.query("++addr")

if __name__ == "__main__":
    # Hello World!
    import time
    with AR488(timeout=4) as gpib:
        print("port name: {}".format(gpib.ser.name))
        print("baudrate: {}".format(gpib.ser.baudrate))
        print("timeout: {}".format(gpib.ser.timeout))

        print("reading version from AR488:")
        print(">> " + gpib.query("++ver"))

        print("current GPIB address:")
        print(">> " + gpib.get_current_address())
        print("setting address to 1 for 34401A")
        gpib.set_address(1)
        print("new GPIB address:")
        print(">> " + gpib.get_current_address())

        print("assert IFC to make AR488 the controller-in-charge")
        # this doesn't seem necessary, at least with only one controller
        gpib.write("++ifc")

        print("turn on auto 2 mode (auto-read after query)")
        gpib.write("++auto 2")
        print("verify auto mode: ")
        print(">> " + gpib.query("++auto"))

        print("get IDN message")
        print(">> " + gpib.query("*IDN?"))

        print("check SCPI version")
        print(">> " + gpib.query("SYST:VERS?"))

        print("turn off display")
        gpib.write("DISP OFF")
        time.sleep(1)
        gpib.write("DISP ON")

        print("display \"hello world.\" for 3 seconds")
        gpib.write("DISPLAY:TEXT \"hello world.\"")
        time.sleep(3)

        print("reset instrument")
        gpib.write("*rst")
        print("restore local (front panel) control")
        gpib.write("++loc")
