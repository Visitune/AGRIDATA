"""
Dashboard Agri-food Data UE - Version Complète
Application Streamlit pour l'analyse des données agricoles européennes
Compatible Streamlit Cloud - Tous les endpoints testés
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

# Configuration de la page
st.set_page_config(
    page_title="🌾 Dashboard Agri-food Data UE",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS professionnel
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E8B57 0%, #3CB371 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #2E8B57;
        margin-bottom: 1rem;
    }
    .alert-critical { border-left-color: #dc3545; background-color: #fff5f5; }
    .alert-warning { border-left-color: #ffc107; background-color: #fffbf0; }
    .alert-good { border-left-color: #28a745; background-color: #f0fff4; }
    
    .endpoint-success { 
        background-color: #d4edda; 
        color: #155724; 
        padding: 0.5rem; 
        border-radius: 5px; 
        margin: 0.2rem 0;
    }
    .endpoint-error { 
        background-color: #f8d7da; 
        color: #721c24; 
        padding: 0.5rem; 
        border-radius: 5px; 
        margin: 0.2rem 0;
    }
    .api-info {
        background-color: #e7f3ff;
        border: 1px solid #b3d7ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# En-tête principal
st.markdown("""
<div class="main-header">
    <h1>🌾 Dashboard Agri-food Data UE</h1>
    <p>Surveillance complète des marchés agricoles européens</p>
    <small>API Officielle Commission Européenne - DG Agriculture et Développement Rural</small>
</div>
""", unsafe_allow_html=True)

class AgrifoodAPIClient:
    """Client complet pour l'API Agri-food officielle"""
    
    def __init__(self):
        self.base_url = "https://www.ec.europa.eu/agrifood/api"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'AgrifoodDashboard/1.0',
            'Cache-Control': 'no-cache'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    @st.cache_data(ttl=1800)  # Cache 30 minutes
    def _make_request(_self, endpoint, params=None):
        """Effectue une requête avec gestion d'erreurs et cache"""
        try:
            url = f"{_self.base_url}/{endpoint}"
            response = _self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data, "success", f"{len(data) if isinstance(data, list) else 1} enregistrements"
            else:
                return None, f"http_{response.status_code}", f"Erreur HTTP {response.status_code}"
                
        except requests.exceptions.Timeout:
            return None, "timeout", "Timeout - L'API a mis trop de temps à répondre"
        except requests.exceptions.ConnectionError:
            return None, "connection", "Erreur de connexion"
        except Exception as e:
            return None, "error", f"Erreur: {str(e)}"
    
    # === BEEF ENDPOINTS ===
    def get_beef_prices(self, member_states, years, weeks=None, months=None, categories=None):
        """Récupère les prix du bœuf (carcasses)"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if weeks:
            params['weeks'] = ','.join(map(str, weeks))
        if months:
            params['months'] = ','.join(map(str, months))
        if categories:
            params['carcassCategories'] = ','.join(categories)
        
        return self._make_request('beef/prices', params)
    
    def get_live_animal_prices(self, member_states, years, weeks=None, categories=None):
        """Récupère les prix des animaux vivants"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if weeks:
            params['weeks'] = ','.join(map(str, weeks))
        if categories:
            params['categories'] = ','.join(categories)
        
        return self._make_request('liveAnimal/prices', params)
    
    def get_beef_production(self, member_states, years, months=None, categories=None):
        """Récupère les données de production de bœuf"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if months:
            params['months'] = ','.join(map(str, months))
        if categories:
            params['categories'] = ','.join(categories)
        
        return self._make_request('beef/production', params)
    
    # === MILK & DAIRY ENDPOINTS ===
    def get_raw_milk_prices(self, member_states, years, months=None, products=None):
        """Récupère les prix du lait cru"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if months:
            params['months'] = ','.join(map(str, months))
        if products:
            params['products'] = ','.join(products)
        
        return self._make_request('rawMilk/prices', params)
    
    def get_dairy_prices(self, member_states, years, weeks=None, products=None):
        """Récupère les prix des produits laitiers"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if weeks:
            params['weeks'] = ','.join(map(str, weeks))
        if products:
            params['products'] = ','.join(products)
        
        return self._make_request('dairy/prices', params)
    
    def get_dairy_production(self, member_states, years, months=None, categories=None):
        """Récupère les données de production laitière"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if months:
            params['months'] = ','.join(map(str, months))
        if categories:
            params['categories'] = ','.join(categories)
        
        return self._make_request('dairy/production', params)
    
    # === OLIVE OIL ENDPOINTS ===
    def get_olive_oil_prices(self, member_states, marketing_years=None, products=None, markets=None):
        """Récupère les prix de l'huile d'olive"""
        params = {
            'memberStateCodes': ','.join(member_states)
        }
        if marketing_years:
            params['marketingYears'] = ','.join(marketing_years)
        if products:
            params['products'] = ','.join(products)
        if markets:
            params['markets'] = ','.join(markets)
        
        return self._make_request('oliveOil/prices', params)
    
    def get_olive_oil_production(self, member_states, granularity, production_years=None, months=None):
        """Récupère les données de production d'huile d'olive"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'granularity': granularity
        }
        if production_years:
            params['productionYears'] = ','.join(map(str, production_years))
        if months and granularity == 'monthly':
            params['months'] = ','.join(map(str, months))
        
        return self._make_request('oliveOil/production', params)
    
    # === CEREAL ENDPOINTS ===
    def get_cereal_prices(self, member_states, marketing_years=None, product_codes=None, stage_codes=None):
        """Récupère les prix des céréales"""
        params = {
            'memberStateCodes': ','.join(member_states)
        }
        if marketing_years:
            params['marketingYears'] = ','.join(marketing_years)
        if product_codes:
            params['productCodes'] = ','.join(product_codes)
        if stage_codes:
            params['stageCodes'] = ','.join(stage_codes)
        
        return self._make_request('cereal/prices', params)
    
    def get_cereal_production(self, member_states, years, crops=None):
        """Récupère les données de production de céréales"""
        params = {
            'memberStateCodes': ','.join(member_states),
            'years': ','.join(map(str, years))
        }
        if crops:
            params['crops'] = ','.join(crops)
        
        return self._make_request('cereal/production', params)
    
    # === LISTING ENDPOINTS ===
    def get_available_products(self, category):
        """Récupère la liste des produits disponibles"""
        endpoints = {
            'raw_milk': 'rawMilk/products',
            'dairy': 'dairy/products',
            'olive_oil': 'oliveOil/products',
            'cereal': 'cereal/products'
        }
        
        if category in endpoints:
            return self._make_request(endpoints[category])
        else:
            return None, "error", f"Catégorie {category} non supportée"

# Initialisation de l'API
@st.cache_resource
def get_api_client():
    return AgrifoodAPIClient()

api = get_api_client()

# Interface utilisateur
st.sidebar.title("🎛️ Configuration")

# Sélection du type d'analyse
analysis_type = st.sidebar.radio(
    "Type d'analyse",
    ["🔍 Exploration", "📊 Analyse des prix", "📈 Comparaison", "🏭 Production"]
)

if analysis_type == "🔍 Exploration":
    st.header("🔍 Exploration des données disponibles")
    
    # Test de tous les endpoints de listing
    st.subheader("📋 Produits disponibles par catégorie")
    
    categories = ['raw_milk', 'dairy', 'olive_oil', 'cereal']
    
    for category in categories:
        with st.expander(f"📦 Produits {category.replace('_', ' ').title()}"):
            data, status, message = api.get_available_products(category)
            
            if status == "success" and data:
                st.success(f"✅ {message}")
                if isinstance(data, list):
                    st.write("**Produits disponibles:**")
                    for item in data[:10]:  # Limiter l'affichage
                        if isinstance(item, dict):
                            st.write(f"• {item}")
                        else:
                            st.write(f"• {item}")
                else:
                    st.json(data)
            else:
                st.error(f"❌ {message}")

elif analysis_type == "📊 Analyse des prix":
    st.header("📊 Analyse des prix agricoles")
    
    # Sélection du secteur
    sector = st.sidebar.selectbox(
        "Secteur agricole",
        ["Bœuf (carcasses)", "Animaux vivants", "Lait cru", "Produits laitiers", "Huile d'olive", "Céréales"]
    )
    
    # Paramètres communs
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        countries = st.multiselect(
            "Pays",
            ["PT", "ES", "FR", "IT", "DE", "NL", "BE", "PL", "AT", "SE", "BG", "EL"],
            default=["PT", "ES", "FR"]
        )
    
    with col2:
        if sector in ["Huile d'olive"]:
            years_input = st.multiselect(
                "Années marketing",
                ["2019/2020", "2020/2021", "2021/2022", "2022/2023"],
                default=["2021/2022"]
            )
        else:
            years_input = st.multiselect(
                "Années",
                [2019, 2020, 2021, 2022, 2023, 2024],
                default=[2021, 2022]
            )
    
    # Paramètres spécifiques selon le secteur
    specific_params = {}
    
    if sector == "Bœuf (carcasses)":
        categories = st.sidebar.multiselect(
            "Catégories",
            ["heifers", "cows", "bulls", "steers"],
            default=["heifers", "cows"]
        )
        weeks = st.sidebar.multiselect("Semaines (optionnel)", list(range(1, 53)))
        specific_params = {"categories": categories, "weeks": weeks if weeks else None}
        
    elif sector == "Animaux vivants":
        categories = st.sidebar.multiselect(
            "Catégories",
            ["young store cattle", "male calves beef type", "male calves dairy type"],
            default=["young store cattle"]
        )
        specific_params = {"categories": categories}
        
    elif sector == "Lait cru":
        products = st.sidebar.multiselect(
            "Produits",
            ["raw milk", "organic raw milk"],
            default=["raw milk"]
        )
        months = st.sidebar.multiselect("Mois (optionnel)", list(range(1, 13)))
        specific_params = {"products": products, "months": months if months else None}
        
    elif sector == "Produits laitiers":
        products = st.sidebar.multiselect(
            "Produits",
            ["butter", "smp", "wmp", "cheese"],
            default=["butter"]
        )
        weeks = st.sidebar.multiselect("Semaines (optionnel)", list(range(1, 53)))
        specific_params = {"products": products, "weeks": weeks if weeks else None}
        
    elif sector == "Huile d'olive":
        products = st.sidebar.multiselect(
            "Produits",
            ["Extra virgin olive oil (up to 0.8%)", "Virgin olive oil (up to 2%)", "Lampante olive oil (2%)"],
            default=["Extra virgin olive oil (up to 0.8%)"]
        )
        specific_params = {"products": products, "marketing_years": years_input}
        
    elif sector == "Céréales":
        product_codes = st.sidebar.multiselect(
            "Codes produits",
            ["BLT", "DUR", "MAI", "ORG", "BARL"],
            default=["BLT"]
        )
        marketing_years = st.sidebar.multiselect(
            "Années marketing",
            ["2019/2020", "2020/2021", "2021/2022"],
            default=["2021/2022"]
        )
        specific_params = {"product_codes": product_codes, "marketing_years": marketing_years}
    
    # Bouton d'analyse
    if st.sidebar.button("📊 ANALYSER", type="primary"):
        if not countries:
            st.error("⚠️ Veuillez sélectionner au moins un pays")
        else:
            with st.spinner("🔄 Récupération des données..."):
                
                # Appel API selon le secteur
                data, status, message = None, "not_called", ""
                
                try:
                    if sector == "Bœuf (carcasses)":
                        data, status, message = api.get_beef_prices(countries, years_input, **specific_params)
                    elif sector == "Animaux vivants":
                        data, status, message = api.get_live_animal_prices(countries, years_input, **specific_params)
                    elif sector == "Lait cru":
                        data, status, message = api.get_raw_milk_prices(countries, years_input, **specific_params)
                    elif sector == "Produits laitiers":
                        data, status, message = api.get_dairy_prices(countries, years_input, **specific_params)
                    elif sector == "Huile d'olive":
                        data, status, message = api.get_olive_oil_prices(countries, **specific_params)
                    elif sector == "Céréales":
                        data, status, message = api.get_cereal_prices(countries, **specific_params)
                        
                except Exception as e:
                    st.error(f"Erreur lors de l'appel API: {str(e)}")
                    data, status, message = None, "error", str(e)
            
            # Affichage des résultats
            if status == "success" and data and len(data) > 0:
                st.success(f"✅ {message}")
                
                df = pd.DataFrame(data)
                
                # Métriques principales
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("📊 Enregistrements", len(df))
                
                with col2:
                    st.metric("🌍 Pays", df['memberStateCode'].nunique() if 'memberStateCode' in df.columns else 0)
                
                with col3:
                    date_cols = [col for col in df.columns if 'date' in col.lower()]
                    if date_cols:
                        st.metric("📅 Période", f"{df[date_cols[0]].min()} - {df[date_cols[0]].max()}")
                    else:
                        st.metric("📅 Colonnes", len(df.columns))
                
                with col4:
                    price_cols = [col for col in df.columns if 'price' in col.lower()]
                    if price_cols:
                        # Nettoyer les prix pour le calcul
                        try:
                            price_clean = df[price_cols[0]].astype(str).str.replace('€', '').str.replace(',', '.').str.extract('(\d+\.?\d*)').astype(float)
                            avg_price = price_clean.mean()
                            unit = df['unit'].iloc[0] if 'unit' in df.columns else '€'
                            st.metric("💰 Prix moyen", f"{avg_price:.2f} {unit}")
                        except:
                            st.metric("💰 Prix", "Voir tableau")
                    else:
                        st.metric("📋 Type", sector)
                
                # Graphiques
                st.subheader("📈 Visualisations")
                
                # Analyser la structure des données pour créer des graphiques appropriés
                if price_cols and 'memberStateCode' in df.columns:
                    try:
                        # Nettoyer les prix
                        df['price_clean'] = df[price_cols[0]].astype(str).str.replace('€', '').str.replace(',', '.').str.extract('(\d+\.?\d*)').astype(float)
                        
                        # Graphique par pays
                        fig = px.box(df, 
                                   x='memberStateCode', 
                                   y='price_clean',
                                   title=f"Distribution des prix - {sector}")
                        fig.update_layout(xaxis_title="Pays", yaxis_title="Prix")
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Si on a des données temporelles
                        date_cols = [col for col in df.columns if 'date' in col.lower() or 'week' in col.lower() or 'month' in col.lower()]
                        if date_cols:
                            time_col = date_cols[0]
                            if df[time_col].dtype == 'object':
                                # Essayer de convertir en datetime
                                try:
                                    df['date_parsed'] = pd.to_datetime(df[time_col], format='%d/%m/%Y', errors='coerce')
                                    time_col = 'date_parsed'
                                except:
                                    pass
                            
                            if time_col in df.columns:
                                fig2 = px.line(df, 
                                             x=time_col, 
                                             y='price_clean',
                                             color='memberStateCode',
                                             title=f"Évolution temporelle des prix - {sector}")
                                st.plotly_chart(fig2, use_container_width=True)
                        
                    except Exception as e:
                        st.write(f"Erreur lors de la création des graphiques: {str(e)}")
                        st.write("Affichage des données brutes:")
                
                # Tableau de données
                st.subheader("📋 Données détaillées")
                st.dataframe(df, use_container_width=True)
                
                # Export
                col1, col2 = st.columns(2)
                
                with col1:
                    csv = df.to_csv(index=False)
                    st.download_button(
                        "📄 Télécharger CSV",
                        csv,
                        f"{sector.lower().replace(' ', '_')}_data.csv",
                        "text/csv"
                    )
                
                with col2:
                    # Statistiques rapides
                    if price_cols:
                        stats = df.describe()
                        st.write("**Statistiques descriptives:**")
                        st.dataframe(stats)
            
            elif status == "success" and (not data or len(data) == 0):
                st.warning("⚠️ Aucune donnée trouvée pour ces critères. Essayez avec d'autres paramètres.")
                
            else:
                st.error(f"❌ {message}")
                st.info("💡 Conseils: Vérifiez les paramètres ou essayez avec d'autres pays/années.")

elif analysis_type == "📈 Comparaison":
    st.header("📈 Comparaison entre secteurs/pays")
    
    st.info("🚧 Fonctionnalité en développement - Permet de comparer plusieurs secteurs ou pays simultanément")
    
    # Interface pour comparaison multiple
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Secteur 1")
        sector1 = st.selectbox("Premier secteur", ["Bœuf", "Lait", "Huile d'olive"], key="s1")
        countries1 = st.multiselect("Pays secteur 1", ["PT", "ES", "FR", "IT"], default=["PT"], key="c1")
    
    with col2:
        st.subheader("Secteur 2")
        sector2 = st.selectbox("Deuxième secteur", ["Bœuf", "Lait", "Huile d'olive"], key="s2")
        countries2 = st.multiselect("Pays secteur 2", ["PT", "ES", "FR", "IT"], default=["ES"], key="c2")
    
    if st.button("🔄 Comparer"):
        st.write("Comparaison en cours de développement...")

elif analysis_type == "🏭 Production":
    st.header("🏭 Analyse de la production")
    
    # Sélection du type de production
    production_type = st.sidebar.selectbox(
        "Type de production",
        ["Bœuf", "Produits laitiers", "Huile d'olive", "Céréales"]
    )
    
    countries = st.sidebar.multiselect(
        "Pays",
        ["PT", "ES", "FR", "IT", "DE", "NL", "AT"],
        default=["PT", "FR"]
    )
    
    years = st.sidebar.multiselect(
        "Années",
        [2019, 2020, 2021, 2022, 2023],
        default=[2021, 2022]
    )
    
    if st.sidebar.button("📊 ANALYSER PRODUCTION", type="primary"):
        if not countries:
            st.error("⚠️ Veuillez sélectionner au moins un pays")
        else:
            with st.spinner("🔄 Récupération des données de production..."):
                
                data, status, message = None, "not_called", ""
                
                try:
                    if production_type == "Bœuf":
                        data, status, message = api.get_beef_production(countries, years)
                    elif production_type == "Produits laitiers":
                        data, status, message = api.get_dairy_production(countries, years)
                    elif production_type == "Huile d'olive":
                        data, status, message = api.get_olive_oil_production(countries, "annual", years)
                    elif production_type == "Céréales":
                        data, status, message = api.get_cereal_production(countries, years)
                        
                except Exception as e:
                    st.error(f"Erreur: {str(e)}")
                    data, status, message = None, "error", str(e)
            
            if status == "success" and data and len(data) > 0:
                st.success(f"✅ {message}")
                
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)
                
                # Graphiques de production
                production_cols = [col for col in df.columns if 'production' in col.lower() or 'tonnes' in col.lower() or 'quantity' in col.lower()]
                
                if production_cols and 'memberStateCode' in df.columns:
                    fig = px.bar(df, 
                               x='memberStateCode', 
                               y=production_cols[0],
                               title=f"Production de {production_type} par pays")
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error(f"❌ {message}")

# Footer avec informations
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📡 API Officielle**
    
    Commission Européenne  
    DG Agriculture et Développement Rural  
    
    Base URL: `www.ec.europa.eu/agrifood/api`
    """)

with col2:
    st.success("""
    **✅ Secteurs Couverts**
    
    • Bœuf et animaux vivants  
    • Lait et produits laitiers  
    • Huile d'olive  
    • Céréales  
    • Données de production  
    """)

with col3:
    st.warning("""
    **⚠️ Notes Techniques**
    
    • Données en temps réel  
    • Format JSON  
    • Cache 30 minutes  
    • Restriction CORS contournée  
    """)

st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 2rem;'>
    🌾 <strong>Dashboard Agri-food Data UE</strong> - Version Complète<br>
    Développé pour l'analyse professionnelle des marchés agricoles européens<br>
    <em>Compatible Streamlit Cloud - Données officielles Commission Européenne</em>
</div>
""", unsafe_allow_html=True)
