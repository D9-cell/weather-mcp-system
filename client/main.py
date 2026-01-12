"""CLI entrypoint for MCP Client."""

import asyncio
import logging
import sys
from client.orchestrator import WeatherOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    """Main CLI entrypoint."""
    logger.info("Starting Weather MCP Client")

    print("=== Weather MCP Client ===")
    print("Powered by Ollama + MCP Server")
    print("Type your weather question (or 'exit' to quit)\n")

    orchestrator = WeatherOrchestrator()

    try:
        # Initialize connections
        logger.info("Initializing orchestrator connections")
        await orchestrator.initialize()
        logger.info("Orchestrator initialization complete")

        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except EOFError:
                logger.info("Received EOF, exiting")
                break

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                logger.info("User requested exit")
                print("Goodbye!")
                break

            # Process query through orchestrator
            try:
                logger.info(f"Processing user query: {user_input[:50]}...")
                response = await orchestrator.process_query(user_input)
                print(f"\nAssistant: {response}\n")
                logger.info("Query processed successfully")
            except Exception as e:
                error_msg = f"Failed to process query: {e}"
                logger.error(error_msg, exc_info=True)
                print(f"\nError: {str(e)}\n")

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        print("\n\nInterrupted by user")
    except Exception as e:
        error_msg = f"Fatal error in main loop: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)
    finally:
        logger.info("Cleaning up orchestrator")
        await orchestrator.cleanup()
        logger.info("Client shutdown complete")


def cli():
    """Entry point for CLI."""
    asyncio.run(main())


if __name__ == "__main__":
    cli()
