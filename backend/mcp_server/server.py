#!/usr/bin/env python3
"""
MCP Server for Univer Report System

This server provides AI agents (like Claude Desktop) access to P&L report data
through the Model Context Protocol (MCP).

Available Tools:
- get_report_data: Retrieve P&L report with filtering
- get_filter_options: Get available years, business groups, and services
- calculate_metrics: Calculate financial metrics (EBIT, EBITDA, margins)
"""

import sys
import json
import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.services.data_loader import data_loader
from app.services.report_calculator import report_calculator

# Initialize MCP server
app = Server("univer-report-server")


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List all available tools for the MCP server."""
    return [
        Tool(
            name="get_report_data",
            description="Retrieve P&L (Profit & Loss) report data with optional filtering by year, months, and business groups. Returns revenue, costs, and profit metrics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "year": {
                        "type": "integer",
                        "description": "The year for the report (e.g., 2024)",
                        "minimum": 2020,
                        "maximum": 2030,
                    },
                    "months": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1, "maximum": 12},
                        "description": "List of months to include (1-12). Example: [1,2,3] for Q1",
                        "minItems": 1,
                        "maxItems": 12,
                    },
                    "business_groups": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of business groups to filter. If not provided, all groups are included.",
                    },
                },
                "required": ["year", "months"],
            },
        ),
        Tool(
            name="get_filter_options",
            description="Get available filter options including years, business groups, and services from the data.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
            name="calculate_metrics",
            description="Calculate financial metrics (EBIT, EBITDA, profit margins, common size percentages) based on provided revenue and cost data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "revenue": {
                        "type": "number",
                        "description": "Total revenue amount",
                    },
                    "cost_of_service": {
                        "type": "number",
                        "description": "Cost of service (direct costs)",
                    },
                    "selling_expenses": {
                        "type": "number",
                        "description": "Selling expenses",
                    },
                    "admin_expenses": {
                        "type": "number",
                        "description": "Administrative expenses",
                    },
                    "depreciation": {
                        "type": "number",
                        "description": "Depreciation amount",
                        "default": 0,
                    },
                    "amortization": {
                        "type": "number",
                        "description": "Amortization amount",
                        "default": 0,
                    },
                },
                "required": ["revenue", "cost_of_service", "selling_expenses", "admin_expenses"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls from the MCP client."""

    try:
        if name == "get_report_data":
            # Extract parameters
            year = arguments["year"]
            months = arguments["months"]
            business_groups = arguments.get("business_groups")

            # Generate report using report_calculator
            report_data = report_calculator.generate_full_report(
                year=year,
                months=months,
                business_groups=business_groups
            )

            # Format response
            result = {
                "year": year,
                "months": months,
                "business_groups": business_groups if business_groups else "All",
                "data": report_data,
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "get_filter_options":
            # Get available filter options
            filter_options = data_loader.get_available_filters()

            result = {
                "years": filter_options.years,
                "business_groups": filter_options.business_groups,
                "services": filter_options.services,
            }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, ensure_ascii=False)
                )
            ]

        elif name == "calculate_metrics":
            # Extract financial data
            revenue = arguments["revenue"]
            cost_of_service = arguments["cost_of_service"]
            selling_expenses = arguments["selling_expenses"]
            admin_expenses = arguments["admin_expenses"]
            depreciation = arguments.get("depreciation", 0)
            amortization = arguments.get("amortization", 0)

            # Calculate metrics
            metrics = report_calculator.calculate_profit_metrics(
                revenue=revenue,
                cost_of_service=cost_of_service,
                selling_expenses=selling_expenses,
                admin_expenses=admin_expenses,
                depreciation=depreciation,
                amortization=amortization
            )

            # Add common size percentages
            if revenue > 0:
                metrics["common_size"] = {
                    "cost_of_service_pct": (cost_of_service / revenue) * 100,
                    "selling_expenses_pct": (selling_expenses / revenue) * 100,
                    "admin_expenses_pct": (admin_expenses / revenue) * 100,
                    "ebit_margin": metrics["ebit_margin"],
                    "ebitda_margin": metrics["ebitda_margin"],
                }

            return [
                TextContent(
                    type="text",
                    text=json.dumps(metrics, indent=2, ensure_ascii=False)
                )
            ]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except Exception as e:
        # Return error as text content
        error_response = {
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [
            TextContent(
                type="text",
                text=json.dumps(error_response, indent=2, ensure_ascii=False)
            )
        ]


async def main():
    """Main entry point for the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
