import subprocess
import sys
import argparse
from typing import List, Optional

def pip_install(proxy: Optional[str], args: List[str]) -> None:
    if proxy is None:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", *args],
            check=True,
        )
    else:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", f"--proxy={proxy}", *args],
            check=True,
        )


pkgs = '''
    pandas
    numpy
    loguru 
    '''

def main():
    parser = argparse.ArgumentParser(description="install requirements")
    parser.add_argument("--cuda", default=None, type=str)
    parser.add_argument(
        "--proxy",
        default=None,
        type=str,
        help="specify http proxy, [http://127.0.0.1:1080]",
    )
    args = parser.parse_args()
    
    for line in pkgs.split("\n"):
        # handle multiple space in an empty line
        line = line.strip()

        if len(line) > 0:
            # use pip's internal APIs in this way is deprecated. This will fail in a future version of pip.
            # The most reliable approach, and the one that is fully supported, is to run pip in a subprocess.
            # ref: https://pip.pypa.io/en/latest/user_guide/#using-pip-from-your-program
            # pip.main(['install', *line.split()])

            pip_install(args.proxy, line.split())

    print("\nsuccessfully installed requirements!")
