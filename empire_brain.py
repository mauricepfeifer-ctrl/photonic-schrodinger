#!/usr/bin/env python3
import asyncio
import os
import sys
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

# Add local directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.product_scout import ProductScout
from modules.trend_hunter import TrendHunter
# Import Content Generator (Python part of Swarm)
# We can just call the script via subprocess or import if we refactor. 
# For now, subprocess is safer for the Go part.

console = Console()

class EmpireBrain:
    def __init__(self):
        self.scout = ProductScout()
        self.hunter = TrendHunter()
        self.icloud_path = os.path.expanduser("~/Library/Mobile Documents/com~apple~CloudDocs/AI_Empire_Swarm")

    def clear(self):
        os.system('clear')

    def display_header(self):
        self.clear()
        console.print(Panel.fit("[bold gold1]👑 EMPIRE BRAIN - CENTRAL COMMAND[/bold gold1]", subtitle="Maurice's AI Empire"))

    async def run_content_swarm(self):
        console.print("[bold blue]🚀 Launching 10k Agent Swarm (Go Ideas + Kimi Content)...[/bold blue]")
        
        # 1. Run Go Swarm
        console.print("   [1/3] Mining Ideas (Go)...")
        if os.system("go run production_swarm_main.go") != 0:
            console.print("[red]❌ Go Swarm Failed[/red]")
            return

        # 2. Run Python Generator
        console.print("   [2/3] Generating Scripts (Kimi AI)...")
        if os.system("python3 production_content_generator.py") != 0:
            console.print("[red]❌ Content Gen Failed[/red]")
            return

        # 3. Sync
        console.print("   [3/3] Syncing to iPhone...")
        os.system("./sync_to_icloud.sh > /dev/null 2>&1")
        
        console.print("[green]✅ Content Swarm Cycle Complete![/green]")
        console.print(f"   [dim]Check {self.icloud_path}[/dim]")
        header = input("\nPress user to continue...")

    async def run_market_scan(self):
        console.print("[bold magenta]📈 Scanning Global Markets...[/bold magenta]")
        
        analysis = await self.hunter.analyze_market()
        
        table = Table(title="Top Emerging Trends")
        table.add_column("Topic", style="cyan")
        table.add_column("Momentum", style="magenta")
        table.add_column("Status", style="green")

        for t in analysis['all_trends']:
            table.add_row(t['topic'], str(t['momentum']), t['status'])
        
        console.print(table)
        console.print(f"\n[bold]💡 BRAIN RECOMMENDATION:[/bold] {analysis['recommendation']}")
        
        # Ask to monetize
        if Prompt.ask("\nScout products for this trend?", choices=["y", "n"]) == "y":
            await self.scout_products(analysis['top_trend']['topic'])
        else:
            input("\nPress enter to continue...")

    async def scout_products(self, niche=None):
        if not niche:
            niche = Prompt.ask("Enter Niche to Scout")
        
        console.print(f"[bold green]💰 Scouting Products for: {niche}[/bold green]")
        opportunities = await self.scout.scan_opportunities(niche)
        
        table = Table(title=f"High-Ticket Opportunities: {niche}")
        table.add_column("Product", style="white")
        table.add_column("Type", style="cyan")
        table.add_column("Commission", style="green")
        table.add_column("Action", style="bold red")

        for op in opportunities:
            table.add_row(op['name'], op['type'], op['commission'], f"Global Link") # Simulating link
        
        console.print(table)
        
        # Save to file
        with open("swarm_output/product_opportunities.json", "w") as f:
            json.dump(opportunities, f, indent=2)
        
        console.print("\n[dim]Saved to swarm_output/product_opportunities.json[/dim]")
        input("\nPress enter to continue...")

    async def main_menu(self):
        while True:
            self.display_header()
            console.print("[1] 🐝 Launch Content Swarm (10k Agents)")
            console.print("[2] 📈 Analyze Market Trends")
            console.print("[3] 💰 Scout Affiliate Products")
            console.print("[4] ☁️  Force Sync to iCloud")
            console.print("[q] Quit")
            
            choice = Prompt.ask("\nSelect Directive", choices=["1", "2", "3", "4", "q"], default="1")
            
            if choice == "1":
                await self.run_content_swarm()
            elif choice == "2":
                await self.run_market_scan()
            elif choice == "3":
                await self.scout_products()
            elif choice == "4":
                os.system("./sync_to_icloud.sh")
                input("Sync complete. Press enter...")
            elif choice == "q":
                console.print("👋 Empire Brain Offline.")
                break

if __name__ == "__main__":
    brain = EmpireBrain()
    try:
        asyncio.run(brain.main_menu())
    except KeyboardInterrupt:
        print("\nExiting...")
