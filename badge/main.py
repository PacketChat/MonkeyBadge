from library.monkeybadge import MonkeyBadge
import uasyncio as asyncio

async def main():
    badge = MonkeyBadge()
    await badge.run()

# Run the main function
asyncio.run(main())
