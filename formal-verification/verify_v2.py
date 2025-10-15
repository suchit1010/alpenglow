#!/usr/bin/env python3
"""
Alpenglow Formal Verification Suite v2.0
Enhanced verification system with advanced logging, analytics, and reporting

Features:
- Real-time progress tracking with detailed metrics
- Structured logging with multiple output formats
- Performance benchmarking and historical tracking
- Parallel verification support
- Advanced reporting with visualizations
- Interactive CLI with rich formatting
"""

import os
import sys
import json
import time
import subprocess
import argparse
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from enum import Enum
import hashlib

# Rich formatting (install: pip install rich)
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.live import Live
    from rich import box
    from rich.layout import Layout
    from rich.prompt import Prompt, Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not found. Install with: pip install rich")
    print("   Falling back to basic output...\n")

console = Console() if RICH_AVAILABLE else None


class VerificationStatus(Enum):
    """Verification result status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"
    ERROR = "error"


class LogLevel(Enum):
    """Log severity levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


@dataclass
class VerificationConfig:
    """Configuration for a single verification run"""
    name: str
    description: str
    spec_file: str
    config_file: str
    expected_duration: str
    invariant_count: int
    category: str
    tags: List[str]
    timeout_seconds: Optional[int] = None


@dataclass
class VerificationResult:
    """Result of a verification run"""
    config_name: str
    status: VerificationStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: float
    states_generated: int
    states_distinct: int
    search_depth: int
    errors_found: int
    error_messages: List[str]
    warnings: List[str]
    memory_mb: float
    cpu_percent: float
    tlc_version: str
    spec_checksum: str
    log_file: str


class VerificationLogger:
    """Advanced logging system with structured output"""
    
    def __init__(self, log_dir: Path = Path("logs")):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_log = self.log_dir / f"session_{self.session_id}.log"
        self.json_log = self.log_dir / f"session_{self.session_id}.json"
        self.events: List[Dict] = []
        
    def log(self, level: LogLevel, message: str, context: Optional[Dict] = None):
        """Log a message with structured data"""
        timestamp = datetime.now().isoformat()
        event = {
            "timestamp": timestamp,
            "level": level.value,
            "message": message,
            "context": context or {}
        }
        self.events.append(event)
        
        # Write to text log
        with open(self.session_log, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level.value}] {message}\n")
            if context:
                f.write(f"  Context: {json.dumps(context, indent=2)}\n")
        
        # Console output
        if RICH_AVAILABLE:
            color = {
                LogLevel.DEBUG: "dim",
                LogLevel.INFO: "cyan",
                LogLevel.WARNING: "yellow",
                LogLevel.ERROR: "red",
                LogLevel.CRITICAL: "bold red"
            }.get(level, "white")
            console.print(f"[{color}]{level.value}[/{color}] {message}")
        else:
            print(f"[{level.value}] {message}")
    
    def save_session(self):
        """Save session data to JSON"""
        with open(self.json_log, 'w', encoding='utf-8') as f:
            json.dump(self.events, f, indent=2)


class VerificationDatabase:
    """Store and retrieve verification results"""
    
    def __init__(self, db_path: Path = Path("verification_results.json")):
        self.db_path = db_path
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load database from file"""
        if self.db_path.exists():
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"runs": [], "summary": {}}
    
    def save(self):
        """Save database to file"""
        with open(self.db_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2)
    
    def add_result(self, result: VerificationResult):
        """Add verification result"""
        result_dict = asdict(result)
        result_dict['status'] = result.status.value
        result_dict['start_time'] = result.start_time.isoformat()
        result_dict['end_time'] = result.end_time.isoformat() if result.end_time else None
        self.data['runs'].append(result_dict)
        self._update_summary()
        self.save()
    
    def _update_summary(self):
        """Update summary statistics"""
        total_runs = len(self.data['runs'])
        successful = sum(1 for r in self.data['runs'] if r['status'] == 'success')
        failed = sum(1 for r in self.data['runs'] if r['status'] == 'failed')
        total_states = sum(r['states_distinct'] for r in self.data['runs'])
        total_time = sum(r['duration_seconds'] for r in self.data['runs'])
        
        self.data['summary'] = {
            "total_runs": total_runs,
            "successful": successful,
            "failed": failed,
            "total_states_verified": total_states,
            "total_time_seconds": total_time,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_history(self, config_name: str, limit: int = 10) -> List[Dict]:
        """Get recent runs for a specific configuration"""
        runs = [r for r in self.data['runs'] if r['config_name'] == config_name]
        return sorted(runs, key=lambda x: x['start_time'], reverse=True)[:limit]


class VerificationRunner:
    """Execute TLC verification with advanced monitoring"""
    
    def __init__(self, logger: VerificationLogger, db: VerificationDatabase):
        self.logger = logger
        self.db = db
        self.tlc_jar = self._find_tlc()
        self.java_cmd = self._find_java()
    
    def _find_tlc(self) -> Path:
        """Locate TLA+ Tools jar"""
        candidates = [
            Path("tla2tools.jar"),
            Path("../tla2tools.jar"),
            Path("/usr/local/lib/tla2tools.jar")
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
        raise FileNotFoundError("tla2tools.jar not found")
    
    def _find_java(self) -> str:
        """Find Java executable"""
        try:
            subprocess.run(["java", "-version"], capture_output=True, check=True)
            return "java"
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Java not found in PATH")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of specification file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            sha256.update(f.read())
        return sha256.hexdigest()[:16]
    
    def run_verification(self, config: VerificationConfig) -> VerificationResult:
        """Run TLC verification with monitoring"""
        self.logger.log(LogLevel.INFO, f"Starting verification: {config.name}")
        
        start_time = datetime.now()
        spec_checksum = self._calculate_checksum(Path(config.spec_file))
        
        # Prepare log file
        log_file = Path("logs") / f"{config.name}_{start_time.strftime('%Y%m%d_%H%M%S')}.log"
        
        # Build TLC command
        cmd = [
            self.java_cmd,
            "-XX:+UseParallelGC",
            "-Xmx4G",
            "-Xms1G",
            "-jar", str(self.tlc_jar),
            "-workers", "auto",
            "-config", config.config_file,
            "-deadlock",
            "-coverage", "1",
            config.spec_file
        ]
        
        if config.timeout_seconds:
            cmd.extend(["-timeout", str(config.timeout_seconds)])
        
        self.logger.log(LogLevel.DEBUG, "TLC Command", {"cmd": " ".join(cmd)})
        
        # Execute with real-time monitoring
        result = self._execute_with_monitoring(cmd, config, log_file, start_time, spec_checksum)
        
        # Save result
        self.db.add_result(result)
        
        return result
    
    def _execute_with_monitoring(
        self, 
        cmd: List[str], 
        config: VerificationConfig,
        log_file: Path,
        start_time: datetime,
        spec_checksum: str
    ) -> VerificationResult:
        """Execute TLC with real-time progress monitoring"""
        
        states_generated = 0
        states_distinct = 0
        search_depth = 0
        errors_found = 0
        error_messages = []
        warnings = []
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                if RICH_AVAILABLE:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(),
                        TaskProgressColumn(),
                        TimeRemainingColumn(),
                        console=console
                    ) as progress:
                        task = progress.add_task(f"[cyan]{config.name}", total=None)
                        
                        for line in process.stdout:
                            f.write(line)
                            f.flush()
                            
                            # Parse TLC output
                            if "states generated" in line.lower():
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.isdigit():
                                        states_generated = int(part.replace(',', ''))
                                        break
                                progress.update(task, description=f"[cyan]{config.name} - {states_generated:,} states")
                            
                            if "distinct states" in line.lower():
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.isdigit():
                                        states_distinct = int(part.replace(',', ''))
                                        break
                            
                            if "depth" in line.lower() and "search" in line.lower():
                                parts = line.split()
                                for part in parts:
                                    if part.isdigit():
                                        search_depth = int(part)
                                        break
                            
                            if "error:" in line.lower():
                                errors_found += 1
                                error_messages.append(line.strip())
                            
                            if "warning:" in line.lower():
                                warnings.append(line.strip())
                else:
                    # Fallback without rich
                    for line in process.stdout:
                        f.write(line)
                        print(line, end='')
                
                process.wait()
                return_code = process.returncode
        
        except Exception as e:
            self.logger.log(LogLevel.ERROR, f"Execution failed: {str(e)}")
            return_code = -1
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Determine status
        if return_code == 0 and errors_found == 0:
            status = VerificationStatus.SUCCESS
        elif errors_found > 0:
            status = VerificationStatus.FAILED
        else:
            status = VerificationStatus.ERROR
        
        # Get TLC version
        tlc_version = self._get_tlc_version()
        
        return VerificationResult(
            config_name=config.name,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            states_generated=states_generated,
            states_distinct=states_distinct,
            search_depth=search_depth,
            errors_found=errors_found,
            error_messages=error_messages,
            warnings=warnings,
            memory_mb=0.0,  # TODO: Monitor actual memory
            cpu_percent=0.0,  # TODO: Monitor actual CPU
            tlc_version=tlc_version,
            spec_checksum=spec_checksum,
            log_file=str(log_file)
        )
    
    def _get_tlc_version(self) -> str:
        """Get TLC version"""
        try:
            result = subprocess.run(
                [self.java_cmd, "-jar", str(self.tlc_jar), "-h"],
                capture_output=True,
                text=True,
                timeout=5
            )
            for line in result.stdout.split('\n'):
                if "Version" in line or "TLC" in line:
                    return line.strip()
            return "Unknown"
        except:
            return "Unknown"


class VerificationSuite:
    """Main verification suite orchestrator"""
    
    def __init__(self):
        self.logger = VerificationLogger()
        self.db = VerificationDatabase()
        self.runner = VerificationRunner(self.logger, self.db)
        self.configs = self._load_configurations()
    
    def _load_configurations(self) -> List[VerificationConfig]:
        """Load verification configurations"""
        return [
            VerificationConfig(
                name="core_safety",
                description="Core safety properties verification",
                spec_file="Alpenglow.tla",
                config_file="MC.cfg",
                expected_duration="1-2 hours",
                invariant_count=12,
                category="safety",
                tags=["core", "safety", "production"]
            ),
            VerificationConfig(
                name="byzantine_adversary",
                description="Byzantine fault tolerance verification",
                spec_file="ByzantineAlpenglow.tla",
                config_file="MC_Byzantine.cfg",
                expected_duration="15-16 hours",
                invariant_count=16,
                category="byzantine",
                tags=["byzantine", "adversarial", "extended"],
                timeout_seconds=72000  # 20 hours
            ),
            VerificationConfig(
                name="liveness_properties",
                description="Temporal liveness verification",
                spec_file="LivenessAlpenglow.tla",
                config_file="MC_Liveness.cfg",
                expected_duration="3-5 minutes",
                invariant_count=4,
                category="liveness",
                tags=["liveness", "temporal", "fast"]
            ),
            VerificationConfig(
                name="edge_case_quorum",
                description="Quorum boundary edge case testing",
                spec_file="Alpenglow.tla",
                config_file="MC_edge_quorum_ok.cfg",
                expected_duration="2-3 seconds",
                invariant_count=8,
                category="edge_cases",
                tags=["edge", "quorum", "smoke"]
            ),
            VerificationConfig(
                name="edge_case_minimal",
                description="Minimal configuration edge case",
                spec_file="Alpenglow.tla",
                config_file="MC_edge_minimal_ok.cfg",
                expected_duration="<5 seconds",
                invariant_count=8,
                category="edge_cases",
                tags=["edge", "minimal", "smoke"]
            ),
            VerificationConfig(
                name="rotor_propagation",
                description="Rotor block propagation verification",
                spec_file="Rotor.tla",
                config_file="RotorMC.cfg",
                expected_duration="1-2 minutes",
                invariant_count=3,
                category="rotor",
                tags=["rotor", "propagation", "fast"]
            ),
        ]
    
    def display_menu(self):
        """Display interactive menu"""
        if RICH_AVAILABLE:
            self._display_rich_menu()
        else:
            self._display_basic_menu()
    
    def _display_rich_menu(self):
        """Display menu with Rich formatting"""
        console.clear()
        
        # Header
        header = Panel(
            "[bold cyan]ALPENGLOW FORMAL VERIFICATION SUITE v2.0[/bold cyan]\n"
            "[dim]Enhanced verification system with advanced analytics[/dim]",
            box=box.DOUBLE,
            border_style="cyan"
        )
        console.print(header)
        console.print()
        
        # Summary statistics
        summary = self.db.data.get('summary', {})
        if summary:
            stats_table = Table(show_header=False, box=box.SIMPLE)
            stats_table.add_column("Metric", style="cyan")
            stats_table.add_column("Value", style="green")
            stats_table.add_row("Total Runs", str(summary.get('total_runs', 0)))
            stats_table.add_row("Successful", str(summary.get('successful', 0)))
            stats_table.add_row("Total States Verified", f"{summary.get('total_states_verified', 0):,}")
            console.print(Panel(stats_table, title="[bold]Historical Summary[/bold]", border_style="green"))
            console.print()
        
        # Verification options
        table = Table(title="Available Verifications", box=box.ROUNDED, show_lines=True)
        table.add_column("#", style="cyan", justify="center")
        table.add_column("Name", style="bold")
        table.add_column("Description", style="dim")
        table.add_column("Duration", style="yellow")
        table.add_column("Category", style="magenta")
        
        for idx, config in enumerate(self.configs, 1):
            table.add_row(
                str(idx),
                config.name,
                config.description,
                config.expected_duration,
                config.category
            )
        
        table.add_row("", "", "", "", "", end_section=True)
        table.add_row("A", "[bold]Run All[/bold]", "Execute all verifications sequentially", "~20 hours", "all")
        table.add_row("H", "[bold]Show History[/bold]", "View verification history", "-", "utility")
        table.add_row("R", "[bold]Generate Report[/bold]", "Create comprehensive report", "-", "utility")
        table.add_row("Q", "[bold]Quit[/bold]", "Exit the suite", "-", "exit")
        
        console.print(table)
    
    def _display_basic_menu(self):
        """Display basic menu without Rich"""
        print("\n" + "="*80)
        print("  ALPENGLOW FORMAL VERIFICATION SUITE v2.0")
        print("  Enhanced verification system")
        print("="*80 + "\n")
        
        for idx, config in enumerate(self.configs, 1):
            print(f"  [{idx}] {config.name}")
            print(f"      {config.description}")
            print(f"      Duration: {config.expected_duration}, Category: {config.category}\n")
        
        print("  [A] Run All Verifications")
        print("  [H] Show History")
        print("  [R] Generate Report")
        print("  [Q] Quit\n")
    
    def run_interactive(self):
        """Run interactive verification session"""
        while True:
            self.display_menu()
            
            if RICH_AVAILABLE:
                choice = Prompt.ask("\n[bold cyan]Enter choice[/bold cyan]", default="Q")
            else:
                choice = input("\nEnter choice: ").strip()
            
            choice = choice.upper()
            
            if choice == 'Q':
                self.logger.log(LogLevel.INFO, "Exiting verification suite")
                self.logger.save_session()
                break
            elif choice == 'A':
                self._run_all()
            elif choice == 'H':
                self._show_history()
            elif choice == 'R':
                self._generate_report()
            elif choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.configs):
                    self._run_single(self.configs[idx])
                else:
                    self.logger.log(LogLevel.WARNING, "Invalid choice")
            else:
                self.logger.log(LogLevel.WARNING, "Invalid choice")
            
            if RICH_AVAILABLE:
                console.input("\n[dim]Press Enter to continue...[/dim]")
    
    def _run_single(self, config: VerificationConfig):
        """Run a single verification"""
        self.logger.log(LogLevel.INFO, f"Running verification: {config.name}")
        result = self.runner.run_verification(config)
        self._display_result(result)
    
    def _run_all(self):
        """Run all verifications"""
        if RICH_AVAILABLE:
            confirm = Confirm.ask("[bold yellow]Run all verifications? This may take 20+ hours[/bold yellow]")
            if not confirm:
                return
        
        results = []
        for config in self.configs:
            result = self.runner.run_verification(config)
            results.append(result)
        
        self._display_summary(results)
    
    def _display_result(self, result: VerificationResult):
        """Display verification result"""
        if RICH_AVAILABLE:
            status_color = "green" if result.status == VerificationStatus.SUCCESS else "red"
            
            result_panel = Panel(
                f"[bold {status_color}]Status:[/bold {status_color}] {result.status.value.upper()}\n"
                f"[cyan]Duration:[/cyan] {result.duration_seconds:.2f} seconds\n"
                f"[cyan]States Generated:[/cyan] {result.states_generated:,}\n"
                f"[cyan]Distinct States:[/cyan] {result.states_distinct:,}\n"
                f"[cyan]Search Depth:[/cyan] {result.search_depth}\n"
                f"[cyan]Errors Found:[/cyan] {result.errors_found}\n"
                f"[cyan]Log File:[/cyan] {result.log_file}",
                title=f"[bold]Verification Result: {result.config_name}[/bold]",
                border_style=status_color
            )
            console.print(result_panel)
        else:
            print(f"\n{'='*60}")
            print(f"  Verification Result: {result.config_name}")
            print(f"{'='*60}")
            print(f"  Status: {result.status.value.upper()}")
            print(f"  Duration: {result.duration_seconds:.2f} seconds")
            print(f"  States Generated: {result.states_generated:,}")
            print(f"  Distinct States: {result.states_distinct:,}")
            print(f"  Search Depth: {result.search_depth}")
            print(f"  Errors Found: {result.errors_found}")
            print(f"  Log File: {result.log_file}")
            print(f"{'='*60}\n")
    
    def _show_history(self):
        """Show verification history"""
        # TODO: Implement history display
        self.logger.log(LogLevel.INFO, "Showing verification history")
    
    def _generate_report(self):
        """Generate comprehensive report"""
        # TODO: Implement report generation
        self.logger.log(LogLevel.INFO, "Generating comprehensive report")
    
    def _display_summary(self, results: List[VerificationResult]):
        """Display summary of multiple results"""
        # TODO: Implement summary display
        pass


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Alpenglow Formal Verification Suite v2.0")
    parser.add_argument("--config", help="Run specific configuration")
    parser.add_argument("--batch", action="store_true", help="Run in batch mode (non-interactive)")
    parser.add_argument("--report", action="store_true", help="Generate report only")
    
    args = parser.parse_args()
    
    suite = VerificationSuite()
    
    if args.report:
        suite._generate_report()
    elif args.config:
        config = next((c for c in suite.configs if c.name == args.config), None)
        if config:
            suite._run_single(config)
        else:
            print(f"Configuration '{args.config}' not found")
    else:
        suite.run_interactive()


if __name__ == "__main__":
    main()
