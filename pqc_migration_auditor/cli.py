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
from . import __version__


logger = get_logger(__name__)


class PQCAuditorCLI:
    """
    Command-line interface for the PQC Migration Auditor.
    """

    def __init__(self):
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
        # Setup logging
        setup_logger(__name__, verbose=args.verbose)

        logger.info(f"PQC Migration Auditor v{__version__}")
        logger.info(f"Mode: {args.mode}")
        logger.info(f"Target: {args.target}")

        # Run scan based on mode
        findings: List[Finding] = []

        if args.mode == "code":
            findings = self._scan_code(args.target)
        elif args.mode == "pcap":
            findings = self._scan_pcap(args.target)
        else:
            logger.error(f"Unknown mode: {args.mode}")
            return 1

        # Generate recommendations
        logger.info("Generating PQC migration recommendations...")
        recommendations = [self.rec_engine.analyze_finding(f) for f in findings]

        # Generate summary
        summary = self.rec_engine.generate_report_summary(findings, recommendations)

        # Get migration checklist
        migration_checklist = self.rec_engine.get_migration_checklist()

        # Scan metadata
        scan_metadata = {
            "mode": args.mode,
            "target": str(args.target)
        }

        # Console output (unless --quiet)
        if not args.quiet:
            self.console_reporter.print_report(
                findings,
                recommendations,
                summary,
                scan_metadata
            )

        # JSON output
        if args.output_json:
            logger.info(f"Writing JSON report to: {args.output_json}")
            json_report = self.json_reporter.generate_report(
                findings,
                recommendations,
                summary,
                scan_metadata,
                migration_checklist
            )
            self.json_reporter.write_report(json_report, Path(args.output_json))

        # HTML output
        if args.output_html:
            logger.info(f"Writing HTML report to: {args.output_html}")
            html_report = self.html_reporter.generate_report(
                findings,
                recommendations,
                summary,
                scan_metadata,
                migration_checklist
            )
            self.html_reporter.write_report(html_report, Path(args.output_html))

        # Summary message
        if not args.quiet:
            print(f"\nScan complete: {len(findings)} findings, {summary['critical_count']} quantum-vulnerable")

        # Return non-zero if quantum-vulnerable findings detected
        return 1 if summary['critical_count'] > 0 else 0

    def _scan_code(self, target_path: str) -> List[Finding]:
        """
        Scan code directory.

        Args:
            target_path: Path to directory to scan

        Returns:
            List of findings
        """
        path = Path(target_path)

        if not path.exists():
            logger.error(f"Target path does not exist: {target_path}")
            return []

        findings: List[Finding] = []

        # Code scanning
        logger.info("Scanning source code...")
        code_findings = self.code_scanner.scan_directory(path)
        findings.extend(code_findings)

        # Certificate scanning
        logger.info("Scanning certificates...")
        cert_findings = self.cert_scanner.scan_directory(path)
        findings.extend(cert_findings)

        return findings

    def _scan_pcap(self, target_path: str) -> List[Finding]:
        """
        Scan PCAP file.

        Args:
            target_path: Path to PCAP file

        Returns:
            List of findings
        """
        path = Path(target_path)

        if not path.exists():
            logger.error(f"PCAP file does not exist: {target_path}")
            return []

        logger.info("Scanning PCAP file...")
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
        cli = PQCAuditorCLI()
        return cli.run(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
