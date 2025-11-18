#!/usr/bin/env python3
"""
Kangaroo Solver Monitor

Monitors progress of all Kangaroo workers and displays
real-time statistics specific to Kangaroo algorithm.
"""

import os
import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

WORK_DIR = Path("kangaroo_work")
DP_DIR = Path("distinguished_points")
RESULTS_DIR = Path("results")

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def clear_screen():
    """Clear terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def load_worker_status(worker_id: int) -> Optional[Dict]:
    """Load status for a specific worker."""
    status_file = WORK_DIR / f"worker_{worker_id}_status.json"

    if not status_file.exists():
        return None

    try:
        with open(status_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        return None


def count_distinguished_points(worker_id: int = None) -> int:
    """Count distinguished points found by workers."""
    count = 0

    if worker_id is not None:
        # Count for specific worker
        dp_file = DP_DIR / f"worker_{worker_id}_dp.txt"
        if dp_file.exists():
            try:
                with open(dp_file, 'r') as f:
                    count = sum(1 for line in f if line.strip() and not line.startswith('#'))
            except:
                pass
    else:
        # Count all DPs (merged)
        merged_file = DP_DIR / "merged_dp.txt"
        if merged_file.exists():
            try:
                with open(merged_file, 'r') as f:
                    count = sum(1 for line in f if line.strip() and not line.startswith('#'))
            except:
                pass

    return count


def check_for_solution() -> Optional[Dict]:
    """Check if solution has been found."""
    solution_file = RESULTS_DIR / "SOLUTION.json"

    if solution_file.exists():
        try:
            with open(solution_file, 'r') as f:
                return json.load(f)
        except:
            return None

    return None


def get_worker_stats(num_workers: int) -> List[Dict]:
    """Get statistics for all Kangaroo workers."""
    stats = []

    for worker_id in range(num_workers):
        status = load_worker_status(worker_id)

        if status:
            timestamp_str = status.get('timestamp', '')
            try:
                last_update = datetime.fromisoformat(timestamp_str)
                time_since_update = (datetime.now() - last_update).total_seconds()
            except:
                time_since_update = float('inf')

            stats.append({
                'worker_id': worker_id,
                'active': time_since_update < 300,  # Active if updated in last 5 minutes
                'status_line': status.get('status_line', 'No status'),
                'last_update': timestamp_str,
                'time_since_update': time_since_update,
                'range_start': status.get('range_start', 'N/A'),
                'range_end': status.get('range_end', 'N/A')
            })
        else:
            stats.append({
                'worker_id': worker_id,
                'active': False,
                'status_line': 'Not started',
                'last_update': 'Never',
                'time_since_update': float('inf'),
                'range_start': 'N/A',
                'range_end': 'N/A'
            })

    return stats


def display_dashboard(num_workers: int = 10):
    """Display Kangaroo monitoring dashboard."""

    print(f"{Colors.CYAN}Starting Kangaroo monitoring dashboard...{Colors.ENDC}")
    print(f"{Colors.CYAN}Press Ctrl+C to exit{Colors.ENDC}\n")
    time.sleep(2)

    try:
        while True:
            clear_screen()

            # Check for solution
            solution = check_for_solution()
            if solution:
                print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
                print(f"{Colors.GREEN}{Colors.BOLD}🎉 SOLUTION FOUND! 🎉{Colors.ENDC}")
                print(f"{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
                print(f"Method: {solution.get('method', 'Kangaroo')}")
                print(f"Public Key: {solution.get('public_key')}")
                print(f"Found by Worker: {solution.get('worker_id')}")
                print(f"Timestamp: {solution.get('found_timestamp')}")
                print(f"Work file: {solution.get('work_file')}")
                print(f"\n{Colors.YELLOW}Check Kangaroo output and work file for private key!{Colors.ENDC}")
                print(f"\n{Colors.GREEN}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
                break

            # Header
            print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 100}{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}Bitcoin Puzzle 135 - Kangaroo Solver Monitor{Colors.ENDC}")
            print(f"{Colors.BOLD}{Colors.HEADER}{'=' * 100}{Colors.ENDC}\n")

            print(f"Algorithm: {Colors.YELLOW}Pollard's Kangaroo (ECDLP){Colors.ENDC}")
            print(f"Target: {Colors.YELLOW}02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16{Colors.ENDC}")
            print(f"Last Updated: {Colors.CYAN}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}\n")

            # Get worker statistics
            worker_stats = get_worker_stats(num_workers)

            # Calculate totals
            active_workers = sum(1 for w in worker_stats if w['active'])
            total_dps = count_distinguished_points()

            # Overall statistics
            print(f"{Colors.BOLD}Overall Statistics:{Colors.ENDC}")
            print(f"  Active Workers: {Colors.GREEN if active_workers > 0 else Colors.RED}"
                  f"{active_workers}/{num_workers}{Colors.ENDC}")
            print(f"  Distinguished Points Found: {Colors.CYAN}{total_dps:,}{Colors.ENDC}")
            print(f"  Expected Complexity: {Colors.YELLOW}~2^67 operations (much faster than brute force!){Colors.ENDC}\n")

            # Worker details
            print(f"{Colors.BOLD}Worker Details:{Colors.ENDC}\n")

            # Table header
            print(f"{'Worker':<10} {'Status':<12} {'Range Start':<35} {'Range End':<35} {'Last Update':<20}")
            print("-" * 110)

            # Worker rows
            for worker in worker_stats:
                worker_id = f"W-{worker['worker_id']}"

                if worker['active']:
                    status = f"{Colors.GREEN}●{Colors.ENDC} Active"
                else:
                    status = f"{Colors.RED}●{Colors.ENDC} Inactive"

                range_start = worker['range_start'][:32] + "..." if len(worker['range_start']) > 32 else worker['range_start']
                range_end = worker['range_end'][:32] + "..." if len(worker['range_end']) > 32 else worker['range_end']

                # Format last update
                if worker['last_update'] == 'Never':
                    last_update = "Never"
                else:
                    try:
                        dt = datetime.fromisoformat(worker['last_update'])
                        last_update = dt.strftime('%H:%M:%S')
                    except:
                        last_update = "Error"

                print(f"{worker_id:<10} {status:<21} {range_start:<35} {range_end:<35} {last_update:<20}")

            print("\n" + "-" * 110)

            # Kangaroo algorithm info
            print(f"\n{Colors.BOLD}Kangaroo Algorithm Info:{Colors.ENDC}")
            print(f"  - Each worker searches independently using random 'kangaroo jumps'")
            print(f"  - Distinguished Points (DPs) are shared between workers for collision detection")
            print(f"  - When two kangaroos collide, the private key can be computed")
            print(f"  - This is ~2^67 times faster than sequential brute force!")

            print(f"\n{Colors.CYAN}Refreshing in 10 seconds... (Press Ctrl+C to exit){Colors.ENDC}")

            time.sleep(10)

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Monitoring stopped by user.{Colors.ENDC}\n")
        sys.exit(0)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor Kangaroo solver progress')
    parser.add_argument('--workers', type=int, default=10,
                        help='Number of workers to monitor (default: 10)')

    args = parser.parse_args()

    # Create directories if they don't exist
    WORK_DIR.mkdir(exist_ok=True)
    DP_DIR.mkdir(exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    display_dashboard(args.workers)


if __name__ == "__main__":
    main()

