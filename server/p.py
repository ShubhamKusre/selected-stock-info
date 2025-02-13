from flask import Flask, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allows frontend requests

# List of top 10 most traded stocks
TOP_10_STOCKS = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN", "GOOGL", "META", "BRK-B", "NFLX", "AMD"]

def get_stock_info(ticker):
    """Fetch stock price, previous close, and percentage change."""
    stock = yf.Ticker(ticker)

    try:
        # Fetch real-time stock data
        stock_data = stock.history(period="1d", interval="1m", prepost=True)  

        if stock_data.empty:
            return {"Stock": ticker, "Error": "No data available"}

        latest_price = stock_data['Close'].iloc[-1]  
        previous_price = stock_data['Close'].iloc[-2] if len(stock_data) > 1 else latest_price  

        # Calculate percentage change
        change_percent = ((latest_price - previous_price) / previous_price) * 100 if previous_price else 0

        return {
            "Stock": ticker,
            "Latest Price": f"${latest_price:.2f}",
            "Change": f"{change_percent:.2f}%",
            "Previous Close": f"${previous_price:.2f}"
        }

    except Exception as e:
        print(f"Error fetching stock data for {ticker}: {str(e)}")
        return {"Stock": ticker, "Error": str(e)}


@app.route('/stocks/top10', methods=['GET'])
def get_top_10_stocks():
    """Fetch real-time stock data for the top 10 most traded stocks."""
    stock_data = [get_stock_info(stock) for stock in TOP_10_STOCKS]
    return jsonify(stock_data)


@app.route('/stock/<ticker>', methods=['GET'])
def get_stock_by_ticker(ticker):
    """Fetch real-time stock data for a single stock by ticker."""
    stock_info = get_stock_info(ticker.upper())  
    return jsonify(stock_info)


@app.route('/stock/<ticker>/chart', methods=['GET'])
def get_stock_chart(ticker):
    """Fetch stock price history for the past month."""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period="1mo", interval="1d")  # Fetch 1 month of data with daily intervals

        if hist.empty:
            return jsonify({"error": "No chart data available"}), 404

        chart_data = [
            {"time": index.strftime("%m-%d"), "price": round(row["Close"], 2)}
            for index, row in hist.iterrows()
        ]

        return jsonify({"chart": chart_data})

    except Exception as e:
        print(f"Error fetching chart data for {ticker}: {str(e)}")
        return jsonify({"error": "Failed to fetch chart data"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=5000)
