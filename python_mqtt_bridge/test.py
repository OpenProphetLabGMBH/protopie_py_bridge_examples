import argparse
parser = argparse.ArgumentParser()

parser.add_argument("echo", help="echo the string you use here", type=str)

args = parser.parse_args()

arg_one = args.echo
print(arg_one)

if arg_one == "echo":
    print("echo matched ...")
    print("Running indefinitely")
    while True:
        s = 1
