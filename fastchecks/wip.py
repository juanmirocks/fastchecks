from datetime import datetime

from apscheduler.schedulers.async_ import AsyncScheduler
from apscheduler.triggers.interval import IntervalTrigger

import asyncio


def tick(name: str):
    print(f"Tick! The time is {datetime.now()} and the name is {name}")


async def main():
    async with AsyncScheduler() as scheduler:
        await scheduler.add_schedule(tick, trigger=IntervalTrigger(seconds=3), id="john", args=["John Doe"])
        await scheduler.add_schedule(tick, trigger=IntervalTrigger(seconds=2), id="peter", args=["Peter Parker"])

        await scheduler.run_until_stopped()


try:
    asyncio.run(main())
except (KeyboardInterrupt, SystemExit):
    pass
