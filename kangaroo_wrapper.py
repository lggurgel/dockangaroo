#!/usr/bin/env python3
"""
Wrapper for Jean-Luc Pons' Kangaroo Tool
Optimized for distributed solving with multiple workers

Kangaroo uses Pollard's Kangaroo algorithm (ECDLP) which is ~2^67 times
faster than brute force for puzzle 135.
"""

import os
import sys
import json
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

# Configuration (loaded from environment variables via config.env)
PUZZLE_NUMBER = int(os.environ.get('PUZZLE_NUMBER', '135'))
TARGET_PUBLIC_KEY = os.environ.get('TARGET_PUBLIC_KEY', '02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16')
MIN_RANGE = 2 ** (PUZZLE_NUMBER - 1)
MAX_RANGE = 2 ** PUZZLE_NUMBER - 1

# Kangaroo Configuration
KANGAROO_BINARY = "/app/kangaroo/kangaroo"  # Path inside Docker container
DP_BITS = int(os.environ.get('DP_BITS', '18'))
WORK_SAVE_INTERVAL = int(os.environ.get('WORK_SAVE_INTERVAL', '60'))
WORK_DIR = Path("kangaroo_work")
DP_DIR = Path("distinguished_points")
RESULTS_DIR = Path("results")

# Create directories
WORK_DIR.mkdir(exist_ok=True)
DP_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)


class KangarooWrapper:
    """Wrapper for running JLP's Kangaroo with checkpoint and coordination."""

    def __init__(self, worker_id: int, num_workers: int):
        self.worker_id = worker_id
        self.num_workers = num_workers
        self.running = True
        self.process = None
        self.found_private_key = None  # Store found private key

        # Calculate this worker's range
        self.start_range, self.end_range = self._calculate_range()

        # File paths
        self.work_file = WORK_DIR / f"worker_{worker_id}.work"
        self.dp_file = DP_DIR / f"worker_{worker_id}_dp.txt"
        self.merged_dp_file = DP_DIR / "merged_dp.txt"
        self.status_file = WORK_DIR / f"worker_{worker_id}_status.json"

        # Rate limiting for periodic operations
        self.last_merge_time = time.time()
        self.last_status_update = time.time()
        self.status_update_interval = 5  # Only update status every 5 seconds

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\n[Worker {self.worker_id}] Received shutdown signal. Stopping Kangaroo...")
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def _calculate_range(self):
        """Calculate non-overlapping range for this worker."""
        total_range = MAX_RANGE - MIN_RANGE + 1
        range_per_worker = total_range // self.num_workers

        start = MIN_RANGE + (self.worker_id * range_per_worker)
        end = start + range_per_worker - 1 if self.worker_id < self.num_workers - 1 else MAX_RANGE

        return start, end

    def _create_input_file(self):
        """Create input file for Kangaroo."""
        input_file = WORK_DIR / f"worker_{self.worker_id}_input.txt"

        # Kangaroo input format (from README):
        # Line 1: Start range (hex, no 0x prefix)
        # Line 2: End range (hex, no 0x prefix)
        # Line 3+: Public key(s)
        with open(input_file, 'w') as f:
            # Format as hex without 0x prefix, uppercase
            start_hex = hex(self.start_range)[2:].upper()
            end_hex = hex(self.end_range)[2:].upper()

            f.write(f"{start_hex}\n")
            f.write(f"{end_hex}\n")
            f.write(f"{TARGET_PUBLIC_KEY}\n")

        return input_file

    def _build_kangaroo_command(self):
        """Build the Kangaroo command with proper arguments."""
        input_file = self._create_input_file()

        # Kangaroo command structure:
        # kangaroo [options] input_file
        # -t threads: Number of CPU threads
        # -d dpbits: Distinguished point bits
        # -w workfile: Work file for auto-saving
        # -i workfile: Load work file (only if exists)
        # Range is specified IN the input file as "start:end"

        # Check if GPU is enabled via environment variable
        gpu_enabled = os.getenv('GPU_ENABLED', '0') == '1'

        if gpu_enabled:
            # GPU mode (for cloud deployment with NVIDIA GPU)
            cmd = [
                KANGAROO_BINARY,
                "-gpu",  # Enable GPU mode
                "-g", "0",  # Use GPU device 0
                "-d", str(DP_BITS),  # Distinguished point bits
            ]
            print(f"[Worker {self.worker_id}] Using GPU acceleration mode")
        else:
            # CPU mode (default for Mac M1)
            cmd = [
                KANGAROO_BINARY,
                "-t", str(os.cpu_count() or 4),  # Use all available CPU cores
                "-d", str(DP_BITS),  # Distinguished point bits
            ]

        # Only load work file if it exists (for resume)
        if self.work_file.exists():
            cmd.extend(["-i", str(self.work_file)])
            print(f"[Worker {self.worker_id}] Resuming from existing work file")
        else:
            print(f"[Worker {self.worker_id}] Starting fresh (no existing work file)")

        # Always save work file
        cmd.extend([
            "-w", str(self.work_file),  # Save work file
            "-wi", str(WORK_SAVE_INTERVAL),  # Save interval from config
            str(input_file)  # Input file with pubkey and range
        ])

        return cmd

    def _check_kangaroo_installed(self):
        """Check if Kangaroo binary is available."""
        if not Path(KANGAROO_BINARY).exists():
            print(f"[Worker {self.worker_id}] ERROR: Kangaroo binary not found at {KANGAROO_BINARY}")
            print(f"[Worker {self.worker_id}] Please build Kangaroo first:")
            print(f"  cd /app && git clone https://github.com/JeanLucPons/Kangaroo.git kangaroo")
            print(f"  cd /app/kangaroo && make")
            return False
        return True

    def _parse_output(self, line: str):
        """Parse Kangaroo output for key information."""
        # Kangaroo outputs various status lines
        # We're interested in: DP count, operations, key found

        # IMPORTANT: Only "Priv:" indicates actual solution!
        # "Key# 0 Pub:" alone is just Kangaroo showing what it's searching for
        if "Priv:" in line or "priv:" in line.lower():
            # Extract private key from line like: "       Priv: 0xABCD1234..."
            private_key = line.split("Priv:")[-1].strip() if "Priv:" in line else line.split("priv:")[-1].strip()

            # Validate the private key
            try:
                # Remove 0x prefix if present
                clean_key = private_key
                if clean_key.startswith('0x') or clean_key.startswith('0X'):
                    clean_key = clean_key[2:]

                # Validate hex format
                private_key_int = int(clean_key, 16)

                # Validate it's in our search range
                if private_key_int < MIN_RANGE or private_key_int > MAX_RANGE:
                    print(f"\n[Worker {self.worker_id}] ⚠️  WARNING: Found key outside search range!")
                    print(f"[Worker {self.worker_id}] Key: {hex(private_key_int)}")
                    print(f"[Worker {self.worker_id}] Expected Range: {hex(MIN_RANGE)} to {hex(MAX_RANGE)}")
                    # Still store it - might be interesting

                print(f"\n[Worker {self.worker_id}] 🎉 PRIVATE KEY FOUND! 🎉")
                print(f"[Worker {self.worker_id}] Private Key: {private_key}")
                print(f"[Worker {self.worker_id}] Validated as: {hex(private_key_int)}")

                # Store for solution handler
                self.found_private_key = private_key
                return "FOUND"

            except ValueError as e:
                print(f"\n[Worker {self.worker_id}] ❌ ERROR: Invalid private key format!")
                print(f"[Worker {self.worker_id}] Raw output: {private_key}")
                print(f"[Worker {self.worker_id}] Error: {e}")
                return None

        # Update status periodically
        if "Dead" in line or "Ops" in line:
            self._update_status(line)

        return None

    def _update_status(self, status_line: str):
        """Update status file with current progress."""
        # Rate limit status updates to reduce I/O
        current_time = time.time()
        if current_time - self.last_status_update < self.status_update_interval:
            return

        self.last_status_update = current_time

        try:
            status_data = {
                'worker_id': self.worker_id,
                'timestamp': datetime.now().isoformat(),
                'status_line': status_line.strip(),
                'work_file': str(self.work_file),
                'range_start': hex(self.start_range),
                'range_end': hex(self.end_range)
            }

            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
        except Exception as e:
            # Log error but don't crash
            print(f"[Worker {self.worker_id}] Warning: Failed to update status: {e}", file=sys.stderr)

    def _merge_distinguished_points(self):
        """
        Merge distinguished points from all workers.
        This is crucial for Kangaroo algorithm efficiency.

        NOTE: This is primarily for monitoring. Kangaroo itself doesn't use the merged file.
        """
        try:
            # Check total size of DP files before loading to prevent OOM
            dp_files = list(DP_DIR.glob("worker_*_dp.txt"))
            total_size = sum(f.stat().st_size for f in dp_files if f.exists())

            # Skip merge if files are too large (> 500 MB)
            if total_size > 500 * 1024 * 1024:
                print(f"[Worker {self.worker_id}] Warning: DP files too large ({total_size / (1024*1024):.1f} MB), skipping merge", file=sys.stderr)
                return

            # Collect all DP files
            all_dps = set()
            dp_count = 0

            for worker_dp_file in dp_files:
                if worker_dp_file.exists():
                    with open(worker_dp_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                all_dps.add(line)
                                dp_count += 1

                                # Safety limit - don't load more than 10 million DPs
                                if dp_count > 10_000_000:
                                    print(f"[Worker {self.worker_id}] Warning: Too many DPs ({dp_count}), stopping merge", file=sys.stderr)
                                    return

            # Write merged DPs
            if all_dps:
                with open(self.merged_dp_file, 'w') as f:
                    f.write(f"# Merged Distinguished Points\n")
                    f.write(f"# Total: {len(all_dps)}\n")
                    f.write(f"# Updated: {datetime.now().isoformat()}\n")
                    for dp in sorted(all_dps):
                        f.write(f"{dp}\n")

        except Exception as e:
            print(f"[Worker {self.worker_id}] Warning: Error merging DPs: {e}", file=sys.stderr)

    def run(self):
        """Main execution loop."""
        print(f"\n[Worker {self.worker_id}] Starting Kangaroo wrapper...")
        print(f"[Worker {self.worker_id}] Range: {hex(self.start_range)} to {hex(self.end_range)}")
        print(f"[Worker {self.worker_id}] Target Public Key: {TARGET_PUBLIC_KEY}")
        print(f"[Worker {self.worker_id}] Distinguished Point Bits: {DP_BITS}")
        print(f"[Worker {self.worker_id}] Work file: {self.work_file}")
        print()

        # Check if Kangaroo is installed
        if not self._check_kangaroo_installed():
            return False

        # Build command
        cmd = self._build_kangaroo_command()

        print(f"[Worker {self.worker_id}] Launching Kangaroo...")
        print(f"[Worker {self.worker_id}] Command: {' '.join(cmd)}")
        print()

        try:
            # Start Kangaroo process
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # Monitor output
            for line in iter(self.process.stdout.readline, ''):
                if not self.running:
                    break

                # Print output
                print(f"[Worker {self.worker_id}] {line.rstrip()}")

                # Parse for important events
                result = self._parse_output(line)
                if result == "FOUND":
                    # Key found! Extract from Kangaroo output
                    self._handle_solution_found()
                    return True

                # Periodically merge DPs from all workers (for monitoring only)
                # Fixed: Use proper time tracking instead of modulo operation
                current_time = time.time()
                if current_time - self.last_merge_time >= 60:
                    self._merge_distinguished_points()
                    self.last_merge_time = current_time

            # Process ended
            self.process.wait()

            if self.process.returncode == 0:
                print(f"\n[Worker {self.worker_id}] Kangaroo completed successfully")
            else:
                print(f"\n[Worker {self.worker_id}] Kangaroo exited with code {self.process.returncode}")

            return False

        except Exception as e:
            print(f"\n[Worker {self.worker_id}] Error running Kangaroo: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            if self.process:
                self.process.terminate()

    def _handle_solution_found(self):
        """Handle when Kangaroo finds the solution."""
        print(f"\n[Worker {self.worker_id}] Processing found solution...")

        # Save the private key to results
        result_file = RESULTS_DIR / f"SOLUTION_FOUND_worker_{self.worker_id}.json"
        txt_file = RESULTS_DIR / f"SOLUTION_FOUND_worker_{self.worker_id}.txt"

        result_data = {
            'puzzle_number': PUZZLE_NUMBER,
            'method': 'Kangaroo (JLP)',
            'public_key': TARGET_PUBLIC_KEY,
            'private_key': self.found_private_key,
            'worker_id': self.worker_id,
            'found_timestamp': datetime.now().isoformat(),
            'search_range_start': hex(self.start_range),
            'search_range_end': hex(self.end_range),
            'work_file': str(self.work_file)
        }

        # Save as JSON
        with open(result_file, 'w') as f:
            json.dump(result_data, f, indent=2)

        # Also save as easy-to-read text file
        with open(txt_file, 'w') as f:
            f.write(f"🎉 PUZZLE {PUZZLE_NUMBER} SOLUTION FOUND! 🎉\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(f"Public Key:  {TARGET_PUBLIC_KEY}\n")
            f.write(f"Private Key: {self.found_private_key}\n\n")
            f.write(f"Found by: Worker {self.worker_id}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Search Range: {hex(self.start_range)} to {hex(self.end_range)}\n")
            f.write(f"Method: Pollard's Kangaroo (JLP)\n")

        # Also save to global solution file
        global_solution = RESULTS_DIR / "SOLUTION.json"
        with open(global_solution, 'w') as f:
            json.dump(result_data, f, indent=2)

        global_txt = RESULTS_DIR / "SOLUTION.txt"
        with open(global_txt, 'w') as f:
            f.write(f"🎉 PUZZLE {PUZZLE_NUMBER} SOLUTION FOUND! 🎉\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(f"Public Key:  {TARGET_PUBLIC_KEY}\n")
            f.write(f"Private Key: {self.found_private_key}\n\n")
            f.write(f"Found by: Worker {self.worker_id}\n")
            f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"[Worker {self.worker_id}] ✅ Solution saved to: {result_file}")
        print(f"[Worker {self.worker_id}] ✅ Private key saved to: {txt_file}")
        print(f"[Worker {self.worker_id}] 🎯 PRIVATE KEY: {self.found_private_key}")


def main():
    """Main entry point."""
    print("=" * 80)
    print("Bitcoin Puzzle 135 Solver - Kangaroo Wrapper")
    print("Using Jean-Luc Pons' Kangaroo (Pollard's Kangaroo Algorithm)")
    print("=" * 80)
    print(f"Target Public Key: {TARGET_PUBLIC_KEY}")
    print(f"Search Range: 2^{PUZZLE_NUMBER-1} to 2^{PUZZLE_NUMBER}-1")
    print(f"Algorithm: Pollard's Kangaroo (ECDLP)")
    print(f"Expected Complexity: O(√N) ≈ 2^67 operations")
    print("=" * 80)
    print()

    # Get worker configuration from environment
    num_workers = int(os.environ.get('NUM_WORKERS', '1'))
    worker_id = int(os.environ.get('WORKER_ID', '0'))

    print(f"Worker ID: {worker_id}")
    print(f"Total Workers: {num_workers}")
    print()

    # Run Kangaroo wrapper
    wrapper = KangarooWrapper(worker_id, num_workers)
    found = wrapper.run()

    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()

