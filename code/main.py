from SoapySDR import Device, SOAPY_SDR_TX, SOAPY_SDR_CF32
from time import sleep
import argparse
import numpy as np
import json
import sys


def load_data_from_file(filename):
    # Assuming the file contains binary complex float32 samples
    data = np.fromfile(filename, dtype=np.complex64)
    return data


def generate_white_noise(sample_rate, duration_sec):
    num_samples = int(sample_rate * duration_sec)
    return np.random.normal(0, 0.1, num_samples) + 1j * np.random.normal(
        0, 0.1, num_samples
    )


def load_config(filepath):
    KEY_FREQUENCY = "frequency"
    KEY_SAMPLE_RATE = "sample_rate"
    KEY_DATA = "data"
    config = []

    with open(filepath) as f:
        items = json.load(f)

    for item in items:
        try:
            frequency = item[KEY_FREQUENCY]
            sample_rate = item[KEY_SAMPLE_RATE]
            data = (
                load_data_from_file(item[KEY_DATA])
                if KEY_DATA in item
                else generate_white_noise(sample_rate, .1)
            )
            config.append((frequency, sample_rate, data))
        except Exception as e:
            print(f"Invlid config item: {item}: {e}")
            sys.exit(1)
    return config


def run_jammer(config):
    # sdr = Device(dict(driver="plutosdr"))
    sdr = Device(dict(driver="hackrf"))
    txStream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32)
    sdr.activateStream(txStream)

    try:
        while True:
            for frequency, sample_rate, data in config:
                sdr.setSampleRate(SOAPY_SDR_TX, 0, sample_rate)
                sdr.setFrequency(SOAPY_SDR_TX, 0, frequency)
                sr = sdr.writeStream(txStream, [data], len(data))
            # sleep(SLEEP_TIMEOUT_SEC)
    except KeyboardInterrupt:
        # User has pressed Ctrl+C, exit the loop
        pass

    sdr.deactivateStream(txStream)
    sdr.closeStream(txStream)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="jammer")
    parser.add_argument(
        "-f",
        "--file",
        dest="filepath",
        required=True,
        help="jammer JSON configuration file",
    )
    args = parser.parse_args()
    config = load_config(args.filepath)
    run_jammer(config)