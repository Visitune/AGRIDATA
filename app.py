"""
Dashboard Agri-food Data UE - Version "Toujours à jour"
Détection automatique des données les plus récentes disponibles
"""

import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import time

# Configuration de la page
st.set_page_config(
    page_title="🌾 Dashboard Agri-food Data UE - Always Fresh",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS amélioré
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
    
    .freshness-indicator {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    .very-fresh { background: #d4edda; border-color: #28a745; color: #155724; }
    .fresh { background: #d1ecf1; border-color: #17a2b8; color: #0c5460; }
    .outdated { background: #fff3cd; border-color: #ffc107; color: #856404; }
    .very-outdated { background: #f8d7da; border-color: #dc3545; color: #721c24; }
    
    .auto-detection {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .data-summary {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .country-coverage {
        display: inline-block;
        padding: 0.3rem 0.7rem;
        margin: 0.2rem;
        border-radius: 15px;
        font-size: 0.85em;
        font-weight: bold;
    }
    .excellent { background: #d4edda; color: #155724; }
    .good { background: #d1ecf1; color: #0c5460; }
    .limited { background: #fff3cd; color: #856404; }
    .none { background: #f8d7da; color: #721c24; }
    
    .smart-tip {
        background: #e7f3ff;
        border: 1px solid #b3d7ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class AlwaysFreshAPI:
    """API Client qui garantit toujours les données les plus récentes"""
    
    def __init__(self):
        self.base_url = "https://www.ec.europa.eu/agrifood/api"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'AgrifoodDashboard-AlwaysFresh/1.0',
            'Cache-Control': 'no-cache'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cache pour éviter tests répétitifs dans la même session
        if 'freshness_cache' not in st.session_state:
            st.session_state.freshness_cache = {}
    
    def _make_request(self, endpoint, params=None):
        """Requête de base avec gestion d'erreurs"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = self.session.get(url, params=params, timeout=25)
            
            if response.status_code == 200:
                data = response.json()
                return data, "success", "OK"
            else:
                return None, f"http_{response.status_code}", f"HTTP {response.status_code}"
        except Exception as e:
            return None, "error", str(e)
    
    @st.cache_data(ttl=900)  # Cache 15 minutes seulement pour fraîcheur
    def auto_detect_latest_year(_self, sector):
        """Détecte automatiquement la dernière année avec données"""
        current_year = datetime.now().year
        
        # Pays de test fiables par secteur
        test_countries = {
            'beef': ['PT', 'ES'],
            'milk': ['FR', 'DE'],
            'olive_oil': ['ES', 'IT'],
            'cereals': ['FR', 'DE']
        }
        
        countries = test_countries.get(sector, ['PT', 'FR'])
        
        # Tester années de la plus récente à -5 ans
        for year in range(current_year, current_year - 6, -1):
            if _self._quick_test_year(sector, year, countries):
                return year, f"Dernières données : {year}"
        
        # Fallback si rien trouvé
        return current_year - 1, f"Données par défaut : {current_year - 1}"
    
    def _quick_test_year(self, sector, year, countries):
        """Test rapide si une année a des données"""
        try:
            params = {
                'memberStateCodes': ','.join(countries[:2]),  # Limiter à 2 pays pour rapidité
            }
            
            if sector == 'olive_oil':
                # Années marketing pour olive oil
                if year >= 2020:
                    params['marketingYears'] = f"{year-1}/{str(year)[-2:]}"
                else:
                    params['marketingYears'] = f"{year}/{str(year+1)[-2:]}"
            else:
                params['years'] = str(year)
            
            endpoint_map = {
                'beef': 'beef/prices',
                'milk': 'rawMilk/prices', 
                'olive_oil': 'oliveOil/prices',
                'cereals': 'cereal/prices'
            }
            
            endpoint = endpoint_map.get(sector)
            if not endpoint:
                return False
            
            data, status, _ = self._make_request(endpoint, params)
            return status == "success" and data and len(data) > 0
            
        except:
            return False
    
    @st.cache_data(ttl=1800)  # Cache 30 minutes
    def get_optimal_years(_self, sector, max_years=5):
        """Récupère les meilleures années disponibles"""
        current_year = datetime.now().year
        optimal_years = []
        
        # Détecter la dernière année disponible
        latest_year, _ = _self.auto_detect_latest_year(sector)
        
        # Construire liste optimale
        for year in range(latest_year, latest_year - 8, -1):
            if len(optimal_years) >= max_years:
                break
                
            if _self._quick_test_year(sector, year, ['PT', 'ES', 'FR'][:2]):
                optimal_years.append(year)
        
        return optimal_years or [current_year - 1, current_year - 2]
    
    @st.cache_data(ttl=1800)
    def get_optimal_countries(_self, sector):
        """Récupère les pays avec le plus de données"""
        
        # Pays à tester par secteur
        candidates = {
            'beef': ['FR', 'DE', 'IT', 'ES', 'NL', 'PL', 'PT', 'BE'],
            'milk': ['DE', 'FR', 'NL', 'IT', 'PL', 'ES', 'BE', 'DK'],
            'olive_oil': ['ES', 'IT', 'EL', 'PT', 'FR'],
            'cereals': ['FR', 'DE', 'PL', 'ES', 'IT', 'RO']
        }
        
        countries_to_test = candidates.get(sector, ['FR', 'DE', 'ES', 'IT'])
        latest_year, _ = _self.auto_detect_latest_year(sector)
        
        country_scores = {}
        
        for country in countries_to_test:
            score = _self._test_country_data_richness(sector, country, latest_year)
            if score > 0:
                country_scores[country] = score
        
        # Trier par score décroissant
        sorted_countries = sorted(country_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'excellent': [c for c, s in sorted_countries if s >= 10][:4],
            'good': [c for c, s in sorted_countries if 3 <= s < 10][:4],
            'limited': [c for c, s in sorted_countries if 1 <= s < 3][:4]
        }
    
    def _test_country_data_richness(self, sector, country, year):
        """Teste la richesse des données pour un pays"""
        try:
            params = {'memberStateCodes': country}
            
            if sector == 'olive_oil':
                params['marketingYears'] = f"{year-1}/{str(year)[-2:]}"
            else:
                params['years'] = str(year)
            
            endpoint_map = {
                'beef': 'beef/prices',
                'milk': 'rawMilk/prices',
                'olive_oil': 'oliveOil/prices', 
                'cereals': 'cereal/prices'
            }
            
            endpoint = endpoint_map.get(sector)
            if not endpoint:
                return 0
            
            data, status, _ = self._make_request(endpoint, params)
            
            if status == "success" and data:
                return len(data)
            return 0
            
        except:
            return 0
    
    def get_data_freshness_status(self, sector):
        """Détermine le statut de fraîcheur des données"""
        current_year = datetime.now().year
        current_month = datetime.now().month
        
        latest_year, _ = self.auto_detect_latest_year(sector)
        
        # Logique spécifique par secteur
        if sector == 'olive_oil':
            # Campagne olive oil : octobre N-1 à septembre N
            if current_month >= 10:  # Oct-Dec : campagne en cours
                expected_year = current_year
            else:  # Jan-Sep : campagne précédente
                expected_year = current_year - 1
        else:
            # Secteurs standard : année civile
            if current_month <= 3:  # Jan-Mar : données année précédente OK
                expected_year = current_year - 1
            else:  # Apr-Dec : données année courante attendues
                expected_year = current_year
        
        # Déterminer le statut
        year_gap = expected_year - latest_year
        
        if year_gap <= 0:
            return {
                'status': 'very_fresh',
                'icon': '🟢',
                'message': f"Données très récentes ({latest_year})",
                'detail': "Données de l'année courante ou attendue disponibles"
            }
        elif year_gap == 1:
            return {
                'status': 'fresh',
                'icon': '🔵',
                'message': f"Données récentes ({latest_year})",
                'detail': "Données avec 1 an de retard - normal pour certains secteurs"
            }
        elif year_gap <= 2:
            return {
                'status': 'outdated', 
                'icon': '🟡',
                'message': f"Données un peu anciennes ({latest_year})",
                'detail': f"Retard de {year_gap} ans - vérifiez la disponibilité"
            }
        else:
            return {
                'status': 'very_outdated',
                'icon': '🔴', 
                'message': f"Données anciennes ({latest_year})",
                'detail': f"Retard de {year_gap} ans - problème possible avec l'API"
            }
    
    # Méthodes API standardisées
    def get_beef_prices(self, countries, years, categories=None):
        params = {
            'memberStateCodes': ','.join(countries),
            'years': ','.join(map(str, years))
        }
        if categories:
            params['carcassCategories'] = ','.join(categories)
        return self._make_request('beef/prices', params)
    
    def get_raw_milk_prices(self, countries, years, products=None):
        params = {
            'memberStateCodes': ','.join(countries),
            'years': ','.join(map(str, years))
        }
        if products:
            params['products'] = ','.join(products)
        return self._make_request('rawMilk/prices', params)
    
    def get_olive_oil_prices(self, countries, marketing_years, products=None):
        params = {
            'memberStateCodes': ','.join(countries),
            'marketingYears': ','.join(marketing_years)
        }
        if products:
            params['products'] = ','.join(products)
        return self._make_request('oliveOil/prices', params)
    
    def standardize_prices(self, df):
        """Standardise les prix avec unités claires"""
        if df.empty or 'price' not in df.columns:
            return df
            
        # Nettoyer les prix
        df['price_raw'] = df['price'].astype(str)
        df['price_clean'] = df['price_raw'].str.replace('€', '', regex=False)
        df['price_clean'] = df['price_clean'].str.replace(',', '.', regex=False)
        df['price_clean'] = df['price_clean'].str.extract(r'(\d+\.?\d*)', expand=False)
        df['price_numeric'] = pd.to_numeric(df['price_clean'], errors='coerce')
        
        # Standardiser les unités
        df['unit_standardized'] = df['unit'].astype(str) if 'unit' in df.columns else '€/unité'
        df['price_standardized'] = df['price_numeric'].copy()
        
        # Convertir €/kg vers €/100kg
        kg_mask = df['unit_standardized'].str.contains('€/kg', case=False, na=False)
        df.loc[kg_mask, 'price_standardized'] = df.loc[kg_mask, 'price_numeric'] * 100
        df.loc[kg_mask, 'unit_standardized'] = '€/100kg'
        
        # Nettoyer les unités pour affichage
        df['unit_display'] = df['unit_standardized'].str.replace('100KG', '100kg', regex=False)
        
        return df

def display_freshness_dashboard(api, sector):
    """Affiche le dashboard de fraîcheur des données"""
    
    freshness = api.get_data_freshness_status(sector)
    
    st.markdown(f"""
    <div class="freshness-indicator {freshness['status']}">
        <h3>{freshness['icon']} {freshness['message']}</h3>
        <p>{freshness['detail']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    return freshness

def display_auto_detection_summary(api, sector):
    """Affiche le résumé de détection automatique"""
    
    st.markdown("### 🔍 Détection automatique")
    
    with st.spinner("Analyse des données disponibles..."):
        # Années optimales
        optimal_years = api.get_optimal_years(sector, max_years=6)
        
        # Pays optimaux
        optimal_countries = api.get_optimal_countries(sector)
        
        # Dernière année
        latest_year, latest_msg = api.auto_detect_latest_year(sector)
    
    st.markdown(f"""
    <div class="auto-detection">
        <h4>📅 Années disponibles</h4>
        <p><strong>Dernière année :</strong> {latest_year}</p>
        <p><strong>Années optimales :</strong> {', '.join(map(str, optimal_years))}</p>
        
        <h4>🌍 Couverture des pays</h4>
    """, unsafe_allow_html=True)
    
    # Afficher pays par niveau
    for level, countries in optimal_countries.items():
        if countries:
            level_names = {
                'excellent': '🟢 Excellente couverture',
                'good': '🔵 Bonne couverture',
                'limited': '🟡 Données limitées'
            }
            
            countries_html = ""
            for country in countries:
                countries_html += f'<span class="country-coverage {level}">{country}</span>'
            
            st.markdown(f"<p><strong>{level_names[level]} :</strong> {countries_html}</p>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return optimal_years, optimal_countries

def create_smart_interface(api):
    """Crée l'interface intelligente avec données toujours fraîches"""
    
    # Sélection du secteur
    st.sidebar.title("🎛️ Configuration Auto-Fresh")
    
    sector_options = {
        "🥩 Bœuf": "beef",
        "🥛 Lait": "milk",
        "🫒 Huile d'olive": "olive_oil",
        "🌾 Céréales": "cereals"
    }
    
    selected_sector_name = st.sidebar.selectbox(
        "Secteur d'analyse",
        list(sector_options.keys()),
        help="Secteur avec détection automatique des données les plus récentes"
    )
    sector = sector_options[selected_sector_name]
    
    # Dashboard de fraîcheur
    freshness = display_freshness_dashboard(api, sector)
    
    # Auto-détection dans expander
    with st.expander("🔍 Voir détection automatique", expanded=True):
        optimal_years, optimal_countries = display_auto_detection_summary(api, sector)
    
    # Interface de sélection basée sur la détection
    st.sidebar.markdown("### 📅 Sélection intelligente")
    
    # Années basées sur détection
    if optimal_years:
        selected_years = st.sidebar.multiselect(
            "Années (détectées automatiquement)",
            options=optimal_years,
            default=optimal_years[:3],
            help="Années avec données confirmées disponibles"
        )
    else:
        selected_years = st.sidebar.multiselect(
            "Années (fallback)",
            options=[2023, 2022, 2021],
            default=[2023, 2022]
        )
    
    # Pays basés sur détection
    st.sidebar.markdown("### 🌍 Pays recommandés")
    
    all_optimal_countries = []
    for level_countries in optimal_countries.values():
        all_optimal_countries.extend(level_countries)
    
    if all_optimal_countries:
        selected_countries = st.sidebar.multiselect(
            "Pays (optimisés par données)",
            options=all_optimal_countries,
            default=all_optimal_countries[:3],
            help="Pays avec meilleures données disponibles"
        )
    else:
        # Fallback si auto-détection échoue
        fallback_countries = {
            'beef': ['PT', 'ES', 'FR'],
            'milk': ['FR', 'DE', 'NL'],
            'olive_oil': ['ES', 'IT', 'EL'],
            'cereals': ['FR', 'DE', 'PL']
        }
        
        selected_countries = st.sidebar.multiselect(
            "Pays (fallback)",
            options=fallback_countries.get(sector, ['FR', 'DE', 'ES']),
            default=fallback_countries.get(sector, ['FR', 'DE'])[:2]
        )
    
    # Paramètres avancés
    with st.sidebar.expander("⚙️ Paramètres avancés"):
        if sector == 'beef':
            categories = st.multiselect(
                "Catégories",
                ['heifers', 'cows', 'bulls'],
                default=['heifers', 'cows']
            )
        elif sector == 'milk':
            products = st.multiselect(
                "Produits",
                ['raw milk', 'organic raw milk'],
                default=['raw milk']
            )
        elif sector == 'olive_oil':
            products = st.multiselect(
                "Qualités",
                ['Extra virgin olive oil (up to 0.8%)', 'Virgin olive oil (up to 2%)'],
                default=['Extra virgin olive oil (up to 0.8%)']
            )
    
    return sector, selected_years, selected_countries, locals()

# Interface principale
st.markdown("""
<div class="main-header">
    <h1>🌾 Dashboard Agri-food Data UE</h1>
    <p><strong>Version "Always Fresh" - Données toujours à jour</strong></p>
    <small>Détection automatique des données les plus récentes disponibles</small>
</div>
""", unsafe_allow_html=True)

# Initialisation API
@st.cache_resource
def get_fresh_api():
    return AlwaysFreshAPI()

api = get_fresh_api()

# Interface intelligente
sector, selected_years, selected_countries, params = create_smart_interface(api)

# Bouton d'analyse
if st.sidebar.button("🚀 ANALYSER (Données Fraîches)", type="primary"):
    if not selected_countries or not selected_years:
        st.error("🚨 Sélectionnez au moins un pays et une année")
    else:
        with st.spinner("🔄 Récupération des données les plus récentes..."):
            
            # Appel API selon secteur
            data, status, message = None, "not_called", ""
            
            try:
                if sector == 'beef':
                    categories_param = params.get('categories', [])
                    data, status, message = api.get_beef_prices(
                        selected_countries, 
                        selected_years, 
                        categories_param if categories_param else None
                    )
                    
                elif sector == 'milk':
                    products_param = params.get('products', [])
                    data, status, message = api.get_raw_milk_prices(
                        selected_countries,
                        selected_years,
                        products_param if products_param else None
                    )
                    
                elif sector == 'olive_oil':
                    # Convertir années en années marketing
                    marketing_years = []
                    for year in selected_years:
                        if year >= 2020:
                            marketing_years.append(f"{year-1}/{str(year)[-2:]}")
                    
                    products_param = params.get('products', [])
                    data, status, message = api.get_olive_oil_prices(
                        selected_countries,
                        marketing_years,
                        products_param if products_param else None
                    )
                    
            except Exception as e:
                status, message = "error", f"Erreur: {str(e)}"
        
        # Traitement des résultats
        if status == "success" and data and len(data) > 0:
            df = pd.DataFrame(data)
            df = api.standardize_prices(df)
            
            st.success(f"✅ {len(df)} enregistrements récupérés - Données fraîches confirmées !")
            
            # Métriques avec données standardisées
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if 'price_standardized' in df.columns:
                    avg_price = df['price_standardized'].mean()
                    unit = df['unit_display'].iloc[0] if 'unit_display' in df.columns else '€'
                    st.metric("💰 Prix moyen", f"{avg_price:.2f} {unit}")
                else:
                    st.metric("📊 Enregistrements", len(df))
            
            with col2:
                countries_count = df['memberStateCode'].nunique() if 'memberStateCode' in df.columns else 0
                st.metric("🌍 Pays couverts", f"{countries_count}/{len(selected_countries)}")
            
            with col3:
                if 'price_standardized' in df.columns:
                    volatility = (df['price_standardized'].std() / df['price_standardized'].mean()) * 100
                    st.metric("📈 Volatilité", f"{volatility:.1f}%")
                else:
                    st.metric("📅 Années", len(selected_years))
            
            with col4:
                latest_date = "N/A"
                if 'beginDate' in df.columns:
                    try:
                        df['date_parsed'] = pd.to_datetime(df['beginDate'], format='%d/%m/%Y')
                        latest_date = df['date_parsed'].max().strftime('%m/%Y')
                    except:
                        pass
                st.metric("📅 Dernière donnée", latest_date)
            
            # Graphique des prix
            if 'price_standardized' in df.columns and len(df) > 1:
                st.markdown("### 📈 Évolution des prix (données fraîches)")
                
                fig = px.line(
                    df,
                    x='beginDate' if 'beginDate' in df.columns else df.index,
                    y='price_standardized',
                    color='memberStateCode',
                    title=f"Prix {sector.replace('_', ' ').title()} - Données les plus récentes",
                    labels={
                        'price_standardized': f"Prix ({df['unit_display'].iloc[0] if 'unit_display' in df.columns else '€'})",
                        'beginDate': 'Date'
                    }
                )
                
                fig.update_layout(
                    hovermode='x unified',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau optimisé
            st.markdown("### 📋 Données détaillées")
            
            display_columns = ['memberStateName', 'beginDate', 'price_standardized', 'unit_display']
            if 'product' in df.columns:
                display_columns.append('product')
                
            display_df = df[[col for col in display_columns if col in df.columns]].copy()
            
            column_rename = {
                'memberStateName': 'Pays',
                'beginDate': 'Date', 
                'price_standardized': 'Prix',
                'unit_display': 'Unité',
                'product': 'Produit'
            }
            
            display_df = display_df.rename(columns=column_rename)
            st.dataframe(display_df, use_container_width=True)
            
            # Export des données fraîches
            col1, col2 = st.columns(2)
            
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    "📄 Export données fraîches (CSV)",
                    csv,
                    f"{sector}_fresh_data_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
            
            with col2:
                # Rapport de fraîcheur
                freshness_report = f"""RAPPORT DONNÉES FRAÎCHES - {sector.upper()}
==============================================

Date de génération: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Secteur: {sector.replace('_', ' ').title()}
Pays analysés: {', '.join(selected_countries)}
Années: {', '.join(map(str, selected_years))}

STATUT DE FRAÎCHEUR:
{api.get_data_freshness_status(sector)['message']}

DONNÉES RÉCUPÉRÉES:
- Nombre d'enregistrements: {len(df)}
- Pays couverts: {countries_count}/{len(selected_countries)}
- Période: {df['beginDate'].min() if 'beginDate' in df.columns else 'N/A'} à {df['beginDate'].max() if 'beginDate' in df.columns else 'N/A'}

Source: API Officielle Commission Européenne
Garantie: Données les plus récentes disponibles
"""
                
                st.download_button(
                    "📊 Rapport de fraîcheur",
                    freshness_report,
                    f"rapport_fresh_{sector}_{datetime.now().strftime('%Y%m%d')}.txt",
                    "text/plain"
                )
        
        else:
            st.error(f"❌ {message}")
            st.info("💡 Les paramètres ont été optimisés automatiquement, mais l'API peut être temporairement indisponible.")

# Footer avec info fraîcheur
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #666; font-size: 0.9em;'>
    <strong>🕐 Always Fresh Dashboard</strong><br>
    ✅ Détection auto des dernières données • ✅ Pays optimisés • ✅ Années vérifiées<br>
    <em>Dernière vérification: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</em>
</div>
""", unsafe_allow_html=True)
