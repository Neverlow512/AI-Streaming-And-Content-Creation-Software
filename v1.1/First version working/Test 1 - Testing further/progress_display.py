# progress_display.py

import time

def progress_display_process(desired_duration_seconds, progress_queue):
    import tqdm

    if desired_duration_seconds > 0:
        # Create a progress bar
        pbar = tqdm.tqdm(total=desired_duration_seconds, unit='s', desc='Streaming Progress')
        while True:
            progress = progress_queue.get()
            if progress is None:
                break
            pbar.n = progress['total_duration_seconds']
            pbar.refresh()
            if progress['total_duration_seconds'] >= desired_duration_seconds:
                break
        pbar.close()
    else:
        # Continuous mode
        print("Streaming in continuous mode. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
