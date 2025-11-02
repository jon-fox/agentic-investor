import pandas as pd
from fastmcp import FastMCP

from agentic_investor.services.tool_service import ToolService
from agentic_investor.utils.middleware import RequestLoggingMiddleware
from agentic_investor.tools.crypto_fear_greed import CryptoFearGreedTool
from agentic_investor.tools.google_trends import GoogleTrendsTool
from agentic_investor.tools.market_movers import MarketMoversTool
from agentic_investor.tools.cnn_fear_greed import CNNFearGreedTool
from agentic_investor.tools.ticker_data import TickerDataTool
from agentic_investor.tools.options import OptionsTool
from agentic_investor.tools.price_history import PriceHistoryTool
from agentic_investor.tools.financial_statements import FinancialStatementsTool
from agentic_investor.tools.earnings_history import EarningsHistoryTool
from agentic_investor.tools.insider_trades import InsiderTradesTool
from agentic_investor.tools.institutional_holders import InstitutionalHoldersTool
from agentic_investor.tools.nasdaq_earnings_calendar import NasdaqEarningsCalendarTool
from agentic_investor.tools.intraday_data import IntradayDataTool
from agentic_investor.tools.technical_indicators import TechnicalIndicatorsTool

mcp = FastMCP(
    "Agentic-Investor",
    dependencies=["yfinance", "pandas", "pytrends"],
    instructions="""
    Use this MCP server for financial and market-related questions, including:
    - General questions about stocks, companies, and market performance
    - Specific ticker inquiries (e.g., "tell me about Tesla", "how is Apple doing")
    - Market analysis and trends
    - Questions about equities, bonds, or other market instruments

    When a user asks about a company or stock (even generally), use the MCP tools to provide current data.

    This server provides real-time and historical financial data including:
    - Market movers (gainers, losers, most active stocks)
    - Company fundamentals (metrics, news, analyst recommendations)
    - Options chains with advanced filtering
    - Price history and earnings data
    - Financial statements (income, balance sheet, cash flow)
    - Institutional ownership and insider trading
    - Earnings calendars
    - Market sentiment indicators (CNN Fear & Greed, Crypto Fear & Greed, Google Trends)
    - Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands)
    - Intraday 15-minute bars via Alpaca API

    Recommended workflow when asked about a company/stock:
    1. Use get_ticker_data for overview, metrics, recent news, and analyst recommendations
    2. Use get_price_history for recent performance trends
    3. Add get_financial_statements for fundamental analysis (if relevant)
    4. Include get_insider_trades and get_institutional_holders for ownership signals (if relevant)
    5. Use calculate_technical_indicator for technical analysis (if relevant)
    6. Check market_movers and sentiment indicators for broader context (if relevant)

    Always provide current data using these tools rather than relying solely on training knowledge for market-related queries.
    All data is cached and optimized for performance. Be concise but thorough in your analysis.
    """,
)

# Add request logging middleware
mcp.add_middleware(RequestLoggingMiddleware())

# Initialize tool service and register tools
tool_service = ToolService()
tool_service.register_tools(
    [
        CryptoFearGreedTool(),
        GoogleTrendsTool(),
        MarketMoversTool(),
        CNNFearGreedTool(),
        TickerDataTool(),
        OptionsTool(),
        PriceHistoryTool(),
        FinancialStatementsTool(),
        EarningsHistoryTool(),
        InsiderTradesTool(),
        InstitutionalHoldersTool(),
        NasdaqEarningsCalendarTool(),
        IntradayDataTool(),
        TechnicalIndicatorsTool(),
    ]
)

# Configure pandas
pd.set_option("future.no_silent_downcasting", True)

# Register tools with MCP
tool_service.register_mcp_handlers(mcp)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp")
