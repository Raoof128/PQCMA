#!/usr/bin/env python3
"""
Performance benchmarking for PQC Migration Auditor.

This script measures the performance characteristics of the scanning engine
under various conditions and workload sizes.
"""

import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
from pqc_migration_auditor.scanner.code_scanner import CodeScanner
from pqc_migration_auditor.analysis.rules import CryptoKnowledgeBase


class PerformanceBenchmark:
    """Performance benchmarking suite."""

    def __init__(self):
        self.scanner = CodeScanner()
        self.knowledge_base = CryptoKnowledgeBase()
        self.results: List[Dict[str, Any]] = []

    def create_test_file(self, size_kb: int) -> Path:
        """Create a test file of specified size."""
        temp_file = Path(tempfile.mktemp(suffix=".py"))

        # Create file with repetitive vulnerable code
        with open(temp_file, "w") as f:
            f.write("# Test file for performance benchmarking\n")
            f.write("from cryptography.hazmat.primitives.asymmetric import rsa\n")
            f.write("from cryptography.hazmat.primitives.asymmetric import ecdsa\n\n")

            # Fill file to target size
            current_size = temp_file.stat().st_size / 1024
            while current_size < size_kb:
                f.write("# RSA key generation\n")
                f.write("private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)\n")
                f.write("# ECDSA usage\n")
                f.write("ecdsa_key = ecdsa.generate_private_key()\n")
                f.write("\n")
                current_size = temp_file.stat().st_size / 1024

        return temp_file

    def create_test_directory(self, num_files: int, file_size_kb: int) -> Path:
        """Create a test directory with multiple files."""
        temp_dir = Path(tempfile.mkdtemp())

        for i in range(num_files):
            test_file = self.create_test_file(file_size_kb)
            shutil.move(str(test_file), str(temp_dir / f"test_file_{i}.py"))

        return temp_dir

    def benchmark_single_file(self, size_kb: int) -> Dict[str, Any]:
        """Benchmark scanning a single file of given size."""
        print(f"\nBenchmark: Single file ({size_kb}KB)")

        test_file = self.create_test_file(size_kb)

        try:
            start_time = time.time()
            findings = self.scanner.scan_file(test_file)
            end_time = time.time()

            duration = end_time - start_time
            findings_count = len(findings)

            result = {
                "test": "single_file",
                "file_size_kb": size_kb,
                "duration_seconds": duration,
                "findings_count": findings_count,
                "throughput_kb_per_second": size_kb / duration if duration > 0 else 0
            }

            print(f"  Duration: {duration:.4f}s")
            print(f"  Findings: {findings_count}")
            print(f"  Throughput: {result['throughput_kb_per_second']:.2f} KB/s")

            return result

        finally:
            test_file.unlink(missing_ok=True)

    def benchmark_directory_scan(self, num_files: int, file_size_kb: int) -> Dict[str, Any]:
        """Benchmark scanning a directory with multiple files."""
        print(f"\nBenchmark: Directory scan ({num_files} files x {file_size_kb}KB)")

        temp_dir = self.create_test_directory(num_files, file_size_kb)

        try:
            start_time = time.time()
            findings = self.scanner.scan_directory(temp_dir)
            end_time = time.time()

            duration = end_time - start_time
            findings_count = len(findings)
            total_size_kb = num_files * file_size_kb

            result = {
                "test": "directory_scan",
                "num_files": num_files,
                "file_size_kb": file_size_kb,
                "total_size_kb": total_size_kb,
                "duration_seconds": duration,
                "findings_count": findings_count,
                "throughput_kb_per_second": total_size_kb / duration if duration > 0 else 0,
                "files_per_second": num_files / duration if duration > 0 else 0
            }

            print(f"  Duration: {duration:.4f}s")
            print(f"  Findings: {findings_count}")
            print(f"  Throughput: {result['throughput_kb_per_second']:.2f} KB/s")
            print(f"  Files/sec: {result['files_per_second']:.2f}")

            return result

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def benchmark_pattern_matching(self, iterations: int = 10000) -> Dict[str, Any]:
        """Benchmark pattern matching performance."""
        print(f"\nBenchmark: Pattern matching ({iterations} iterations)")

        test_lines = [
            "private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)",
            "ecdsa_key = ecdsa.generate_private_key()",
            "cipher = AES.new(key, AES.MODE_GCM)",
            "normal code without crypto",
        ]

        start_time = time.time()
        total_findings = 0

        for _ in range(iterations):
            for line in test_lines:
                findings = self.scanner.scan_line(Path("benchmark.py"), 1, line)
                total_findings += len(findings)

        end_time = time.time()
        duration = end_time - start_time
        iterations_per_second = iterations / duration if duration > 0 else 0

        result = {
            "test": "pattern_matching",
            "iterations": iterations,
            "duration_seconds": duration,
            "iterations_per_second": iterations_per_second,
            "total_findings": total_findings
        }

        print(f"  Duration: {duration:.4f}s")
        print(f"  Iterations/sec: {iterations_per_second:.2f}")
        print(f"  Total findings: {total_findings}")

        return result

    def run_all_benchmarks(self):
        """Run all performance benchmarks."""
        print("=" * 60)
        print("PQC Migration Auditor - Performance Benchmarks")
        print("=" * 60)

        # Single file benchmarks (various sizes)
        for size in [10, 50, 100, 500]:
            result = self.benchmark_single_file(size)
            self.results.append(result)

        # Directory scan benchmarks
        for num_files, file_size in [(10, 10), (50, 10), (100, 5)]:
            result = self.benchmark_directory_scan(num_files, file_size)
            self.results.append(result)

        # Pattern matching benchmark
        result = self.benchmark_pattern_matching(10000)
        self.results.append(result)

        self.print_summary()

    def print_summary(self):
        """Print benchmark summary."""
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)

        # Single file benchmarks
        print("\nSingle File Scans:")
        print(f"{'Size (KB)':<12} {'Duration (s)':<15} {'Throughput (KB/s)':<20}")
        print("-" * 60)
        for r in self.results:
            if r["test"] == "single_file":
                print(f"{r['file_size_kb']:<12} {r['duration_seconds']:<15.4f} {r['throughput_kb_per_second']:<20.2f}")

        # Directory scans
        print("\nDirectory Scans:")
        print(f"{'Files':<10} {'Size (KB)':<12} {'Duration (s)':<15} {'Files/sec':<12}")
        print("-" * 60)
        for r in self.results:
            if r["test"] == "directory_scan":
                print(f"{r['num_files']:<10} {r['total_size_kb']:<12} {r['duration_seconds']:<15.4f} {r['files_per_second']:<12.2f}")

        # Pattern matching
        print("\nPattern Matching:")
        for r in self.results:
            if r["test"] == "pattern_matching":
                print(f"  Iterations: {r['iterations']}")
                print(f"  Duration: {r['duration_seconds']:.4f}s")
                print(f"  Throughput: {r['iterations_per_second']:.2f} iterations/sec")

        print("\n" + "=" * 60)


def main():
    """Run benchmarks."""
    benchmark = PerformanceBenchmark()
    benchmark.run_all_benchmarks()

    print("\nBenchmark complete!")
    print("Note: Results may vary based on system performance and load.")


if __name__ == "__main__":
    main()
