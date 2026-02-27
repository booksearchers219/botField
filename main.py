#!/usr/bin/env python3

import argparse
import random
import sys

from orchestrator import Orchestrator
from agents import create_default_agents
from database import init_database, DB_PATH
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="botField v0.1 - Deterministic agent simulation"
    )

    parser.add_argument(
        "--steps",
        type=int,
        required=True,
        help="Number of simulation ticks to run"
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic runs (default: 42)"
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing database before running simulation"
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.steps <= 0:
        print("Error: --steps must be greater than 0")
        sys.exit(1)

    # Deterministic seed
    random.seed(args.seed)

    print(f"\n=== botField v0.1 ===")
    print(f"Steps: {args.steps}")
    print(f"Seed:  {args.seed}\n")

    
    # Optional reset
    if args.reset:
        if Path(DB_PATH).exists():
            print("Resetting database...")
            Path(DB_PATH).unlink()

    # Initialize database
    db = init_database()

    # Create agents
    agents = create_default_agents(db)

    # Create orchestrator
    orchestrator = Orchestrator(agents=agents, db=db)

    # Run simulation
    orchestrator.run(steps=args.steps)

    print("\nSimulation complete.\n")


if __name__ == "__main__":
    main()



