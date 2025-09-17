from .progress_bar import progress_bar
from .enums import Styles
from sys import stdout
import time

def main():
    # Example
    for prgrs_bar, el in progress_bar(range(100), title="Do something...", show_percentage=True, size=15, style=Styles.CLASSIC):
        stdout.write("\033[2J\033[H\r" + prgrs_bar)
        stdout.write("\n" + str(el))

        stdout.flush()
        time.sleep(0.02)
    stdout.write("\n")

if __name__ == "__main__":
    main()