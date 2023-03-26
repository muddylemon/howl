import time
from datetime import timedelta

start_time = time.monotonic()
filename = "timestamps.txt"

print("Press Enter to record a timestamp. Press Ctrl+C to stop.")

try:
    with open(filename, "w") as file:
        while True:
            input()
            elapsed_time = time.monotonic() - start_time
            formatted_time = str(timedelta(seconds=round(elapsed_time)))
            minutes, seconds = formatted_time.split(':')[-2:]
            file.write(f"[{minutes}:{seconds}]\n")
            file.flush()
            print(f"Timestamp [{minutes}:{seconds}] recorded.")
except KeyboardInterrupt:
    print("\nScript stopped. Check the 'timestamps.txt' file for your timestamps.")
