"""Quick test to verify TickTick API connection."""

import asyncio
import sys
import os

# Fix Windows encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from ticktick_mcp.api import TickTickAPI


async def test():
    print("Testing TickTick API connection...\n")

    try:
        api = TickTickAPI()

        # Test 1: Get projects
        print("1. Getting projects...")
        projects = await api.get_projects()
        print(f"   Found {len(projects)} project(s):")
        for p in projects:
            name = p.get('name', 'Untitled')
            print(f"   - {name} (ID: {p.get('id')})")

        # Test 2: Get all tasks
        print("\n2. Getting all tasks...")
        tasks = await api.get_all_tasks()
        print(f"   Found {len(tasks)} task(s)")

        if tasks:
            print("\n   First 5 tasks:")
            for t in tasks[:5]:
                priority_map = {0: "[ ]", 1: "[L]", 3: "[M]", 5: "[H]"}
                priority = priority_map.get(t.get("priority", 0), "[ ]")
                title = t.get('title', 'Untitled')
                print(f"   {priority} {title}")

        print("\n[OK] API connection successful!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test())
