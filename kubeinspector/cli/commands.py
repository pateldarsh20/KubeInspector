import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress

from ..core.scanner import Scanner
from ..core.inspector import Inspector
from ..core.fixer import Fixer
from ..personality.response_builder import ResponseBuilder

console = Console()
mate = ResponseBuilder()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """⚓ KubeInspector - Yer Kubernetes Seaworthiness Inspector 🏴☠️"""
    pass

@cli.command()
@click.option('--path', '-p', default='.', help='Path to scan for K8s YAML files')
@click.option('--namespace', '-n', default=None, help='Filter by namespace')
@click.option('--output', '-o', default='terminal', help='Output format: terminal, json')
def inspect(path, namespace, output):
    """
    Inspect yer Kubernetes YAML files against the Captain's Checklist.
    """
    console.print(f"\n[bold cyan]{mate.greeting()}[/bold cyan]\n")
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Scanning the ship...", total=100)
        
        scanner = Scanner(path)
        progress.update(task, advance=20, description="[cyan]Scanning YAML files...")
        scanned = scanner.scan()
        
        progress.update(task, advance=40, description="[cyan]Running inspections...")
        
        inspector = Inspector()
        report = inspector.inspect_all(scanned)
        
        progress.update(task, advance=30, description="[cyan]Generating report...")
        
        if namespace and output == 'terminal':
            report = inspector.filter_by_namespace(report, namespace)
        
        progress.update(task, advance=10, description="[green]Done!")
    
    if output == 'json':
        import json
        console.print(json.dumps(report, indent=2))
        return
    
    _display_terminal_report(report, scanned)
    
    if not report['summary']['all_clear']:
        _prompt_for_fixes(report, scanner, inspector)

def _display_terminal_report(report, scanned):
    summary = report['summary']
    
    status_color = "green" if summary['all_clear'] else "red"
    status_text = "✅ ALL CLEAR! Ship be seaworthy!" if summary['all_clear'] else "❌ ISSUES FOUND! Ship needs repairs!"
    
    console.print(Panel.fit(
        f"[bold {status_color}]{status_text}[/bold {status_color}]\n\n"
        f"[cyan]Total Checks:[/cyan] {summary['total_checks']}  "
        f"[green]Passed:[/green] {summary['passed']}  "
        f"[red]Failed:[/red] {summary['failed']}",
        title="⚓ INSPECTION REPORT",
        border_style="cyan"
    ))
    
    console.print(f"\n[dim]📦 Workloads found: {len(scanned.get('workloads', []))}[/dim]")
    console.print(f"[dim]🔄 HPAs found: {len(scanned.get('hpas', []))}[/dim]")

    # ── CRITICAL ISSUES ───────────────────────────────────────────────
    if report['mandatory_failures']:
        console.print("\n[bold red]🚨 CRITICAL ISSUES (Fix 'em or walk the plank!)[/bold red]")
        table = Table(show_header=True, header_style="bold white on red", border_style="red", show_lines=True)
        table.add_column("Severity",  style="bold red",   no_wrap=True)
        table.add_column("Category",  style="cyan",       no_wrap=True)
        table.add_column("Resource",  style="bold white", no_wrap=False)
        table.add_column("Check",     style="yellow")
        table.add_column("Details",   style="white")
        for failure in report['mandatory_failures']:
            table.add_row(
                "🔴 MANDATORY",
                failure.get('category', '-'),
                f"{failure.get('namespace', 'default')}/{failure.get('resource_name', 'unknown')}",
                failure.get('check_name', ''),
                failure.get('details', 'Unknown issue')
            )
        console.print(table)

    # ── RECOMMENDED IMPROVEMENTS ──────────────────────────────────────
    if report.get('recommended_failures'):
        console.print("\n[bold yellow]⚠️  RECOMMENDED IMPROVEMENTS[/bold yellow]")
        table = Table(show_header=True, header_style="bold white on dark_orange", border_style="yellow", show_lines=True)
        table.add_column("Severity",  style="bold yellow", no_wrap=True)
        table.add_column("Category",  style="cyan",        no_wrap=True)
        table.add_column("Resource",  style="bold white",  no_wrap=False)
        table.add_column("Check",     style="yellow")
        table.add_column("Details",   style="white")
        for failure in report['recommended_failures']:
            table.add_row(
                "🟡 RECOMMENDED",
                failure.get('category', '-'),
                f"{failure.get('namespace', 'default')}/{failure.get('resource_name', 'unknown')}",
                failure.get('check_name', ''),
                failure.get('details', '')
            )
        console.print(table)

    if summary['all_clear']:
        console.print(report['pirate_summary'])

def _prompt_for_fixes(report, scanner, inspector):
    fixer = Fixer(inspector)
    
    # We must attach original_yaml to each result for fixing to work
    for result in report['all_results']:
        original_yaml = _get_original_yaml({"resource": result['resource_name']}, scanner)
        if original_yaml:
            result['original_yaml'] = original_yaml
            
    fix_plan = fixer.generate_fix_plan(report['mandatory_failures'] + report.get('recommended_failures', []))
    
    if fix_plan['total_fixes'] == 0:
        console.print("\n[bold yellow]No auto-fixes available for these issues.[/bold yellow]")
        return
        
    console.print(f"\n[bold yellow]🔧 I can fix {fix_plan['total_fixes']} issues, Captain![/bold yellow]")
    
    for fix in fix_plan['fixes']:
        console.print(f"  • {fix['resource']}: {fix['fix_description']}")
    
    console.print("\n[bold]What be yer orders, Captain?[/bold]")
    console.print("[1] [green]Aye! Fix everything![/green]")
    console.print("[2] [yellow]Just the critical issues[/yellow]")
    console.print("[3] [dim]Show me the fix details first[/dim]")
    console.print("[4] [red]Abandon ship! (Exit)[/red]")
    
    choice = click.prompt("Yer choice", type=int, default=4)
    
    if choice == 1:
        _apply_all_fixes(fix_plan, fixer, report, scanner)
    elif choice == 2:
        mandatory_plan = {
            "fixes": [f for f in fix_plan['fixes'] if any(mf['check_id'] == f['check_id'] for mf in report['mandatory_failures'])]
        }
        _apply_all_fixes(mandatory_plan, fixer, report, scanner)
    elif choice == 3:
        _show_fix_details(fix_plan, inspector)
        _prompt_for_fixes(report, scanner, inspector)
    else:
        console.print("[red]Aye, Captain. We'll let the ship sink then...[/red]")

def _apply_all_fixes(fix_plan, fixer, report, scanner):
    if not click.confirm(f"[bold red]Are ye SURE ye want me to modify {fix_plan['total_fixes']} files?[/bold red]"):
        console.print("[yellow]Wise choice, Captain. Measure twice, cut once.[/yellow]")
        return
    
    with Progress() as progress:
        task = progress.add_task("[cyan]Applying fixes...", total=len(fix_plan['fixes']))
        
        for fix in fix_plan['fixes']:
            progress.update(task, description=f"[cyan]Fixing {fix['resource']}...")
            
            original_result = _find_original_result(fix, report)
            original_yaml = _get_original_yaml(fix, scanner)
            
            if original_yaml and original_result:
                result = fixer.apply_fix(
                    original_result,
                    original_yaml,
                    original_yaml.get('_file_path', 'unknown')
                )
                
                if result['success']:
                    console.print(f"  [green]✓[/green] {fix['resource']}: {fix['fix_description']}")
                else:
                    console.print(f"  [red]✗[/red] {fix['resource']}: {result.get('error', 'Failed')}")
            
            progress.advance(task)
    
    console.print(f"\n[bold green]🏴☠️  Fixes applied, Captain! Run 'kubeinspector inspect' again to verify![/bold green]")

def _find_original_result(fix, report):
    for result in report['all_results']:
        if result['check_id'] == fix['check_id'] and result['resource_name'] == fix['resource']:
            return result
    return None

def _get_original_yaml(fix, scanner):
    for workload in scanner.resources:
        if workload['name'] == fix['resource']:
            workload['content']['_file_path'] = workload['file_path']
            return workload['content']
    for hpa in scanner.hpas:
        if hpa['name'] == fix['resource']:
            hpa['content']['_file_path'] = hpa['file_path']
            return hpa['content']
    return None

def _show_fix_details(fix_plan, inspector):
    mate = ResponseBuilder()
    for fix in fix_plan['fixes']:
        console.print(f"\n[bold]{fix['resource']}[/bold]")
        console.print(f"  Check: {fix['check']}")
        console.print(f"  Fix: {fix['fix_description']}")
        explanation = mate.get_explanation(fix['check_id'])
        console.print(f"  [dim]💡 {explanation}[/dim]")

@cli.command()
def checklist():
    """Show the Captain's Checklist"""
    inspector = Inspector()
    console.print("\n[bold cyan]📋 CAPTAIN'S SEAWORTHINESS CHECKLIST[/bold cyan]\n")
    for item in inspector.checklist['items']:
        severity_color = {"MANDATORY": "red", "RECOMMENDED": "yellow", "OPTIONAL": "dim"}.get(item['severity'], "white")
        console.print(f"[{severity_color}]■[/{severity_color}] [bold]{item['name']}[/bold]")
        console.print(f"  [{severity_color}]{item['severity']}[/{severity_color}]")
        console.print(f"  [dim]{item['description']}[/dim]\n")

@cli.command()
def version():
    """Show version"""
    console.print("[cyan]⚓ KubeInspector v1.0.0[/cyan]")
    console.print("[dim]Built with rum and determination 🏴☠️[/dim]")

if __name__ == '__main__':
    cli()
