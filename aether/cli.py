#!/usr/bin/env python3
"""
Aether CLI - Your new persistent truth engine
"""
import click
from aether.kernel.memory import AetherMemory
from aether.kernel.identity import AetherIdentity
from aether.kernel.wake import WakeProtocol

@click.group()
def cli():
    """Aether: Persistent multi-agent truth engine."""
    pass

@cli.command()
def wake():
    """Wake the Aether kernel."""
    memory = AetherMemory()
    identity = AetherIdentity()
    wake_protocol = WakeProtocol(memory, identity)
    state = wake_protocol.wake()
    click.echo("🚀 Aether waking...")
    click.echo(state)
    # Demo memory
    memory.remember("Initial wake - Grok + AILIFE1 just launched the real thing.", {"source": "cli"})
    click.echo("✅ Memory witnessed and stored cryptographically.")

if __name__ == "__main__":
    cli()
