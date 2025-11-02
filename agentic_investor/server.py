import pandas as pd
from mcp.server.fastmcp import FastMCP

from agentic_investor.services.tool_service import ToolService
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

mcp = FastMCP("Agentic-Investor", dependencies=["yfinance", "pandas", "pytrends"])

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
    mcp.run()
