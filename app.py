"""
Analyseur API Agri-food - Structure complète de chaque endpoint
Analyse systématique pour corriger tous les problèmes identifiés
"""

import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="🔍 Analyseur API Agri-food",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Analyseur API Agri-food - Structure complète")
st.markdown("**Analyse systématique de chaque endpoint pour corriger les problèmes**")

class APIAnalyzer:
    """Analyseur complet des endpoints API"""
    
    def __init__(self):
        self.base_url = "https://www.ec.europa.eu/agrifood/api"
        self.headers = {
            'Accept': 'application/json',
            'User-Agent': 'APIAnalyzer/1.0'
        }
    
    def test_endpoint(self, endpoint, params=None, description=""):
        """Teste un endpoint avec analyse complète"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, params=params, headers=self.headers, timeout=20)
            
            result = {
                'endpoint': endpoint,
                'description': description,
                'url': url,
                'params': params or {},
                'status_code': response.status_code,
                'success': response.status_code == 200,
                'data': None,
                'structure': {},
                'record_count': 0,
                'countries': [],
                'date_range': {},
                'issues': []
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    result['data'] = data
                    result['record_count'] = len(data) if isinstance(data, list) else 1
                    
                    if isinstance(data, list) and len(data) > 0:
                        # Analyser la structure
                        first_record = data[0]
                        result['structure'] = {key: type(value).__name__ for key, value in first_record.items()}
                        
                        # Analyser les pays
                        if 'memberStateCode' in first_record:
                            result['countries'] = list(set([item.get('memberStateCode') for item in data if item.get('memberStateCode')]))
                        
                        # Analyser les dates
                        date_fields = [field for field in first_record.keys() if 'date' in field.lower()]
                        if date_fields:
                            dates = []
                            for item in data:
                                for field in date_fields:
                                    if item.get(field):
                                        dates.append(item[field])
                            if dates:
                                result['date_range'] = {
                                    'min': min(dates),
                                    'max': max(dates),
                                    'count': len(set(dates))
                                }
                        
                        # Détecter les doublons par date/pays
                        if 'memberStateCode' in first_record and date_fields:
                            combinations = []
                            for item in data:
                                key = f"{item.get('memberStateCode')}_{item.get(date_fields[0])}"
                                combinations.append(key)
                            
                            duplicates = len(combinations) - len(set(combinations))
                            if duplicates > 0:
                                result['issues'].append(f"⚠️ {duplicates} doublons détectés (même pays/date)")
                        
                        # Analyser les prix
                        if 'price' in first_record:
                            prices = [item.get('price') for item in data if item.get('price')]
                            price_formats = list(set([str(p) for p in prices[:10]]))
                            result['price_formats'] = price_formats
                            
                            # Détecter problèmes de format prix
                            mixed_formats = any('€' in str(p) for p in prices) and any('€' not in str(p) for p in prices)
                            if mixed_formats:
                                result['issues'].append("⚠️ Formats de prix incohérents")
                
                except json.JSONDecodeError:
                    result['issues'].append("❌ Réponse non-JSON")
            
            else:
                result['issues'].append(f"❌ HTTP {response.status_code}")
                if response.text:
                    result['error_detail'] = response.text[:200]
            
            return result
            
        except Exception as e:
            return {
                'endpoint': endpoint,
                'description': description,
                'success': False,
                'issues': [f"❌ Erreur: {str(e)}"],
                'record_count': 0
            }
    
    def analyze_beef_endpoints(self):
        """Analyse complète des endpoints bœuf"""
        st.subheader("🥩 Analyse des endpoints BŒUF")
        
        endpoints = [
            {
                'endpoint': 'beef/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Prix bœuf carcasses - basique'
            },
            {
                'endpoint': 'beef/prices', 
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023', 'carcassCategories': 'heifers,cows'},
                'description': 'Prix bœuf avec catégories'
            },
            {
                'endpoint': 'beef/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023', 'weeks': '20,21,22'},
                'description': 'Prix bœuf par semaines'
            },
            {
                'endpoint': 'beef/categories',
                'params': {},
                'description': 'Liste des catégories de bœuf'
            },
            {
                'endpoint': 'beef/productCodes',
                'params': {},
                'description': 'Codes produits bœuf'
            },
            {
                'endpoint': 'liveAnimal/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Prix animaux vivants'
            },
            {
                'endpoint': 'liveAnimal/categories',
                'params': {},
                'description': 'Catégories animaux vivants'
            },
            {
                'endpoint': 'beef/production',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Production de bœuf'
            }
        ]
        
        results = []
        for test in endpoints:
            with st.spinner(f"Test {test['endpoint']}..."):
                result = self.test_endpoint(test['endpoint'], test['params'], test['description'])
                results.append(result)
                
                # Affichage immédiat
                if result['success']:
                    st.success(f"✅ {test['endpoint']} - {result['record_count']} enregistrements")
                    if result['countries']:
                        st.write(f"   Pays: {', '.join(result['countries'])}")
                    if result.get('date_range'):
                        st.write(f"   Dates: {result['date_range']['min']} → {result['date_range']['max']}")
                    if result.get('issues'):
                        for issue in result['issues']:
                            st.warning(f"   {issue}")
                else:
                    st.error(f"❌ {test['endpoint']} - {'; '.join(result['issues'])}")
        
        return results
    
    def analyze_milk_endpoints(self):
        """Analyse complète des endpoints lait"""
        st.subheader("🥛 Analyse des endpoints LAIT")
        
        endpoints = [
            {
                'endpoint': 'rawMilk/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Prix lait cru - basique'
            },
            {
                'endpoint': 'rawMilk/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023', 'products': 'raw milk'},
                'description': 'Prix lait cru avec produit'
            },
            {
                'endpoint': 'rawMilk/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023', 'months': '6,7,8'},
                'description': 'Prix lait cru par mois'
            },
            {
                'endpoint': 'rawMilk/products',
                'params': {},
                'description': 'Produits lait cru disponibles'
            },
            {
                'endpoint': 'dairy/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Prix produits laitiers'
            },
            {
                'endpoint': 'dairy/prices',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023', 'products': 'butter,smp'},
                'description': 'Prix laitiers avec produits'
            },
            {
                'endpoint': 'dairy/products',
                'params': {},
                'description': 'Produits laitiers disponibles'
            },
            {
                'endpoint': 'dairy/production',
                'params': {'memberStateCodes': 'PT,DE', 'years': '2023'},
                'description': 'Production laitière'
            }
        ]
        
        results = []
        for test in endpoints:
            with st.spinner(f"Test {test['endpoint']}..."):
                result = self.test_endpoint(test['endpoint'], test['params'], test['description'])
                results.append(result)
                
                if result['success']:
                    st.success(f"✅ {test['endpoint']} - {result['record_count']} enregistrements")
                    if result['countries']:
                        st.write(f"   Pays: {', '.join(result['countries'])}")
                    if result.get('issues'):
                        for issue in result['issues']:
                            st.warning(f"   {issue}")
                else:
                    st.error(f"❌ {test['endpoint']} - {'; '.join(result['issues'])}")
        
        return results
    
    def analyze_olive_oil_endpoints(self):
        """Analyse complète des endpoints huile d'olive"""
        st.subheader("🫒 Analyse des endpoints HUILE D'OLIVE")
        
        endpoints = [
            {
                'endpoint': 'oliveOil/prices',
                'params': {'memberStateCodes': 'ES,IT', 'marketingYears': '2022/2023'},
                'description': 'Prix huile olive - année marketing'
            },
            {
                'endpoint': 'oliveOil/prices',
                'params': {'memberStateCodes': 'ES,IT', 'marketingYears': '2022/2023', 'products': 'Extra virgin olive oil (up to 0.8%)'},
                'description': 'Prix huile avec qualité'
            },
            {
                'endpoint': 'oliveOil/products',
                'params': {},
                'description': 'Qualités huile d\'olive'
            },
            {
                'endpoint': 'oliveOil/markets',
                'params': {},
                'description': 'Marchés huile d\'olive'
            },
            {
                'endpoint': 'oliveOil/memberStates',
                'params': {},
                'description': 'États producteurs huile'
            },
            {
                'endpoint': 'oliveOil/production',
                'params': {'memberStateCodes': 'ES,IT', 'granularity': 'annual', 'productionYears': '2022'},
                'description': 'Production annuelle huile'
            }
        ]
        
        results = []
        for test in endpoints:
            with st.spinner(f"Test {test['endpoint']}..."):
                result = self.test_endpoint(test['endpoint'], test['params'], test['description'])
                results.append(result)
                
                if result['success']:
                    st.success(f"✅ {test['endpoint']} - {result['record_count']} enregistrements")
                    if result['countries']:
                        st.write(f"   Pays: {', '.join(result['countries'])}")
                    if result.get('issues'):
                        for issue in result['issues']:
                            st.warning(f"   {issue}")
                else:
                    st.error(f"❌ {test['endpoint']} - {'; '.join(result['issues'])}")
        
        return results
    
    def analyze_cereals_endpoints(self):
        """Analyse complète des endpoints céréales"""
        st.subheader("🌾 Analyse des endpoints CÉRÉALES")
        
        endpoints = [
            {
                'endpoint': 'cereal/prices',
                'params': {'memberStateCodes': 'PT,FR', 'marketingYears': '2022/2023'},
                'description': 'Prix céréales - année marketing'
            },
            {
                'endpoint': 'cereal/prices',
                'params': {'memberStateCodes': 'PT,FR', 'marketingYears': '2022/2023', 'productCodes': 'BLT,DUR'},
                'description': 'Prix céréales avec codes produits'
            },
            {
                'endpoint': 'cereal/products',
                'params': {},
                'description': 'Produits céréales'
            },
            {
                'endpoint': 'cereal/stages',
                'params': {},
                'description': 'Stades commercialisation'
            },
            {
                'endpoint': 'cereal/markets',
                'params': {},
                'description': 'Marchés céréales'
            },
            {
                'endpoint': 'cereal/production',
                'params': {'memberStateCodes': 'PT,FR', 'years': '2023'},
                'description': 'Production céréales'
            }
        ]
        
        results = []
        for test in endpoints:
            with st.spinner(f"Test {test['endpoint']}..."):
                result = self.test_endpoint(test['endpoint'], test['params'], test['description'])
                results.append(result)
                
                if result['success']:
                    st.success(f"✅ {test['endpoint']} - {result['record_count']} enregistrements")
                    if result['countries']:
                        st.write(f"   Pays: {', '.join(result['countries'])}")
                    if result.get('issues'):
                        for issue in result['issues']:
                            st.warning(f"   {issue}")
                else:
                    st.error(f"❌ {test['endpoint']} - {'; '.join(result['issues'])}")
        
        return results
    
    def generate_recommendations(self, all_results):
        """Génère des recommandations basées sur l'analyse"""
        st.subheader("💡 Recommandations pour corriger les problèmes")
        
        working_endpoints = [r for r in all_results if r['success']]
        failing_endpoints = [r for r in all_results if not r['success']]
        
        st.markdown(f"**📊 Résumé :** {len(working_endpoints)} endpoints fonctionnels, {len(failing_endpoints)} en échec")
        
        # Problème 1: Pays limités
        st.markdown("### 🌍 Problème pays limités")
        
        country_coverage = {}
        for result in working_endpoints:
            if result['countries']:
                for country in result['countries']:
                    if country not in country_coverage:
                        country_coverage[country] = 0
                    country_coverage[country] += 1
        
        if country_coverage:
            sorted_countries = sorted(country_coverage.items(), key=lambda x: x[1], reverse=True)
            st.write("**Pays avec le plus de données :**")
            for country, count in sorted_countries[:10]:
                st.write(f"- {country}: {count} endpoints")
            
            st.code(f"""
# Configuration pays recommandée basée sur analyse
OPTIMAL_COUNTRIES = {{
    'beef': {sorted_countries[:4]},
    'milk': {[c for c, _ in sorted_countries if c in ['DE', 'FR', 'NL', 'IT', 'ES']][:4]},
    'olive_oil': {[c for c, _ in sorted_countries if c in ['ES', 'IT', 'EL', 'PT']][:4]},
    'cereals': {[c for c, _ in sorted_countries if c in ['FR', 'DE', 'PL', 'ES']][:4]}
}}
""")
        
        # Problème 2: Doublons
        st.markdown("### 🔄 Problème doublons")
        
        endpoints_with_duplicates = [r for r in working_endpoints if any('doublons' in issue for issue in r.get('issues', []))]
        
        if endpoints_with_duplicates:
            st.warning(f"⚠️ {len(endpoints_with_duplicates)} endpoints ont des doublons")
            for result in endpoints_with_duplicates:
                st.write(f"- {result['endpoint']}: {[i for i in result['issues'] if 'doublons' in i][0]}")
            
            st.code("""
# Solution pour éliminer doublons
def remove_duplicates(df):
    # Identifier colonnes clés
    key_columns = ['memberStateCode', 'beginDate']
    
    # Garder le premier enregistrement par combinaison
    df_clean = df.drop_duplicates(subset=key_columns, keep='first')
    
    # Ou agreger si plusieurs prix pour même date
    df_aggregated = df.groupby(key_columns).agg({
        'price': 'mean',  # Moyenne des prix
        'unit': 'first',
        'memberStateName': 'first'
    }).reset_index()
    
    return df_clean
""")
        
        # Problème 3: Structure des données
        st.markdown("### 📊 Structure des données")
        
        for result in working_endpoints[:5]:  # Montrer structure des 5 premiers
            if result.get('structure'):
                st.write(f"**{result['endpoint']}:**")
                st.json(result['structure'])
        
        # Recommandations finales
        st.markdown("### 🎯 Plan de correction")
        
        st.markdown("""
        **1. Corriger la sélection des pays :**
        - Utiliser les pays identifiés avec le plus de données
        - Adapter par secteur (ES/IT pour olive oil, DE/FR pour lait)
        
        **2. Éliminer les doublons :**
        - Grouper par pays + date
        - Prendre la moyenne ou le premier enregistrement
        
        **3. Standardiser les paramètres :**
        - Beef: utiliser `carcassCategories` (pas `categories`)
        - Olive oil: `marketingYears` format YYYY/YYYY
        - Cereals: `productCodes` pour filtrer
        
        **4. Gestion des années :**
        - Tester années une par une
        - Olive oil: années marketing décalées
        - Production: souvent année civile simple
        """)

# Interface principale
analyzer = APIAnalyzer()

st.markdown("## 🔍 Analyse complète des endpoints")

# Options d'analyse
analysis_options = st.multiselect(
    "Secteurs à analyser",
    ["🥩 Bœuf", "🥛 Lait", "🫒 Huile d'olive", "🌾 Céréales"],
    default=["🥩 Bœuf", "🥛 Lait"]
)

if st.button("🚀 LANCER L'ANALYSE COMPLÈTE", type="primary"):
    
    all_results = []
    
    if "🥩 Bœuf" in analysis_options:
        beef_results = analyzer.analyze_beef_endpoints()
        all_results.extend(beef_results)
    
    if "🥛 Lait" in analysis_options:
        milk_results = analyzer.analyze_milk_endpoints()
        all_results.extend(milk_results)
    
    if "🫒 Huile d'olive" in analysis_options:
        olive_results = analyzer.analyze_olive_oil_endpoints()
        all_results.extend(olive_results)
    
    if "🌾 Céréales" in analysis_options:
        cereal_results = analyzer.analyze_cereals_endpoints()
        all_results.extend(cereal_results)
    
    # Générer recommandations
    if all_results:
        analyzer.generate_recommendations(all_results)
        
        # Export des résultats
        st.markdown("### 💾 Export de l'analyse")
        
        results_df = pd.DataFrame([
            {
                'Endpoint': r['endpoint'],
                'Description': r['description'],
                'Succès': r['success'],
                'Enregistrements': r['record_count'],
                'Pays': ', '.join(r.get('countries', [])),
                'Problèmes': '; '.join(r.get('issues', []))
            }
            for r in all_results
        ])
        
        st.dataframe(results_df, use_container_width=True)
        
        csv = results_df.to_csv(index=False)
        st.download_button(
            "📄 Télécharger analyse complète",
            csv,
            f"analyse_api_agrifood_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )
