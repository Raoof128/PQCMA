"""
Console reporter for generating human-readable terminal output.
"""

from typing import List, Dict, Any
from ..analysis.recommendations import Finding, Recommendation
from ..analysis.rules import RiskLevel


class ConsoleReporter:
    """
    Generates console-friendly audit reports with formatting.
    """

    def __init__(self):
        # ANSI color codes
        self.COLORS = {
            "RED": "\033[91m",
            "YELLOW": "\033[93m",
            "GREEN": "\033[92m",
            "BLUE": "\033[94m",
            "CYAN": "\033[96m",
            "MAGENTA": "\033[95m",
            "BOLD": "\033[1m",
            "RESET": "\033[0m"
        }

    def print_report(
        self,
        findings: List[Finding],
        recommendations: List[Recommendation],
        summary: Dict[str, Any],
        scan_metadata: Dict[str, Any]
    ) -> None:
        """
        Print a formatted report to console.

        Args:
            findings: List of detected vulnerabilities
            recommendations: List of PQC recommendations
            summary: Summary statistics
            scan_metadata: Metadata about the scan
        """
        self._print_header()
        self._print_scan_info(scan_metadata)
        self._print_summary(summary)
        self._print_findings(findings)
        self._print_recommendations(recommendations)
        self._print_footer()

    def _print_header(self) -> None:
        """Print report header."""
        print()
        print(self._colorize("=" * 80, "BOLD"))
        print(self._colorize("  POST-QUANTUM CRYPTOGRAPHY (PQC) MIGRATION AUDIT REPORT", "BOLD", "CYAN"))
        print(self._colorize("  Aligned with NIST PQC Standards and ASD Guidance", "CYAN"))
        print(self._colorize("=" * 80, "BOLD"))
        print()

    def _print_scan_info(self, metadata: Dict[str, Any]) -> None:
        """Print scan information."""
        print(self._colorize("Scan Information:", "BOLD"))
        print(f"  Mode:   {metadata.get('mode', 'unknown')}")
        print(f"  Target: {metadata.get('target', 'unknown')}")
        print()

    def _print_summary(self, summary: Dict[str, Any]) -> None:
        """Print summary statistics."""
        print(self._colorize("Summary:", "BOLD"))
        print(f"  Total Findings:        {summary.get('total_findings', 0)}")
        print(f"  Quantum Vulnerable:    {self._colorize(str(summary.get('findings_by_risk', {}).get(RiskLevel.QUANTUM_VULNERABLE.value, 0)), 'RED')}")
        print(f"  Transitional:          {summary.get('findings_by_risk', {}).get(RiskLevel.TRANSITIONAL.value, 0)}")
        print()

        # Findings by type
        findings_by_type = summary.get('findings_by_type', {})
        if any(findings_by_type.values()):
            print(self._colorize("  Findings by Type:", "BOLD"))
            if findings_by_type.get('CODE', 0) > 0:
                print(f"    Code:          {findings_by_type['CODE']}")
            if findings_by_type.get('PCAP', 0) > 0:
                print(f"    Network (PCAP): {findings_by_type['PCAP']}")
            if findings_by_type.get('CERT', 0) > 0:
                print(f"    Certificates:   {findings_by_type['CERT']}")
            print()

        # Algorithms detected
        algorithms = summary.get('algorithms_detected', {})
        if algorithms:
            print(self._colorize("  Vulnerable Algorithms Detected:", "BOLD"))
            for algo, count in sorted(algorithms.items(), key=lambda x: x[1], reverse=True):
                print(f"    {algo:20s} {count} occurrence(s)")
            print()

    def _print_findings(self, findings: List[Finding]) -> None:
        """Print detailed findings."""
        if not findings:
            print(self._colorize("No quantum-vulnerable cryptography detected!", "GREEN", "BOLD"))
            print()
            return

        print(self._colorize("=" * 80, "BOLD"))
        print(self._colorize("Detailed Findings:", "BOLD", "YELLOW"))
        print(self._colorize("=" * 80, "BOLD"))
        print()

        for idx, finding in enumerate(findings, 1):
            risk_color = self._get_risk_color(finding.risk_level)

            print(f"{self._colorize(f'[{idx}]', 'BOLD')} {finding.finding_type} Finding")
            print(f"  Location:    {finding.location}")
            print(f"  Algorithm:   {self._colorize(finding.algorithm, risk_color, 'BOLD')}")

            if finding.key_size:
                print(f"  Key Size:    {finding.key_size} bits")

            print(f"  Risk Level:  {self._colorize(finding.risk_level, risk_color, 'BOLD')}")

            if finding.details:
                print(f"  Details:     {finding.details}")

            print()

    def _print_recommendations(self, recommendations: List[Recommendation]) -> None:
        """Print PQC migration recommendations."""
        if not recommendations:
            return

        print(self._colorize("=" * 80, "BOLD"))
        print(self._colorize("Post-Quantum Migration Recommendations:", "BOLD", "CYAN"))
        print(self._colorize("=" * 80, "BOLD"))
        print()

        # Group recommendations by vulnerable algorithm
        algo_recs: Dict[str, Recommendation] = {}
        for rec in recommendations:
            if rec.vulnerable_algorithm not in algo_recs:
                algo_recs[rec.vulnerable_algorithm] = rec

        for algo, rec in algo_recs.items():
            print(self._colorize(f"• {algo}", "BOLD", "YELLOW"))
            print(f"  Primary Replacement:     {self._colorize(rec.primary_replacement, 'GREEN')}")

            if rec.alternative_replacements:
                print(f"  Alternative Replacements:")
                for alt in rec.alternative_replacements:
                    print(f"    - {alt}")

            print(f"\n  Migration Guidance:")
            # Word wrap the guidance
            guidance_lines = self._wrap_text(rec.migration_guidance, 70)
            for line in guidance_lines:
                print(f"    {line}")

            print()

    def _print_footer(self) -> None:
        """Print report footer."""
        print(self._colorize("=" * 80, "BOLD"))
        print(self._colorize("Next Steps:", "BOLD", "MAGENTA"))
        print()
        print("  1. Review all quantum-vulnerable findings above")
        print("  2. Prioritize systems by criticality and data sensitivity")
        print("  3. Develop a phased PQC migration plan")
        print("  4. Engage vendors for PQC roadmap support")
        print("  5. Implement crypto-agile architecture")
        print("  6. Consider hybrid classical/PQC deployments during transition")
        print()
        print(self._colorize("References:", "BOLD"))
        print("  • NIST PQC Project: https://csrc.nist.gov/projects/post-quantum-cryptography")
        print("  • ASD PQC Guidance: https://www.cyber.gov.au/resources-business-and-government/")
        print("                      maintaining-devices-and-systems/cryptography/quantum-computing")
        print()
        print(self._colorize("=" * 80, "BOLD"))
        print()

    def _colorize(self, text: str, *colors: str) -> str:
        """
        Apply color codes to text.

        Args:
            text: Text to colorize
            *colors: Color names to apply

        Returns:
            Colored text string
        """
        color_codes = "".join(self.COLORS.get(c, "") for c in colors)
        reset_code = self.COLORS["RESET"]
        return f"{color_codes}{text}{reset_code}"

    def _get_risk_color(self, risk_level: str) -> str:
        """Get color for risk level."""
        risk_colors = {
            RiskLevel.QUANTUM_VULNERABLE.value: "RED",
            RiskLevel.TRANSITIONAL.value: "YELLOW",
            RiskLevel.PQC_SAFE.value: "GREEN",
            RiskLevel.UNKNOWN.value: "CYAN"
        }
        return risk_colors.get(risk_level, "CYAN")

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """
        Wrap text to specified width.

        Args:
            text: Text to wrap
            width: Maximum line width

        Returns:
            List of wrapped lines
        """
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            word_length = len(word)

            if current_length + word_length + len(current_line) <= width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = word_length

        if current_line:
            lines.append(" ".join(current_line))

        return lines
