"""
HTML reporter for generating web-viewable audit reports.
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from ..analysis.recommendations import Finding, Recommendation
from ..analysis.rules import RiskLevel
from ..utils.logging_utils import get_logger


logger = get_logger(__name__)


class HTMLReporter:
    """
    Generates HTML-format audit reports.
    """

    def __init__(self, tool_version: str = "1.0.0"):
        self.tool_version = tool_version

    def generate_report(
        self,
        findings: List[Finding],
        recommendations: List[Recommendation],
        summary: Dict[str, Any],
        scan_metadata: Dict[str, Any],
        migration_checklist: List[Dict[str, Any]]
    ) -> str:
        """
        Generate an HTML report.

        Args:
            findings: List of detected vulnerabilities
            recommendations: List of PQC recommendations
            summary: Summary statistics
            scan_metadata: Metadata about the scan
            migration_checklist: PQC migration checklist

        Returns:
            HTML string
        """
        html = self._generate_html_header()
        html += self._generate_html_body(
            findings,
            recommendations,
            summary,
            scan_metadata,
            migration_checklist
        )
        html += self._generate_html_footer()

        return html

    def write_report(
        self,
        html_content: str,
        output_path: Path
    ) -> None:
        """
        Write HTML report to file.

        Args:
            html_content: HTML content string
            output_path: Path to output file
        """
        try:
            with open(output_path, 'w') as f:
                f.write(html_content)
            logger.info(f"HTML report written to: {output_path}")
        except Exception as e:
            logger.error(f"Error writing HTML report: {e}")

    def _generate_html_header(self) -> str:
        """Generate HTML header with styles."""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PQC Migration Audit Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .section {
            background: white;
            padding: 25px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .finding {
            background: #fff;
            border-left: 4px solid #dc3545;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 4px;
        }
        .finding.quantum-vulnerable {
            border-left-color: #dc3545;
        }
        .finding.transitional {
            border-left-color: #ffc107;
        }
        .finding.pqc-safe {
            border-left-color: #28a745;
        }
        .finding-header {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .finding-detail {
            margin: 5px 0;
        }
        .finding-detail strong {
            display: inline-block;
            width: 120px;
        }
        .recommendation {
            background: #e7f3ff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            border-left: 4px solid #0066cc;
        }
        .recommendation h3 {
            color: #0066cc;
            margin-top: 0;
        }
        .recommendation .guidance {
            background: white;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
        }
        .checklist {
            list-style: none;
            padding: 0;
        }
        .checklist-phase {
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .checklist-phase h3 {
            color: #667eea;
            margin-top: 0;
        }
        .checklist-phase ul {
            margin: 10px 0 0 0;
        }
        .checklist-phase li {
            margin: 5px 0;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            font-weight: bold;
        }
        .badge-danger {
            background: #dc3545;
            color: white;
        }
        .badge-warning {
            background: #ffc107;
            color: #333;
        }
        .badge-success {
            background: #28a745;
            color: white;
        }
        .badge-info {
            background: #17a2b8;
            color: white;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
"""

    def _generate_html_body(
        self,
        findings: List[Finding],
        recommendations: List[Recommendation],
        summary: Dict[str, Any],
        scan_metadata: Dict[str, Any],
        migration_checklist: List[Dict[str, Any]]
    ) -> str:
        """Generate HTML body content."""
        html = f"""
    <div class="header">
        <h1>🔐 Post-Quantum Cryptography Migration Audit Report</h1>
        <p>Aligned with NIST PQC Standards and ASD Guidance</p>
        <p><small>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Tool Version: {self.tool_version}</small></p>
    </div>

    <div class="section">
        <h2>📊 Executive Summary</h2>
        <div class="summary-grid">
            <div class="summary-card">
                <h3>Total Findings</h3>
                <div class="value">{summary.get('total_findings', 0)}</div>
            </div>
            <div class="summary-card">
                <h3>Quantum Vulnerable</h3>
                <div class="value" style="color: #dc3545;">{summary.get('findings_by_risk', {}).get(RiskLevel.QUANTUM_VULNERABLE.value, 0)}</div>
            </div>
            <div class="summary-card">
                <h3>Scan Mode</h3>
                <div class="value" style="font-size: 1.2em;">{scan_metadata.get('mode', 'unknown').upper()}</div>
            </div>
            <div class="summary-card">
                <h3>Target</h3>
                <div class="value" style="font-size: 0.8em; word-break: break-all;">{scan_metadata.get('target', 'unknown')}</div>
            </div>
        </div>

        <h3>Vulnerable Algorithms Detected</h3>
        <table>
            <tr>
                <th>Algorithm</th>
                <th>Occurrences</th>
                <th>Risk Level</th>
            </tr>
"""

        algorithms = summary.get('algorithms_detected', {})
        for algo, count in sorted(algorithms.items(), key=lambda x: x[1], reverse=True):
            html += f"""
            <tr>
                <td><strong>{algo}</strong></td>
                <td>{count}</td>
                <td><span class="badge badge-danger">QUANTUM VULNERABLE</span></td>
            </tr>
"""

        html += """
        </table>
    </div>
"""

        # Findings section
        if findings:
            html += """
    <div class="section">
        <h2>🔍 Detailed Findings</h2>
"""

            for idx, finding in enumerate(findings, 1):
                risk_class = finding.risk_level.lower().replace('_', '-')
                badge_class = self._get_badge_class(finding.risk_level)

                html += f"""
        <div class="finding {risk_class}">
            <div class="finding-header">[{idx}] {finding.finding_type} Finding</div>
            <div class="finding-detail"><strong>Location:</strong> <code>{finding.location}</code></div>
            <div class="finding-detail"><strong>Algorithm:</strong> {finding.algorithm} <span class="badge {badge_class}">{finding.risk_level}</span></div>
"""

                if finding.key_size:
                    html += f"""            <div class="finding-detail"><strong>Key Size:</strong> {finding.key_size} bits</div>
"""

                if finding.details:
                    html += f"""            <div class="finding-detail"><strong>Details:</strong> {finding.details}</div>
"""

                html += """        </div>
"""

            html += """    </div>
"""

        # Recommendations section
        if recommendations:
            # Group by algorithm
            algo_recs: Dict[str, Recommendation] = {}
            for rec in recommendations:
                if rec.vulnerable_algorithm not in algo_recs:
                    algo_recs[rec.vulnerable_algorithm] = rec

            html += """
    <div class="section">
        <h2>💡 Post-Quantum Migration Recommendations</h2>
"""

            for algo, rec in algo_recs.items():
                html += f"""
        <div class="recommendation">
            <h3>🔄 Migration Path for {algo}</h3>
            <p><strong>Primary Replacement:</strong> <span style="color: #28a745; font-weight: bold;">{rec.primary_replacement}</span></p>
"""

                if rec.alternative_replacements:
                    html += """            <p><strong>Alternative Replacements:</strong></p>
            <ul>
"""
                    for alt in rec.alternative_replacements:
                        html += f"""                <li>{alt}</li>
"""
                    html += """            </ul>
"""

                html += f"""
            <div class="guidance">
                <strong>Migration Guidance:</strong>
                <p>{rec.migration_guidance}</p>
            </div>
        </div>
"""

            html += """    </div>
"""

        # Migration checklist
        if migration_checklist:
            html += """
    <div class="section">
        <h2>✅ PQC Migration Checklist</h2>
        <div class="checklist">
"""

            for phase in migration_checklist:
                html += f"""
            <div class="checklist-phase">
                <h3>📌 {phase['phase']}</h3>
                <ul>
"""
                for task in phase['tasks']:
                    html += f"""                    <li>{task}</li>
"""

                html += """                </ul>
            </div>
"""

            html += """        </div>
    </div>
"""

        # References
        html += """
    <div class="section">
        <h2>📚 References & Resources</h2>
        <ul>
            <li><strong>NIST Post-Quantum Cryptography Project:</strong><br>
                <a href="https://csrc.nist.gov/projects/post-quantum-cryptography" target="_blank">
                    https://csrc.nist.gov/projects/post-quantum-cryptography
                </a>
            </li>
            <li><strong>Australian Signals Directorate - Quantum Computing & PQC:</strong><br>
                <a href="https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/cryptography/quantum-computing-and-post-quantum-cryptography" target="_blank">
                    https://www.cyber.gov.au/resources-business-and-government/maintaining-devices-and-systems/cryptography/quantum-computing-and-post-quantum-cryptography
                </a>
            </li>
            <li><strong>NIST FIPS 203 (ML-KEM):</strong> Module-Lattice-Based Key Encapsulation Mechanism</li>
            <li><strong>NIST FIPS 204 (ML-DSA):</strong> Module-Lattice-Based Digital Signature Algorithm</li>
            <li><strong>NIST FIPS 205 (SLH-DSA):</strong> Stateless Hash-Based Digital Signature Algorithm</li>
        </ul>
    </div>
"""

        return html

    def _generate_html_footer(self) -> str:
        """Generate HTML footer."""
        return """
    <div class="footer">
        <p>This report was generated by the <strong>Post-Quantum Cryptography Migration Auditor</strong></p>
        <p>Developed in alignment with ASD's 2025 Post-Quantum Cryptography Guidelines</p>
    </div>
</body>
</html>
"""

    def _get_badge_class(self, risk_level: str) -> str:
        """Get CSS badge class for risk level."""
        badge_classes = {
            RiskLevel.QUANTUM_VULNERABLE.value: "badge-danger",
            RiskLevel.TRANSITIONAL.value: "badge-warning",
            RiskLevel.PQC_SAFE.value: "badge-success",
            RiskLevel.UNKNOWN.value: "badge-info"
        }
        return badge_classes.get(risk_level, "badge-info")
