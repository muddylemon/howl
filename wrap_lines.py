import sys
import os
import re
import argparse

def wrap_lines(prefix, suffix, input_file, output_file=None):
    if output_file is None:
        words = prefix.split()[:5]
        output_file = '-'.join(words).lower() + '.txt'

    with open(input_file, 'r') as in_file, open(output_file, 'w') as out_file:
        for line in in_file.readlines():
            _, content = line.strip().split(None, 1)
            wrapped_line = f"{prefix} ( {content} ), {suffix}\n"
            out_file.write(wrapped_line)

    print(f"Output written to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wrap lines with a prefix and suffix.")
    parser.add_argument("prefix", help="The prefix to add at the beginning of each line.")
    parser.add_argument("suffix", help="The suffix to add at the end of each line.")
    parser.add_argument("input_file", help="Path to the input file.")
    parser.add_argument("--output_file", default=None, help="Path to the output file. (optional)")

    args = parser.parse_args()

    wrap_lines(args.prefix, args.suffix, args.input_file, args.output_file)
