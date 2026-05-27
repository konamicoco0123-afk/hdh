def fifo_page_replacement(reference_string, num_frames):
    """Simulate FIFO page replacement.

    Args:
        reference_string (list[int]): Page reference sequence.
        num_frames (int): Number of page frames.

    Returns:
        dict: frame history, page fault positions, total faults.
    """
    frames = []
    frame_contents = [None] * num_frames
    next_replace = 0
    page_faults = []

    for step, page in enumerate(reference_string):
        if page not in frame_contents:
            frame_contents[next_replace] = page
            page_faults.append(step)
            next_replace = (next_replace + 1) % num_frames
        frames.append(frame_contents.copy())

    return {
        "algorithm": "FIFO",
        "references": reference_string,
        "frames": frames,
        "page_faults": page_faults,
        "total_page_faults": len(page_faults),
    }


def lru_page_replacement(reference_string, num_frames):
    """Simulate LRU page replacement.

    Args:
        reference_string (list[int]): Page reference sequence.
        num_frames (int): Number of page frames.

    Returns:
        dict: frame history, page fault positions, total faults.
    """
    frames = []
    frame_contents = []
    last_used = {}
    page_faults = []

    for step, page in enumerate(reference_string):
        if page not in frame_contents:
            if len(frame_contents) < num_frames:
                frame_contents.append(page)
            else:
                # find least recently used page
                lru_page = min(frame_contents, key=lambda p: last_used.get(p, -1))
                replace_index = frame_contents.index(lru_page)
                frame_contents[replace_index] = page
            page_faults.append(step)
        last_used[page] = step
        # maintain consistent frame length with None placeholders
        padded = frame_contents + [None] * (num_frames - len(frame_contents))
        frames.append(padded[:num_frames])

    return {
        "algorithm": "LRU",
        "references": reference_string,
        "frames": frames,
        "page_faults": page_faults,
        "total_page_faults": len(page_faults),
    }
