#!/usr/bin/env python3
"""
Bitcoin Puzzle 135 Solver - Statistics and Performance Analysis

This script analyzes checkpoint data to provide detailed statistics
about solving performance, time estimates, and more.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

CHECKPOINT_DIR = Path("checkpoints")
MIN_RANGE = 2 ** 134
MAX_RANGE = 2 ** 135 - 1
TOTAL_KEYS = MAX_RANGE - MIN_RANGE + 1


def load_checkpoints(num_workers: int = 10) -> List[Dict]:
    """Load all checkpoint files."""
    checkpoints = []

    for worker_id in range(num_workers):
        checkpoint_file = CHECKPOINT_DIR / f"worker_{worker_id}.json"

        if checkpoint_file.exists():
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    checkpoints.append(data)
            except Exception as e:
                print(f"Warning: Could not load checkpoint for worker {worker_id}: {e}")

    return checkpoints


def calculate_statistics(checkpoints: List[Dict]) -> Dict:
    """Calculate comprehensive statistics from checkpoints."""
    if not checkpoints:
        return {
            'total_keys_checked': 0,
            'total_workers': 0,
            'active_workers': 0,
            'progress_percent': 0.0,
            'avg_keys_per_worker': 0,
            'estimated_speed': 0,
            'estimated_completion': 'Unknown'
        }

    total_keys_checked = sum(c.get('keys_checked', 0) for c in checkpoints)
    total_workers = len(checkpoints)

    # Calculate active workers (updated in last 5 minutes)
    active_workers = 0
    now = datetime.now()
    for checkpoint in checkpoints:
        try:
            timestamp = datetime.fromisoformat(checkpoint.get('timestamp', ''))
            if (now - timestamp).total_seconds() < 300:
                active_workers += 1
        except:
            pass

    # Calculate progress
    progress_percent = (total_keys_checked / TOTAL_KEYS) * 100

    # Calculate average keys per worker
    avg_keys_per_worker = total_keys_checked / total_workers if total_workers > 0 else 0

    # Estimate speed (keys/second)
    # This is a rough estimate based on time since start
    estimated_speed = 0
    if checkpoints:
        try:
            # Find the earliest start time
            earliest_time = None
            for checkpoint in checkpoints:
                try:
                    timestamp = datetime.fromisoformat(checkpoint.get('timestamp', ''))
                    if earliest_time is None or timestamp < earliest_time:
                        earliest_time = timestamp
                except:
                    pass

            if earliest_time:
                elapsed_seconds = (now - earliest_time).total_seconds()
                if elapsed_seconds > 0:
                    estimated_speed = total_keys_checked / elapsed_seconds
        except:
            pass

    # Estimate completion time
    if estimated_speed > 0:
        keys_remaining = TOTAL_KEYS - total_keys_checked
        seconds_remaining = keys_remaining / estimated_speed

        # Handle very large time estimates (avoid timedelta overflow)
        MAX_SECONDS = 86400 * 999999999  # Max days * seconds per day

        if seconds_remaining > MAX_SECONDS:
            years_remaining = seconds_remaining / (365.25 * 24 * 3600)
            estimated_completion = f"{years_remaining:.2e} years"
        else:
            try:
                estimated_completion = str(timedelta(seconds=int(seconds_remaining)))
            except (OverflowError, OSError):
                years_remaining = seconds_remaining / (365.25 * 24 * 3600)
                estimated_completion = f"{years_remaining:.2e} years"
    else:
        estimated_completion = 'Unknown'

    return {
        'total_keys_checked': total_keys_checked,
        'total_workers': total_workers,
        'active_workers': active_workers,
        'progress_percent': progress_percent,
        'avg_keys_per_worker': avg_keys_per_worker,
        'estimated_speed': estimated_speed,
        'estimated_completion': estimated_completion
    }


def print_statistics(stats: Dict):
    """Print statistics in a formatted way."""
    print("\n" + "=" * 80)
    print("Bitcoin Puzzle 135 - Detailed Statistics")
    print("=" * 80 + "\n")

    print("Overall Progress:")
    print(f"  Total Keys Checked:    {stats['total_keys_checked']:>25,}")
    print(f"  Total Keys in Range:   {TOTAL_KEYS:>25,}")
    print(f"  Progress:              {stats['progress_percent']:>24.12f}%")
    print()

    print("Workers:")
    print(f"  Total Workers:         {stats['total_workers']:>25,}")
    print(f"  Active Workers:        {stats['active_workers']:>25,}")
    print(f"  Avg Keys per Worker:   {stats['avg_keys_per_worker']:>25,.0f}")
    print()

    print("Performance:")
    print(f"  Estimated Speed:       {stats['estimated_speed']:>25,.0f} keys/sec")

    if stats['estimated_speed'] > 0:
        keys_per_minute = stats['estimated_speed'] * 60
        keys_per_hour = stats['estimated_speed'] * 3600
        keys_per_day = stats['estimated_speed'] * 86400

        print(f"                         {keys_per_minute:>25,.0f} keys/min")
        print(f"                         {keys_per_hour:>25,.0f} keys/hour")
        print(f"                         {keys_per_day:>25,.0f} keys/day")
    print()

    print("Time Estimates:")
    print(f"  Est. Completion Time:  {stats['estimated_completion']}")

    if stats['estimated_speed'] > 0:
        # Calculate years
        keys_remaining = TOTAL_KEYS - stats['total_keys_checked']
        seconds_remaining = keys_remaining / stats['estimated_speed']
        years_remaining = seconds_remaining / (365.25 * 24 * 3600)

        print(f"  (Approximately:        {years_remaining:>25.2e} years)")
    print()

    print("Reality Check:")
    print(f"  Search Space:          ~2^134 keys")
    print(f"  Current Speed:         ~{stats['estimated_speed']:,.0f} keys/second")
    print(f"  Probability per Key:   ~{1/TOTAL_KEYS:.2e}")
    print()

    # Calculate probability of finding it in next N keys
    if stats['estimated_speed'] > 0:
        next_hour_keys = stats['estimated_speed'] * 3600
        next_day_keys = stats['estimated_speed'] * 86400
        next_year_keys = stats['estimated_speed'] * 365.25 * 24 * 3600

        prob_hour = (next_hour_keys / TOTAL_KEYS) * 100
        prob_day = (next_day_keys / TOTAL_KEYS) * 100
        prob_year = (next_year_keys / TOTAL_KEYS) * 100

        print("Probability of Finding Solution:")
        print(f"  Next Hour:             {prob_hour:>25.2e}%")
        print(f"  Next Day:              {prob_day:>25.2e}%")
        print(f"  Next Year:             {prob_year:>25.2e}%")

    print("\n" + "=" * 80 + "\n")


def print_worker_details(checkpoints: List[Dict]):
    """Print detailed statistics for each worker."""
    if not checkpoints:
        print("No checkpoint data available.\n")
        return

    print("=" * 80)
    print("Worker Details")
    print("=" * 80 + "\n")

    # Sort by worker_id
    checkpoints_sorted = sorted(checkpoints, key=lambda x: x.get('worker_id', 0))

    for checkpoint in checkpoints_sorted:
        worker_id = checkpoint.get('worker_id', 'Unknown')
        keys_checked = checkpoint.get('keys_checked', 0)
        progress = checkpoint.get('progress_percent', 0)
        current_key = checkpoint.get('current_key', 0)
        start_key = checkpoint.get('start_key', 0)
        end_key = checkpoint.get('end_key', 0)
        timestamp = checkpoint.get('timestamp', 'Unknown')

        # Calculate worker's range
        worker_range = end_key - start_key + 1

        print(f"Worker {worker_id}:")
        print(f"  Range:          {hex(start_key)} to {hex(end_key)}")
        print(f"  Keys in Range:  {worker_range:,}")
        print(f"  Keys Checked:   {keys_checked:,}")
        print(f"  Progress:       {progress:.6f}%")
        print(f"  Current Key:    {hex(current_key)}")
        print(f"  Last Update:    {timestamp}")
        print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze Bitcoin puzzle solver statistics')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of workers (default: 10)')
    parser.add_argument('--details', action='store_true',
                       help='Show detailed per-worker statistics')

    args = parser.parse_args()

    # Load checkpoints
    checkpoints = load_checkpoints(args.workers)

    if not checkpoints:
        print("\n❌ No checkpoint data found. Start the solver first!\n")
        return

    # Calculate and print statistics
    stats = calculate_statistics(checkpoints)
    print_statistics(stats)

    # Print worker details if requested
    if args.details:
        print_worker_details(checkpoints)


if __name__ == "__main__":
    main()

