# Agri-food Dashboard – UX+ Design Refresh (Streamlit)
# Source officielle: EC Agri-food Data Portal (API) – voir aide & citations dans l'app
# Réf: https://agridata.ec.europa.eu/extensions/DataPortal/API_Documentation.html

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime
import urllib.parse

# -------------------- Page config & theme --------------------
st.set_page_config(
    page_title="🌾 Agri-food EU – Markets Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles sobres et accessibles
st.markdown("""
<style>
:root { --brand:#2E8B57; --brand2:#3CB371; }
.main-header{
  background: linear-gradient(135deg,var(--brand),var(--brand2));
  padding:1.3rem 1.1rem;border-radius:14px;color:#fff;margin:0 0 1.1rem 0;
  box-shadow:0 6px 28px rgba(0,0,0,.08);
}
.small-muted{color:#f2f2f2;opacity:.9}
.metric-card{background:#fff;padding:1rem;border-radius:10px;
  border-left:4px solid var(--brand);box-shadow:0 2px 16px rgba(0,0,0,.06);}
.badge{display:inline-block;padding:.25rem .5rem;border-radius:999px;
  background:#0d6efd12;border:1px solid #0d6efd30;color:#0d6efd;font-size:.75rem;}
.helpbox{background:#e7f3ff;border:1px solid #b3d7ff;border-radius:8px;padding:0.8rem;}
.errbox{background:#fff5f5;border:1px solid #f5c2c7;border-radius:8px;padding:0.8rem;}
.okbox{background:#f0fff4;border:1px solid #b7f7c1;border-radius:8px;padding:0.8rem;}
footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
  <h1 style="margin:0;">🌾 Agri-food EU – Markets Dashboard</h1>
  <div class="small-muted">Surveillance des marchés agricoles (prix & production) •
    <span class="badge">Source: EC Agri-food Data Portal (API)</span>
  </div>
</div>
""", unsafe_allow_html=True)

# -------------------- API Client --------------------
class AgrifoodAPIClient:
    """Client API DG AGRI (Agri-food data portal)"""
    def __init__(self):
        self.base_url = "https://www.ec.europa.eu/agrifood/api"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "AgrifoodDashboard/1.1 (Streamlit)"
        })

    @st.cache_data(ttl=1800, show_spinner=False)
    def _make_request(_self, endpoint, params=None):
        url = f"{_self.base_url}/{endpoint}"
        try:
            r = _self.session.get(url, params=params, timeout=30)
            if r.status_code == 200:
                data = r.json()
                count = len(data) if isinstance(data, list) else (1 if data else 0)
                return data, "success", f"{count} enregistrements", url
            return None, f"http_{r.status_code}", f"Erreur HTTP {r.status_code}", url
        except requests.exceptions.Timeout:
            return None, "timeout", "Timeout API (>30s)", url
        except requests.exceptions.ConnectionError:
            return None, "connection", "Erreur de connexion", url
        except Exception as e:
            return None, "error", f"{type(e).__name__}: {e}", url

    # ---- Endpoints (prix) ----
    def get_beef_prices(self, member_states, years, weeks=None, months=None, categories=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if weeks: p["weeks"] = ",".join(map(str, weeks))
        if months: p["months"] = ",".join(map(str, months))
        if categories: p["carcassCategories"] = ",".join(categories)
        return self._make_request("beef/prices", p)

    def get_live_animal_prices(self, member_states, years, weeks=None, categories=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if weeks: p["weeks"] = ",".join(map(str, weeks))
        if categories: p["categories"] = ",".join(categories)
        return self._make_request("liveAnimal/prices", p)

    def get_raw_milk_prices(self, member_states, years, months=None, products=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if months: p["months"] = ",".join(map(str, months))
        if products: p["products"] = ",".join(products)
        return self._make_request("rawMilk/prices", p)

    def get_dairy_prices(self, member_states, years, weeks=None, products=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if weeks: p["weeks"] = ",".join(map(str, weeks))
        if products: p["products"] = ",".join(products)
        return self._make_request("dairy/prices", p)

    def get_olive_oil_prices(self, member_states, marketing_years=None, products=None, markets=None):
        p = {"memberStateCodes": ",".join(member_states)}
        if marketing_years: p["marketingYears"] = ",".join(marketing_years)
        if products: p["products"] = ",".join(products)
        if markets: p["markets"] = ",".join(markets)
        return self._make_request("oliveOil/prices", p)

    def get_cereal_prices(self, member_states, marketing_years=None, product_codes=None, stage_codes=None):
        p = {"memberStateCodes": ",".join(member_states)}
        if marketing_years: p["marketingYears"] = ",".join(marketing_years)
        if product_codes: p["productCodes"] = ",".join(product_codes)
        if stage_codes: p["stageCodes"] = ",".join(stage_codes)
        return self._make_request("cereal/prices", p)

    # ---- Endpoints (production) ----
    def get_beef_production(self, member_states, years, months=None, categories=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if months: p["months"] = ",".join(map(str, months))
        if categories: p["categories"] = ",".join(categories)
        return self._make_request("beef/production", p)

    def get_dairy_production(self, member_states, years, months=None, categories=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if months: p["months"] = ",".join(map(str, months))
        if categories: p["categories"] = ",".join(categories)
        return self._make_request("dairy/production", p)

    def get_olive_oil_production(self, member_states, granularity, production_years=None, months=None):
        p = {"memberStateCodes": ",".join(member_states), "granularity": granularity}
        if production_years: p["productionYears"] = ",".join(map(str, production_years))
        if months and granularity == "monthly": p["months"] = ",".join(map(str, months))
        return self._make_request("oliveOil/production", p)

    def get_cereal_production(self, member_states, years, crops=None):
        p = {"memberStateCodes": ",".join(member_states), "years": ",".join(map(str, years))}
        if crops: p["crops"] = ",".join(crops)
        return self._make_request("cereal/production", p)

    # ---- Listings ----
    def get_available_products(self, category):
        mapping = {
            "raw_milk": "rawMilk/products", "dairy": "dairy/products",
            "olive_oil": "oliveOil/products", "cereal": "cereal/products"
        }
        if category not in mapping: return None, "error", f"Catégorie {category} non supportée", None
        return self._make_request(mapping[category])

@st.cache_resource(show_spinner=False)
def get_api_client():
    return AgrifoodAPIClient()

api = get_api_client()

# -------------------- Helpers --------------------
def clean_price_series(df):
    price_cols = [c for c in df.columns if "price" in c.lower()]
    unit = df["unit"].iloc[0] if "unit" in df.columns and not df["unit"].isna().all() else "€"
    if price_cols:
        col = price_cols[0]
        s = (df[col].astype(str)
                .str.replace("€", "", regex=False)
                .str.replace(",", ".", regex=False)
                .str.extract(r"([0-9]+(?:\.[0-9]+)?)")[0]
                .astype(float))
        df["price_value"] = s
    else:
        df["price_value"] = None
    return df, unit

def parse_time_column(df):
    # Essaye: 'date' -> datetime ; sinon 'week' ou 'month'
    date_cols = [c for c in df.columns if "date" in c.lower()]
    if date_cols:
        c = date_cols[0]
        out = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
        if out.notna().any():
            df["time"] = out
            return df, "date"
    week_cols = [c for c in df.columns if "week" in c.lower()]
    if week_cols and "year" in df.columns:
        # construire ISO semaine
        df["time"] = pd.to_datetime(df["year"].astype(str) + "-W" + df[week_cols[0]].astype(str) + "-1", errors="coerce")
        return df, "week"
    month_cols = [c for c in df.columns if "month" in c.lower()]
    if month_cols and "year" in df.columns:
        df["time"] = pd.to_datetime(df["year"].astype(str) + "-" + df[month_cols[0]].astype(str) + "-01", errors="coerce")
        return df, "month"
    return df, None

def empty_state(msg="Choisissez des paramètres puis lancez une analyse."):
    st.info(msg)

def show_api_status(status, message, url):
    cols = st.columns([1,3])
    with cols[0]:
        if status == "success": st.markdown('<div class="okbox">✅ API OK</div>', unsafe_allow_html=True)
        else: st.markdown(f'<div class="errbox">❌ {message}</div>', unsafe_allow_html=True)
    with cols[1]:
        if url:
            st.markdown(f"**Requête API** : `{url}`")

def permalink_from_state(params: dict):
    # fabrique une URL partageable avec querystring (pour Streamlit Cloud)
    base = st.experimental_get_query_params()
    base.update(params)
    st.experimental_set_query_params(**base)
    return "?" + urllib.parse.urlencode(base, doseq=True)

# -------------------- Onboarding --------------------
with st.expander("ℹ️ Comment utiliser ce tableau de bord (clique pour ouvrir)", expanded=True):
    st.markdown(
        "- **1.** Choisissez un **type d'analyse** dans la barre latérale (Exploration, Prix, Production).\n"
        "- **2.** Sélectionnez pays, années (ou années marketing) et produits.\n"
        "- **3.** Cliquez **ANALYSER** : la *Vue graphique* s’affiche, puis *Données* et *Métadonnées*.\n"
        "- **Unités** : la majorité des prix sont en **€/100 kg** (à confirmer via la colonne `unit`).\n"
        "- **Années marketing** : p.ex. *2021/2022* pour céréales/huile d’olive.\n"
        "- **Sources** : API **Agri-food data portal** (Commission européenne).", help=None
    )
    st.caption("Docs & secteurs : API Doc, What’s new (API étendue bœuf/animaux vivants/céréales/huile d’olive), pages filières. Voir Aide.")

# -------------------- Sidebar --------------------
st.sidebar.title("🎛️ Configuration")
analysis_type = st.sidebar.radio("Type d'analyse", ["🔍 Exploration", "📊 Prix", "🏭 Production"])

# Presets rapides
with st.sidebar.expander("⚡ Presets rapides"):
    preset = st.selectbox("Choisir un preset", [
        "—",
        "Olive oil – PT/ES/IT – 2022/2023",
        "Cereals (BLT) – FR/DE – 2021/2022",
        "Beef (carcasses) – FR/ES/PT – 2023–2024",
        "Raw milk – FR/DE/NL – 2022–2024"
    ])
    if st.button("Charger le preset"):
        st.session_state["preset"] = preset

# -------------------- Exploration --------------------
if analysis_type == "🔍 Exploration":
    st.header("🔍 Exploration des listes de produits par catégorie")
    cats = ['raw_milk', 'dairy', 'olive_oil', 'cereal']
    for c in cats:
        with st.expander(f"📦 {c.replace('_',' ').title()}"):
            data, status, msg, url = api.get_available_products(c)
            show_api_status(status, msg, url)
            if status == "success" and data:
                df = pd.DataFrame(data if isinstance(data, list) else [data])
                st.dataframe(df, use_container_width=True)
            elif status == "success":
                empty_state("Aucun produit disponible signalé par l'API.")
            else:
                st.stop()

# -------------------- Prix --------------------
elif analysis_type == "📊 Prix":
    st.header("📊 Analyse des prix")

    # Gestion preset
    countries_default = ["PT", "ES", "FR"]
    years_default = [2022, 2023]
    marketing_default = ["2021/2022"]
    sector = st.sidebar.selectbox("Secteur", ["Bœuf (carcasses)", "Animaux vivants", "Lait cru", "Produits laitiers", "Huile d'olive", "Céréales"])

    if st.session_state.get("preset"):
        p = st.session_state["preset"]
        if "Olive oil" in p:
            sector = "Huile d'olive"; countries_default = ["PT","ES","IT"]; marketing_default = ["2022/2023"]
        elif "Cereals" in p:
            sector = "Céréales"; countries_default = ["FR","DE"]; marketing_default = ["2021/2022"]
        elif "Beef" in p:
            sector = "Bœuf (carcasses)"; countries_default = ["FR","ES","PT"]; years_default = [2023, 2024]
        elif "Raw milk" in p:
            sector = "Lait cru"; countries_default = ["FR","DE","NL"]; years_default = [2022, 2023, 2024]

    colA, colB = st.sidebar.columns(2)
    with colA:
        countries = st.multiselect("Pays", ["PT","ES","FR","IT","DE","NL","BE","PL","AT","SE","BG","EL"], default=countries_default)
    with colB:
        years_input = None
        if sector == "Huile d'olive":
            years_mkt = st.multiselect("Années marketing", ["2019/2020","2020/2021","2021/2022","2022/2023","2023/2024"], default=marketing_default)
        else:
            years_input = st.multiselect("Années", [2019,2020,2021,2022,2023,2024], default=years_default)

    # Paramètres spécifiques
    specific = {}
    if sector == "Bœuf (carcasses)":
        specific["categories"] = st.sidebar.multiselect("Catégories carcasses", ["heifers","cows","bulls","steers"], default=["heifers","cows"])
        specific["weeks"] = st.sidebar.multiselect("Semaines (opt.)", list(range(1,53)))
    elif sector == "Animaux vivants":
        specific["categories"] = st.sidebar.multiselect("Catégories", ["young store cattle","male calves beef type","male calves dairy type"], default=["young store cattle"])
    elif sector == "Lait cru":
        specific["products"] = st.sidebar.multiselect("Produits", ["raw milk","organic raw milk"], default=["raw milk"])
        specific["months"] = st.sidebar.multiselect("Mois (opt.)", list(range(1,13)))
    elif sector == "Produits laitiers":
        specific["products"] = st.sidebar.multiselect("Produits", ["butter","smp","wmp","cheese"], default=["butter"])
        specific["weeks"] = st.sidebar.multiselect("Semaines (opt.)", list(range(1,53)))
    elif sector == "Huile d'olive":
        specific["products"] = st.sidebar.multiselect("Produits", [
            "Extra virgin olive oil (up to 0.8%)","Virgin olive oil (up to 2%)","Lampante olive oil (2%)"
        ], default=["Extra virgin olive oil (up to 0.8%)"])
        specific["marketing_years"] = years_mkt
    elif sector == "Céréales":
        specific["product_codes"] = st.sidebar.multiselect("Codes produits", ["BLT","DUR","MAI","ORG","BARL"], default=["BLT"])
        specific["marketing_years"] = st.sidebar.multiselect("Années marketing", ["2019/2020","2020/2021","2021/2022","2022/2023","2023/2024"], default=marketing_default)

    run = st.sidebar.button("📊 ANALYSER", type="primary")

    if not run:
        empty_state("Choisissez vos paramètres puis cliquez **ANALYSER**.")
    else:
        if not countries:
            st.error("Veuillez sélectionner au moins un pays."); st.stop()

        with st.spinner("Récupération des données API…"):
            try:
                data, status, msg, url = None, "not_called", "", ""
                if sector == "Bœuf (carcasses)":
                    data, status, msg, url = api.get_beef_prices(countries, years_input, **specific)
                elif sector == "Animaux vivants":
                    data, status, msg, url = api.get_live_animal_prices(countries, years_input, **specific)
                elif sector == "Lait cru":
                    data, status, msg, url = api.get_raw_milk_prices(countries, years_input, **specific)
                elif sector == "Produits laitiers":
                    data, status, msg, url = api.get_dairy_prices(countries, years_input, **specific)
                elif sector == "Huile d'olive":
                    data, status, msg, url = api.get_olive_oil_prices(countries, **specific)
                elif sector == "Céréales":
                    data, status, msg, url = api.get_cereal_prices(countries, **specific)
            except Exception as e:
                st.error(f"Erreur appel API: {e}"); st.stop()

        show_api_status(status, msg, url)

        if status != "success" or not data:
            st.warning("Aucune donnée renvoyée pour ces critères. Essayez d’autres paramètres.")
            st.stop()

        df = pd.DataFrame(data)
        if df.empty:
            st.warning("Données vides."); st.stop()

        # Nettoyage prix & temps
        df, unit = clean_price_series(df)
        df, time_type = parse_time_column(df)

        # KPIs
        k1,k2,k3,k4 = st.columns(4)
        with k1: st.metric("Enregistrements", len(df))
        with k2: st.metric("Pays", df["memberStateCode"].nunique() if "memberStateCode" in df else 0)
        with k3:
            if "time" in df:
                st.metric("Période", f"{df['time'].min().date()} → {df['time'].max().date()}")
            else:
                st.metric("Période", "—")
        with k4:
            if df["price_value"].notna().any():
                st.metric("Prix moyen", f"{df['price_value'].mean():.2f} {unit}")
            else:
                st.metric("Prix", "N/D")

        # Tabs vues
        t1, t2, t3 = st.tabs(["📈 Vue graphique", "📋 Données", "🧭 Métadonnées & dictionnaire"])
        with t1:
            if "memberStateCode" in df and df["price_value"].notna().any():
                box = px.box(df, x="memberStateCode", y="price_value",
                             title=f"Distribution des prix – {sector} ({unit})")
                st.plotly_chart(box, use_container_width=True)
            if "time" in df and df["price_value"].notna().any() and "memberStateCode" in df:
                line = px.line(df.sort_values("time"), x="time", y="price_value",
                               color="memberStateCode",
                               title=f"Évolution temporelle – {sector} ({unit})")
                st.plotly_chart(line, use_container_width=True)

            with st.expander("🧠 Interprétation rapide"):
                st.markdown(
                    "- **Boxplot** : détecte médiane, dispersion, **outliers** ⇒ volatilité marché.\n"
                    "- **Courbe par pays** : compare trajectoires ; **dates marketing** peuvent décaler les séries.\n"
                    "- Vérifiez **unit** (€/100kg, €/t…) avant comparaison inter-produits."
                )

        with t2:
            st.dataframe(df, use_container_width=True, height=480)
            st.download_button("📄 Télécharger CSV", df.to_csv(index=False), file_name="agrifood_prices.csv", mime="text/csv")
            link = permalink_from_state({"view":"prices","sector":sector})
            st.caption(f"Permalien de cette vue : `{link}`")

        with t3:
            cols = [f"- `{c}`" for c in df.columns]
            st.markdown("**Colonnes disponibles**:\n" + "\n".join(cols))
            st.markdown("**Notes** :")
            st.markdown("- `memberStateCode` = code État membre (FR, ES, …)\n- `unit` = unité économique (ex. €/100kg)\n- `year/week/month` ou `date` selon endpoint\n- `price_value` = prix nettoyé (float) extrait de la colonne brute")

# -------------------- Production --------------------
elif analysis_type == "🏭 Production":
    st.header("🏭 Analyse de la production")
    production_type = st.sidebar.selectbox("Type", ["Bœuf","Produits laitiers","Huile d'olive","Céréales"])
    countries = st.sidebar.multiselect("Pays", ["PT","ES","FR","IT","DE","NL","AT"], default=["PT","FR"])
    years = st.sidebar.multiselect("Années", [2019,2020,2021,2022,2023,2024], default=[2022,2023])
    run = st.sidebar.button("📊 ANALYSER PRODUCTION", type="primary")

    if not run:
        empty_state("Sélectionnez vos paramètres puis lancez l’analyse.")
    else:
        if not countries: st.error("Sélectionnez au moins un pays."); st.stop()
        with st.spinner("Récupération des données de production…"):
            try:
                if production_type == "Bœuf":
                    data, status, msg, url = api.get_beef_production(countries, years)
                elif production_type == "Produits laitiers":
                    data, status, msg, url = api.get_dairy_production(countries, years)
                elif production_type == "Huile d'olive":
                    data, status, msg, url = api.get_olive_oil_production(countries, "annual", years)
                elif production_type == "Céréales":
                    data, status, msg, url = api.get_cereal_production(countries, years)
            except Exception as e:
                st.error(f"Erreur API: {e}"); st.stop()

        show_api_status(status, msg, url)
        if status != "success" or not data:
            st.warning("Aucune donnée pour ces critères."); st.stop()

        df = pd.DataFrame(data)
        if df.empty: st.warning("Données vides."); st.stop()

        metric_cols = [c for c in df.columns if any(k in c.lower() for k in ["production","tonnes","quantity","volume"])]
        if "memberStateCode" in df and metric_cols:
            fig = px.bar(df, x="memberStateCode", y=metric_cols[0],
                         title=f"Production {production_type} par pays – {metric_cols[0]}")
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True, height=480)
        st.download_button("📄 Télécharger CSV", df.to_csv(index=False), file_name="agrifood_production.csv", mime="text/csv")

# -------------------- Aide & Références --------------------
st.markdown("---")
with st.expander("📚 Aide & Références (sources officielles)"):
    st.markdown(
        "- **API Documentation** (DG AGRI, Agri-food data portal). "
        "[Ouvrir](https://agridata.ec.europa.eu/extensions/DataPortal/API_Documentation.html)\n"
        "- **What’s new (API & extensions)** : disponibilité des API bœuf, animaux vivants, céréales, huile d’olive & production. "
        "[Ouvrir](https://agridata.ec.europa.eu/extensions/DataPortal/whatsnew.html)\n"
        "- **Céréales (doc API sectorielle)** : endpoints & paramètres. "
        "[Ouvrir](https://agridata.ec.europa.eu/extensions/API_Documentation/cereals.html)\n"
        "- **Huile d’olive (page marché + dashboard PDF)** : contexte & définitions. "
        "[Ouvrir](https://agriculture.ec.europa.eu/data-and-analysis/markets/price-data/price-monitoring-sector/olive-oil_en)"
    )

st.caption("© Données officielles Commission européenne – Agri-food Data Portal. Utilisation conforme aux mentions du portail.")
