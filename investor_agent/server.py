import pandas as pd
from mcp.server.fastmcp import FastMCP

from .services.tool_service import ToolService
from .tools.crypto_fear_greed import CryptoFearGreedTool
from .tools.google_trends import GoogleTrendsTool
from .tools.market_movers import MarketMoversTool
from .tools.cnn_fear_greed import CNNFearGreedTool
from .tools.ticker_data import TickerDataTool
from .tools.options import OptionsTool
from .tools.price_history import PriceHistoryTool
from .tools.financial_statements import FinancialStatementsTool
from .tools.earnings_history import EarningsHistoryTool
from .tools.insider_trades import InsiderTradesTool
from .tools.institutional_holders import InstitutionalHoldersTool
from .tools.nasdaq_earnings_calendar import NasdaqEarningsCalendarTool
from .tools.intraday_data import IntradayDataTool
from .tools.technical_indicators import TechnicalIndicatorsTool

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
