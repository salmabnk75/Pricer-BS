# Importation des bibliothèques nécessaires pour coder notre pricer
import math   # Fonctions mathématiques standards
import streamlit as st # Création d'une interface web interactive
import matplotlib.pyplot as plt # Tracé de graphiques
import pandas as pd # Manipulation de tableaux de données

# Fonction de répartition de la loi normale standard (CDF)

def N(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

# Fonction de densité de la loi normale standard (PDF)

def phi(x):
    return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x**2)

# Calcul de d1 dans la formule de Black-Scholes

def d1(S, K, T, r, sigma):
    return (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))

# Calcul de d2 à partir de d1

def d2(S, K, T, r, sigma):
    return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)

# Calcul du prix d'une option européenne (Call ou Put)

def black_scholes_price(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)
    if option_type == 'call':
        return S * N(d_1) - K * math.exp(-r * T) * N(d_2)
    else:
        return K * math.exp(-r * T) * N(-d_2) - S * N(-d_1)

# Fonctions de calcul des Greeks 

# Delta : Sensibilité du prix de l’option au prix du sous-jacent

def delta(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    return N(d_1) if option_type == 'call' else N(d_1) - 1

# Gamma : Sensibilité du Delta par rapport au prix du sous-jacent

def gamma(S, K, T, r, sigma):
    d_1 = d1(S, K, T, r, sigma)
    return phi(d_1) / (S * sigma * math.sqrt(T))

# Vega : Sensibilité du prix de l’option à la volatilité

def vega(S, K, T, r, sigma):
    d_1 = d1(S, K, T, r, sigma)
    return S * phi(d_1) * math.sqrt(T)

# Theta : Sensibilité du prix de l’option au temps (perte de valeur dans le temps)

def theta(S, K, T, r, sigma, option_type):
    d_1 = d1(S, K, T, r, sigma)
    d_2 = d2(S, K, T, r, sigma)
    first_term = - (S * phi(d_1) * sigma) / (2 * math.sqrt(T))
    if option_type == 'call':
        return first_term - r * K * math.exp(-r * T) * N(d_2)
    else:
        return first_term + r * K * math.exp(-r * T) * N(-d_2)

# Rho : # Sensibilité du prix de l’option au taux d’intérêt

def rho(S, K, T, r, sigma, option_type):
    d_2 = d2(S, K, T, r, sigma)
    if option_type == 'call':
        return K * T * math.exp(-r * T) * N(d_2)
    else:
        return -K * T * math.exp(-r * T) * N(-d_2)

# Interface utilisateur avec Streamlit :

# Configuration de la page Streamlit
st.set_page_config(page_title="Pricer Black-Scholes+", layout="wide")
st.title("Pricer Black-Scholes")

# Barre latérale : saisie des paramètres

with st.sidebar:
    st.header("Paramètres")
    S = st.slider("Prix spot (S)", 20, 1000, 100) #Prix entre 20 et 1000
    K = st.slider("Prix d'exercice (K)", 20, 1000, 100)
    T = st.slider("Maturité (jours)", 7, 730, 365) / 365 #Maturité de 7 jours à 2 ans
    r = st.slider("Taux sans risque (r)", 0.0, 0.2, 0.05)
    sigma = st.slider("Volatilité (σ)", 0.01, 1.0, 0.2)
    option_type = st.radio("Type d’option", ['call', 'put'])

# Création des onglets : Prix & Greeks, Graphiques, Export

tabs = st.tabs(["Prix & Greeks", "Graphique Prix", "Greeks vs T", "Exporter les résultats"])
S_range = list(range(50, 151))
T_range = [i/365 for i in range(30, 366, 5)]

# Onglet 1 : Affichage du prix de l’option et des Greeks

with tabs[0]:
    st.subheader("Prix de l’option")
    price = black_scholes_price(S, K, T, r, sigma, option_type)
    st.write(f"*{option_type.capitalize()} = {price:.4f}*")
    st.subheader("Greeks")
    st.write(f"*Delta* : {delta(S, K, T, r, sigma, option_type):.4f}")
    st.write(f"*Gamma* : {gamma(S, K, T, r, sigma):.4f}")
    st.write(f"*Vega* : {vega(S, K, T, r, sigma):.4f}")
    st.write(f"*Theta* : {theta(S, K, T, r, sigma, option_type):.4f}")
    st.write(f"*Rho* : {rho(S, K, T, r, sigma, option_type):.4f}")

# Onglet 2 : Graphique du prix en fonction de S

with tabs[1]:
    prices = [black_scholes_price(s, K, T, r, sigma, option_type) for s in S_range]
    fig, ax = plt.subplots()
    ax.plot(S_range, prices)
    ax.set_title("Prix de l'option en fonction de S")
    ax.set_xlabel("Prix spot (S)")
    ax.set_ylabel("Prix de l’option")
    ax.grid(True)
    st.pyplot(fig)

# Onglet 3 : Évolution d’un Greek en fonction de la maturité

with tabs[2]:
    greek = st.selectbox("Choisir un Greek", ["Delta", "Gamma", "Vega", "Theta", "Rho"])
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
    ax2.set_title(f"{greek} en fonction du temps (T)")
    ax2.set_xlabel("Maturité (jours)")
    ax2.set_ylabel(greek)
    ax2.grid(True)
    st.pyplot(fig2)

# Onglet 4 : Export des résultats en CSV

with tabs[3]:
    st.subheader("Export des résultats")
    results = {
        "Prix": [black_scholes_price(S, K, T, r, sigma, option_type)],
        "Delta": [delta(S, K, T, r, sigma, option_type)],
        "Gamma": [gamma(S, K, T, r, sigma)],
        "Vega": [vega(S, K, T, r, sigma)],
        "Theta": [theta(S, K, T, r, sigma, option_type)],
        "Rho": [rho(S, K, T, r, sigma, option_type)]
    }
    df = pd.DataFrame(results)
    st.dataframe(df)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger en CSV", csv, "greeks_result.csv", "text/csv")