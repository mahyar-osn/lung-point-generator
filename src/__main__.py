import os
import argparse

import numpy as np

from pts_generator import generate as pgen
from ex_generator import generate as egen


class ProgramArguments(object):
    def __init__(self):
        self.input_file = None
        self.output_dir = None


def run(file_path: str, file_format: str, output_dir: str, file_name: str) -> None:
    if file_format == "exdata":
        coordinates = pgen(file_path)
        output_file = os.path.join(output_dir, f"{file_name}.pts")
        with open(output_file, 'w') as points_file:
            for coordinate in coordinates:
                points_file.write(f"{coordinate[0]:.2f} {coordinate[1]:.2f} {coordinate[2]:.2f}\n")
        return None
    else:
        content = np.load(file_path)
        output_file = os.path.join(output_dir, f"{file_name}.exdata")
        egen(content, output_file)


def main():
    args = parse_args()
    if os.path.exists(args.input_file):
        file_name = os.path.basename(args.input_file).split(".")[0]
        if args.output_dir is None:
            output_dir = os.path.dirname(args.input_file)
        else:
            output_dir = args.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if args.input_file.endswith("exdata"):
            run(args.input_file, "exdata", output_dir, file_name)
        elif args.input_file.endswith("npy"):
            run(args.input_file, "npy", output_dir, file_name)
        else:
            raise KeyError(f"Invalid file format extension. Either '.npy' or '.exdata' file is allowed.")


def parse_args() -> ProgramArguments:
    parser = argparse.ArgumentParser(description="This application reads 3D digitised lung data in ZINC .exdata format,"
                                                 "and outputs .pts file.")
    parser.add_argument("--input_file", help="Path to the input file.")
    parser.add_argument("--output_dir", help="Location to save the annotated .exdata file."
                                             "[Default is the input .exdata directory.")

    program_arguments = ProgramArguments()
    parser.parse_args(namespace=program_arguments)

    return program_arguments


if __name__ == '__main__':
    main()
