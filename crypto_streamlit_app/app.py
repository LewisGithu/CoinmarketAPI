import streamlit as st
import requests
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Crypto Live Tracker | Githu Analytics",
    layout="wide"
)

st.title("Cryptocurrency Live Market Tracker")
st.caption("Live data pulled via CoinMarketCap API | Built by Lewis Githu")

API_KEY = st.secrets["CMC_API_KEY"].strip()

CURRENCY_SYMBOLS = {
    "USD": "$",
    "KES": "KES ",
    "EUR": "€",
    "GBP": "£"
}

@st.cache_data(ttl=300)
def fetch_crypto_data(currency="USD", limit=15):
    base_url = "https://pro-api.coinmarketcap.com"
    endpoint = "/v1/cryptocurrency/listings/latest"
    url = base_url + endpoint

    parameters = {
        "start": "1",
        "limit": str(limit),
        "convert": currency
    }
    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": API_KEY,
    }

    response = requests.get(url, headers=headers, params=parameters, timeout=15)
    response.raise_for_status()
    data = response.json()

    records = []
    for coin in data["data"]:
        quote = coin["quote"][currency]
        price_now = quote["price"]
        pct_1h = quote["percent_change_1h"] or 0.0
        pct_24h = quote["percent_change_24h"] or 0.0
        pct_7d = quote["percent_change_7d"] or 0.0

        price_1h_ago = price_now / (1 + pct_1h / 100)
        price_24h_ago = price_now / (1 + pct_24h / 100)
        price_7d_ago = price_now / (1 + pct_7d / 100)

        records.append({
            "Rank": coin["cmc_rank"],
            "Name": coin["name"],
            "Symbol": coin["symbol"],
            f"Price ({currency})": price_now,
            "1h Change (%)": pct_1h,
            "24h Change (%)": pct_24h,
            "7d Change (%)": pct_7d,
            f"Market Cap ({currency})": quote["market_cap"],
            "Price_7d": price_7d_ago,
            "Price_24h": price_24h_ago,
            "Price_1h": price_1h_ago,
        })
    return pd.DataFrame(records)

ctrl_col1, ctrl_col2 = st.columns([1, 3])
with ctrl_col1:
    currency = st.selectbox(
        "Display Currency:",
        options=["USD", "KES", "EUR", "GBP"],
        index=0
    )

sym = CURRENCY_SYMBOLS[currency]

try:
    df = fetch_crypto_data(currency=currency)
except Exception as e:
    st.error(f"Error details: {e}")
    st.stop()

with ctrl_col2:
    selected_coins = st.multiselect(
        "Select Cryptocurrencies to Compare:",
        options=df["Name"].tolist(),
        default=df["Name"].head(6).tolist()
    )

filtered_df = df[df["Name"].isin(selected_coins)]
price_col = f"Price ({currency})"
mcap_col = f"Market Cap ({currency})"

if not filtered_df.empty:
    # Top KPI Cards
    cols = st.columns(min(len(filtered_df), 3))
    for idx, (_, row) in enumerate(filtered_df.head(3).iterrows()):
        cols[idx].metric(
            label=f"#{row['Rank']} {row['Name']} ({row['Symbol']})",
            value=f"{sym}{row[price_col]:,.2f}",
            delta=f"{row['24h Change (%)']:.2f}% (24h)"
        )

    st.divider()

    # Two-Column Comparison Charts
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("7-Day Normalized Growth (%)")
        trend_rows = []
        for _, row in filtered_df.iterrows():
            base = row["Price_7d"] if row["Price_7d"] else 1
            points = [
                ("7d Ago", row["Price_7d"], 0.0),
                ("24h Ago", row["Price_24h"], ((row["Price_24h"] - base) / base) * 100),
                ("1h Ago", row["Price_1h"], ((row["Price_1h"] - base) / base) * 100),
                ("Now", row[price_col], ((row[price_col] - base) / base) * 100),
            ]
            for time_label, actual_price, pct_from_7d in points:
                trend_rows.append({
                    "Coin": row["Name"],
                    "Timeframe": time_label,
                    "Growth Since 7d Ago (%)": pct_from_7d,
                    "Actual Price": f"{sym}{actual_price:,.2f}"
                })

        trend_df = pd.DataFrame(trend_rows)
        line_fig = px.line(
            trend_df,
            x="Timeframe",
            y="Growth Since 7d Ago (%)",
            color="Coin",
            markers=True,
            hover_data={"Actual Price": True, "Growth Since 7d Ago (%)": ":.2f"}
        )
        line_fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        st.plotly_chart(line_fig, use_container_width=True)

    with chart_col2:
        st.subheader("Percentage Fluctuation Comparison")
        timeframe = st.radio(
            "Select Timeframe:",
            ["1h Change (%)", "24h Change (%)", "7d Change (%)"],
            horizontal=True
        )
        bar_fig = px.bar(
            filtered_df,
            x="Name",
            y=timeframe,
            color=timeframe,
            color_continuous_scale=["#ef4444", "#9ca3af", "#10b981"]
        )
        st.plotly_chart(bar_fig, use_container_width=True)

    st.divider()

    # Individual Chart for Each Cryptocurrency (3-Column Grid)
    st.subheader(f"Individual Price Charts ({currency})")
    coins_list = list(filtered_df.iterrows())
    
    for i in range(0, len(coins_list), 3):
        grid_cols = st.columns(3)
        for j in range(3):
            if i + j < len(coins_list):
                _, row = coins_list[i + j]
                coin_df = pd.DataFrame({
                    "Timeframe": ["7d Ago", "24h Ago", "1h Ago", "Now"],
                    f"Price ({currency})": [
                        row["Price_7d"],
                        row["Price_24h"],
                        row["Price_1h"],
                        row[price_col]
                    ]
                })

                line_color = "#10b981" if row["7d Change (%)"] >= 0 else "#ef4444"
                indiv_fig = px.line(
                    coin_df,
                    x="Timeframe",
                    y=f"Price ({currency})",
                    markers=True,
                    title=f"{row['Name']} ({row['Symbol']}) — {sym}{row[price_col]:,.2f}"
                )
                indiv_fig.update_traces(line_color=line_color, line_width=3)
                indiv_fig.update_layout(
                    height=280,
                    margin=dict(l=10, r=10, t=40, b=10),
                    xaxis_title="",
                    yaxis_title=""
                )
                grid_cols[j].plotly_chart(indiv_fig, use_container_width=True)

    st.divider()

    # Clean Market Data Table
    st.subheader(f"Live Market Data ({currency})")
    display_cols = ["Rank", "Name", "Symbol", price_col, "1h Change (%)", "24h Change (%)", "7d Change (%)", mcap_col]
    st.dataframe(
        filtered_df[display_cols].style.format({
            price_col: f"{sym}{{:,.2f}}",
            "1h Change (%)": "{:.2f}%",
            "24h Change (%)": "{:.2f}%",
            "7d Change (%)": "{:.2f}%",
            mcap_col: f"{sym}{{:,.0f}}"
        }),
        use_container_width=True,
        hide_index=True
    )
