#!/usr/bin/env python3
"""Check whether the workstation has the tools needed for this project."""
import argparse
import shutil
import subprocess

TOOLS = {
    "python": ["python", "--version"],
    "git": ["git", "--version"],
    "aws": ["aws", "--version"],
    "sam": ["sam", "--version"],
    "docker": ["docker", "--version"],
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--aws", action="store_true", help="Also verify your AWS caller identity")
    args = parser.parse_args()
    for name, command in TOOLS.items():
        if not shutil.which(command[0]):
            print(f"[missing] {name}")
            continue
        result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=15)
        message = (result.stdout or result.stderr).strip().splitlines()
        print(f"[{'ok' if result.returncode == 0 else 'check'}] {name}: {message[0] if message else 'no version output'}")
    if args.aws:
        if not shutil.which("aws"):
            parser.error("AWS CLI is not installed")
        result = subprocess.run(["aws", "sts", "get-caller-identity"], check=False)
        return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
