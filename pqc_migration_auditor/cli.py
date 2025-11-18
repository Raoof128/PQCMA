"""
Command-line interface for the PQC Migration Auditor.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .scanner.code_scanner import CodeScanner
from .scanner.cert_scanner import CertificateScanner
from .scanner.pcap_scanner import PCAPScanner
from .analysis.recommendations import RecommendationEngine, Finding
from .reporting.console_reporter import ConsoleReporter
from .reporting.json_reporter import JSONReporter
from .reporting.html_reporter import HTMLReporter
from .utils.logging_utils import setup_logger, get_logger
from .utils.file_utils import validate_output_path
from . import __version__


class PQCAuditorCLI:
    """
    Command-line interface for the PQC Migration Auditor.
    """

    def __init__(self, verbose: bool = False):
        """
        Initialize the CLI.

        Args:
            verbose: Enable verbose logging
        """
        # Setup logging first
        setup_logger('pqc_migration_auditor', verbose=verbose)
        self.logger = get_logger(__name__)

        # Initialize components
        self.code_scanner = CodeScanner()
        self.cert_scanner = CertificateScanner()
        self.pcap_scanner = PCAPScanner()
        self.rec_engine = RecommendationEngine()
        self.console_reporter = ConsoleReporter()
        self.json_reporter = JSONReporter(__version__)
        self.html_reporter = HTMLReporter(__version__)

    def run(self, args: argparse.Namespace) -> int:
        """
        Run the auditor with the given arguments.

        Args:
            args: Parsed command-line arguments

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        self.logger.info(f"PQC Migration Auditor v{__version__}")
        self.logger.info(f"Mode: {args.mode}")
        self.logger.info(f"Target: {args.target}")

        # Validate output paths before scanning
        if args.output_json:
            json_path = validate_output_path(args.output_json, '.json')
            if not json_path:
                self.logger.error(f"Invalid JSON output path: {args.output_json}")
                print(f"Error: Invalid JSON output path: {args.output_json}", file=sys.stderr)
                return 1
            args.output_json = json_path

        if args.output_html:
            html_path = validate_output_path(args.output_html, '.html')
            if not html_path:
                self.logger.error(f"Invalid HTML output path: {args.output_html}")
                print(f"Error: Invalid HTML output path: {args.output_html}", file=sys.stderr)
                return 1
            args.output_html = html_path

        # Run scan based on mode
        findings: List[Finding] = []

        try:
            if args.mode == "code":
                findings = self._scan_code(args.target)
            elif args.mode == "pcap":
                findings = self._scan_pcap(args.target)
            else:
                self.logger.error(f"Unknown mode: {args.mode}")
                return 1

        except KeyboardInterrupt:
            print("\n\nScan interrupted by user", file=sys.stderr)
            return 130
        except Exception as e:
            self.logger.error(f"Error during scan: {e}", exc_info=True)
            print(f"Error during scan: {e}", file=sys.stderr)
            return 1

        # Check if any findings were generated
        if not findings:
            if not args.quiet:
                print("\n✓ No quantum-vulnerable cryptography detected!")
                print("  Your code appears to be using quantum-safe algorithms or no detectable crypto.")
            return 0

        # Generate recommendations
        self.logger.info("Generating PQC migration recommendations...")
        recommendations = []
        try:
            recommendations = [self.rec_engine.analyze_finding(f) for f in findings]
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {e}", exc_info=True)
            print(f"Warning: Could not generate recommendations: {e}", file=sys.stderr)

        # Generate summary
        try:
            summary = self.rec_engine.generate_report_summary(findings, recommendations)
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}", exc_info=True)
            summary = {
                "total_findings": len(findings),
                "critical_count": len([f for f in findings if f.risk_level == "QUANTUM_VULNERABLE"]),
                "findings_by_type": {},
                "findings_by_risk": {},
                "algorithms_detected": {}
            }

        # Get migration checklist
        migration_checklist = self.rec_engine.get_migration_checklist()

        # Scan metadata
        scan_metadata = {
            "mode": args.mode,
            "target": str(args.target)
        }

        # Console output (unless --quiet)
        if not args.quiet:
            try:
                self.console_reporter.print_report(
                    findings,
                    recommendations,
                    summary,
                    scan_metadata
                )
            except Exception as e:
                self.logger.error(f"Error printing console report: {e}", exc_info=True)
                print(f"Warning: Error displaying report: {e}", file=sys.stderr)

        # JSON output
        if args.output_json:
            try:
                self.logger.info(f"Writing JSON report to: {args.output_json}")
                json_report = self.json_reporter.generate_report(
                    findings,
                    recommendations,
                    summary,
                    scan_metadata,
                    migration_checklist
                )
                self.json_reporter.write_report(json_report, args.output_json)
                if not args.quiet:
                    print(f"\n✓ JSON report saved to: {args.output_json}")
            except Exception as e:
                self.logger.error(f"Error writing JSON report: {e}", exc_info=True)
                print(f"Error writing JSON report: {e}", file=sys.stderr)

        # HTML output
        if args.output_html:
            try:
                self.logger.info(f"Writing HTML report to: {args.output_html}")
                html_report = self.html_reporter.generate_report(
                    findings,
                    recommendations,
                    summary,
                    scan_metadata,
                    migration_checklist
                )
                self.html_reporter.write_report(html_report, args.output_html)
                if not args.quiet:
                    print(f"✓ HTML report saved to: {args.output_html}")
            except Exception as e:
                self.logger.error(f"Error writing HTML report: {e}", exc_info=True)
                print(f"Error writing HTML report: {e}", file=sys.stderr)

        # Summary message
        if not args.quiet:
            critical_count = summary.get('critical_count', 0)
            print(f"\n{'='*80}")
            print(f"Scan complete: {len(findings)} findings, {critical_count} quantum-vulnerable")
            print(f"{'='*80}\n")

        # Return non-zero if quantum-vulnerable findings detected
        return 1 if summary.get('critical_count', 0) > 0 else 0

    def _scan_code(self, target_path: str) -> List[Finding]:
        """
        Scan code directory.

        Args:
            target_path: Path to directory to scan

        Returns:
            List of findings
        """
        path = Path(target_path).resolve()

        if not path.exists():
            self.logger.error(f"Target path does not exist: {target_path}")
            raise FileNotFoundError(f"Target path does not exist: {target_path}")

        if not path.is_dir():
            self.logger.error(f"Target path is not a directory: {target_path}")
            raise NotADirectoryError(f"Target path is not a directory: {target_path}")

        findings: List[Finding] = []

        # Code scanning
        self.logger.info("Scanning source code...")
        code_findings = self.code_scanner.scan_directory(path)
        findings.extend(code_findings)

        # Certificate scanning
        self.logger.info("Scanning certificates...")
        try:
            cert_findings = self.cert_scanner.scan_directory(path)
            findings.extend(cert_findings)
        except Exception as e:
            self.logger.warning(f"Certificate scanning failed: {e}")
            # Continue without cert findings

        return findings

    def _scan_pcap(self, target_path: str) -> List[Finding]:
        """
        Scan PCAP file.

        Args:
            target_path: Path to PCAP file

        Returns:
            List of findings
        """
        path = Path(target_path).resolve()

        if not path.exists():
            self.logger.error(f"PCAP file does not exist: {target_path}")
            raise FileNotFoundError(f"PCAP file does not exist: {target_path}")

        if not path.is_file():
            self.logger.error(f"PCAP path is not a file: {target_path}")
            raise ValueError(f"PCAP path is not a file: {target_path}")

        self.logger.info("Scanning PCAP file...")
        findings = self.pcap_scanner.scan_pcap(path)

        return findings


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="pqc-auditor",
        description="Post-Quantum Cryptography (PQC) Migration Auditor - "
                    "Identify quantum-vulnerable cryptography and get NIST/ASD-aligned "
                    "migration recommendations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a code repository
  pqc-auditor --mode code --target ./my-project

  # Scan a PCAP file and generate reports
  pqc-auditor --mode pcap --target capture.pcap --output-json report.json --output-html report.html

  # Scan with verbose output
  pqc-auditor --mode code --target ./my-project --verbose

References:
  NIST PQC:  https://csrc.nist.gov/projects/post-quantum-cryptography
  ASD PQC:   https://www.cyber.gov.au/.../quantum-computing-and-post-quantum-cryptography

Developed in alignment with ASD's 2025 Post-Quantum Cryptography Guidelines.
        """
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--mode",
        required=True,
        choices=["code", "pcap"],
        help="Scan mode: 'code' for source code directory, 'pcap' for network capture file"
    )

    parser.add_argument(
        "--target",
        required=True,
        help="Target to scan (directory path for code mode, PCAP file path for pcap mode)"
    )

    parser.add_argument(
        "--output-json",
        help="Write machine-readable JSON report to specified file"
    )

    parser.add_argument(
        "--output-html",
        help="Write human-readable HTML report to specified file"
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress console output (useful with --output-json/--output-html)"
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.

    Args:
        argv: Command-line arguments (defaults to sys.argv)

    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    try:
        cli = PQCAuditorCLI(verbose=args.verbose)
        return cli.run(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        # Setup basic logger for uncaught exceptions
        logger = get_logger(__name__)
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"Unexpected error: {e}", file=sys.stderr)
        print("Run with --verbose for more details", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
