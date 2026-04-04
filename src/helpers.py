def reorder_entries_of_yt_with_oldest_first(entries):
    """Return a reordered list of yt-dlp playlist entries with oldest videos first."""
    if not entries or not isinstance(entries, list):
        return entries

    def entry_order_key(entry):
        if not isinstance(entry, dict):
            return float('inf')

        upload_date = entry.get('upload_date')
        if upload_date:
            return upload_date

        playlist_index = entry.get('playlist_index') or entry.get('index') or entry.get('position')
        if playlist_index is not None:
            try:
                return int(playlist_index)
            except (TypeError, ValueError):
                pass

        return float('inf')

    if any(isinstance(entry, dict) and entry.get('upload_date') for entry in entries):
        sorted_entries = sorted(entries, key=entry_order_key)
        print("Ordering playlist entries by oldest upload_date first.")
        return sorted_entries

    if any(isinstance(entry, dict) and entry.get('playlist_index') for entry in entries):
        sorted_entries = sorted(entries, key=entry_order_key)
        print("Ordering playlist entries by playlist_index ascending.")
        return sorted_entries

    print("Reversing playlist entries to use oldest-first fallback ordering.")
    return list(reversed(entries))
