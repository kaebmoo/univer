#!/usr/bin/env python3
"""
Main entry point for Univer Report Generator
Can run both CLI and Web modes
"""
import sys
import argparse


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Univer Report Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  cli       Generate report via command-line
  web       Start web server

Examples:
  # Start web server
  python main.py web

  # Generate report via CLI
  python main.py cli --data-dir ../data --output-dir ./output

  # Show CLI help
  python main.py cli --help
        """
    )

    parser.add_argument(
        'mode',
        choices=['cli', 'web'],
        help='Operation mode: cli or web'
    )

    # Parse only the mode argument
    args, remaining = parser.parse_known_args()

    if args.mode == 'cli':
        # Pass remaining args to CLI
        sys.argv = ['cli.py'] + remaining
        from src.cli.cli import ReportCLI
        ReportCLI.main()

    elif args.mode == 'web':
        # Start web server
        import uvicorn
        from config.settings import settings

        print("=" * 60)
        print("Starting Univer Report Generator Web Server")
        print("=" * 60)
        print(f"Host: {settings.web_host}")
        print(f"Port: {settings.web_port}")
        print(f"Environment: {settings.app_env}")
        print(f"API Docs: http://localhost:{settings.web_port}/api/docs")
        print("=" * 60)

        uvicorn.run(
            "src.web.main:app",
            host=settings.web_host,
            port=settings.web_port,
            reload=settings.debug
        )


if __name__ == '__main__':
    main()
