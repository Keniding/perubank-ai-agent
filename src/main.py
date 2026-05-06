"""
PeruBank AI Agent - Entry Point
Multi-Agent Banking System powered by AMD Instinct MI300X
"""

import asyncio
from datetime import datetime

from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel

from src.agents.orchestrator import build_banking_graph
from src.config.settings import settings

console = Console()


def display_banner():
    banner = """
[bold cyan]ðŸ¦ PeruBank AI Agent[/bold cyan]
[dim]Multi-Agent Banking System | AMD MI300X + LangGraph[/dim]
[dim]AMD Developer Hackathon 2026 | Team LEAD[/dim]
    """
    console.print(Panel(banner, border_style="cyan"))
    console.print(f"[dim]ðŸ“… {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]")
    console.print(f"[dim]ðŸ–¥ï¸  Model: {settings.VLLM_MODEL}[/dim]")
    console.print(f"[dim]ðŸ”— Endpoint: {settings.VLLM_BASE_URL}[/dim]\n")


async def run_interactive():
    """Run the agent system in interactive mode."""
    display_banner()

    # Build the graph
    graph = build_banking_graph()
    console.print("[green]âœ… Agent graph compiled successfully[/green]\n")

    while True:
        try:
            user_input = console.input("[bold yellow]ðŸ‘¤ Cliente:[/bold yellow] ")

            if user_input.lower() in ["exit", "quit", "salir"]:
                console.print("\n[cyan]ðŸ‘‹ Â¡Hasta luego! Gracias por usar PeruBank AI.[/cyan]")
                break

            if not user_input.strip():
                continue

            # Execute the graph
            with console.status("[bold green]ðŸ¤– Procesando...[/bold green]"):
                result = await graph.ainvoke(
                    {
                        "messages": [HumanMessage(content=user_input)],
                        "customer_id": "CLI-2026-DEMO",
                        "intent": "",
                        "risk_score": 0.0,
                        "compliance_check": {},
                        "recommendation": "",
                        "current_agent": "",
                    }
                )

            # Display response
            console.print()
            for msg in result["messages"]:
                if hasattr(msg, "content") and msg.content.startswith("["):
                    console.print(f"[bold green]ðŸ¤– {msg.content}[/bold green]")
            console.print()

        except KeyboardInterrupt:
            console.print("\n[cyan]ðŸ‘‹ SesiÃ³n terminada.[/cyan]")
            break


def main():
    """Main entry point."""
    asyncio.run(run_interactive())


if __name__ == "__main__":
    main()
