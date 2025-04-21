# Import necessary libraries to build our pricer
import math   # Standard mathematical functions
import streamlit as st # Create an interactive web interface
import matplotlib.pyplot as plt # Plotting graphs
import pandas as pd # Data table manipulation

# Standard normal cumulative distribution function (CDF)

def N(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# Standard normal probability density function (PDF)

def phi(x):
    return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x**2)

# Calculation of d1 in the Black-Scholes formula

def d1(S, K, T, r, sigma):
    return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))

# Calculation of d2 based on d1

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

# Calculation of the price of a European option (Call or Put)

def black_scholes_price(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)
    if option_type == 'call':
        return S * N(d_1) - K * math.exp(-r * T) * N(d_2)
    else:
        return K * math.exp(-r * T) * N(-d_2) - S * N(-d_1)

# Functions to calculate the Greeks

# Delta: Sensitivity of the option price to the underlying asset price

def delta(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    return N(d_1) if option_type == 'call' else N(d_1) - 1

# Gamma: Sensitivity of Delta with respect to the underlying asset price

def gamma(S, K, T, r, sigma):
    d_1 = d1(S, K, T, r, sigma)
    return phi(d_1) / (S * sigma * math.sqrt(T))

# Vega: Sensitivity of the option price to volatility

def vega(S, K, T, r, sigma):
    d_1 = d1(S, K, T, r, sigma)
    return S * phi(d_1) * math.sqrt(T)

# Theta: Sensitivity of the option price to time (time decay)

def theta(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)
    first_term = - (S * phi(d_1) * sigma) / (2 * math.sqrt(T))
    if option_type == 'call':
        return first_term - r * K * math.exp(-r * T) * N(d_2)
    else:
        return first_term + r * K * math.exp(-r * T) * N(-d_2)

# Rho: Sensitivity of the option price to the interest rate

def rho(S, K, T, r, sigma, option_type):
    d_2 = d2(S, K, T, r, sigma)
    if option_type == 'call':
        return K * T * math.exp(-r * T) * N(d_2)
    else:
        return -K * T * math.exp(-r * T) * N(-d_2)

# User interface with Streamlit:

# Streamlit page configuration
st.set_page_config(page_title="Pricer Black-Scholes+", layout="wide")
st.title("Pricer Black-Scholes")

# Sidebar: input of parameters

with st.sidebar:
    st.header("Parameters")
    S = st.slider("Spot Price (S)", 20, 1000, 100) # Price between 20 and 1000
    K = st.slider("Strike Price (K)", 20, 1000, 100)
    T = st.slider("Maturity (days)", 7, 730, 365) / 365 #Maturity from de 7 days to 2 years
    r = st.slider("Risk-free rate (r)", 0.0, 0.2, 0.05)
    sigma = st.slider("Volatility (σ)", 0.01, 1.0, 0.2)
    option_type = st.radio("Option type", ['call', 'put'])

# Create tabs: Price & Greeks, Charts, Export

tabs = st.tabs(["Price & Greeks", "Price Chart", "Greeks vs T", "Export results"])
S_range = list(range(50, 151))
T_range = [i/365 for i in range(30, 366, 5)]

# Tab 1: Display of the option price and the Greeks

with tabs[0]:
    st.subheader("Option price")
    price = black_scholes_price(S, K, T, r, sigma, option_type)
    st.write(f"*{option_type.capitalize()} = {price:.4f}*")
    st.subheader("Greeks")
    st.write(f"*Delta* : {delta(S, K, T, r, sigma, option_type):.4f}")
    st.write(f"*Gamma* : {gamma(S, K, T, r, sigma):.4f}")
    st.write(f"*Vega* : {vega(S, K, T, r, sigma):.4f}")
    st.write(f"*Theta* : {theta(S, K, T, r, sigma, option_type):.4f}")
    st.write(f"*Rho* : {rho(S, K, T, r, sigma, option_type):.4f}")

# Tab 2: Option price graph as a function of S

with tabs[1]:
    prices = [black_scholes_price(s, K, T, r, sigma, option_type) for s in S_range]
    fig, ax = plt.subplots()
    ax.plot(S_range, prices)
    ax.set_title("Option price as a function of S")
    ax.set_xlabel("Spot price (S)")
    ax.set_ylabel("Option price")
    ax.grid(True)
    st.pyplot(fig)

# Tab 3: Evolution of a Greek with respect to maturity

with tabs[2]:
    greek = st.selectbox("Choose a Greek", ["Delta", "Gamma", "Vega", "Theta", "Rho"])
    greek_values = []
    for t in T_range:
        if greek == "Delta":
            greek_values.append(delta(S, K, t, r, sigma, option_type))
        elif greek == "Gamma":
            greek_values.append(gamma(S, K, t, r, sigma))
        elif greek == "Vega":
            greek_values.append(vega(S, K, t, r, sigma))
        elif greek == "Theta":
            greek_values.append(theta(S, K, t, r, sigma, option_type))
        elif greek == "Rho":
            greek_values.append(rho(S, K, t, r, sigma, option_type))
    fig2, ax2 = plt.subplots()
    ax2.plot([t*365 for t in T_range], greek_values)
    ax2.set_title(f"{greek} as a function of time (T)")
    ax2.set_xlabel("Maturity (days)")
    ax2.set_ylabel(greek)
    ax2.grid(True)
    st.pyplot(fig2)

# Tab 4: Export results to CSV

with tabs[3]:
    st.subheader("Export results")
    results = {
        "Price": [black_scholes_price(S, K, T, r, sigma, option_type)],
        "Delta": [delta(S, K, T, r, sigma, option_type)],
        "Gamma": [gamma(S, K, T, r, sigma)],
        "Vega": [vega(S, K, T, r, sigma)],
        "Theta": [theta(S, K, T, r, sigma, option_type)],
        "Rho": [rho(S, K, T, r, sigma, option_type)]
    }
    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download as CSV", csv, "greeks_result.csv", "text/csv")
