import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import streamlit as st
import pandas as pd
import altair as alt
from utils import extract_text_from_pdf, extract_contact_info, extract_name_candidate, extract_skills, create_pdf_report
from model import calculate_similarity

# --- CONFIGURATION ---
st.set_page_config(page_title="Smart CV Sorter", layout="wide", page_icon="⚡")

# --- STYLE CSS (LE RETOUR DU DARK MODE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* FOND ANIMÉ DARK */
    .stApp {
        background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #e0e0e0;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* BARRE LATÉRALE (GLASSMORPHISM) */
    section[data-testid="stSidebar"] {
        background-color: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* CARTES STATS */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
    }

    /* TITRE PRINCIPAL */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#ffffff, #a5a5a5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    /* CARTE DU MEILLEUR PROFIL */
    .winner-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 25px;
    }
    .winner-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
    }
    .winner-score {
        font-size: 1.2rem;
        background-color: rgba(0,0,0,0.3);
        padding: 5px 12px;
        border-radius: 20px;
        color: #00ffcc;
        font-weight: bold;
        margin-left: 10px;
    }

    /* BOUTON PRINCIPAL */
    .stButton>button {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 8px;
        padding: 12px 25px;
        font-weight: 600;
        letter-spacing: 0.5px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_1, col_2 = st.columns([0.5, 4])
with col_2:
    st.markdown('<h1 class="main-title">Smart CV Sorter</h1>', unsafe_allow_html=True)
    st.markdown("Système d'analyse sémantique & extraction de compétences.")

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Configuration")
    job_description = st.text_area("Description du Poste", height=250, placeholder="Collez l'offre ici...")
    uploaded_files = st.file_uploader("Dossier Candidats (PDF)", type=["pdf"], accept_multiple_files=True)

# --- TRAITEMENT ---
if uploaded_files and job_description:
    
    if st.button("Lancer l'analyse", use_container_width=True):
        
        progress_text = "Analyse en cours..."
        my_bar = st.progress(0, text=progress_text)
        results = []
        
        for i, file in enumerate(uploaded_files):
            text = extract_text_from_pdf(file)
            
            # Extraction infos
            name = extract_name_candidate(text, file.name)
            email, phone = extract_contact_info(text)
            skills = extract_skills(text)
            
            # IA
            if text:
                score = float(calculate_similarity(text, job_description))
            else:
                score = 0.0
                
            results.append({
                "Candidat": name,
                "Score": score,
                "Email": email,
                "Téléphone": phone,
                "Compétences": skills,
                "Fichier": file.name
            })
            my_bar.progress((i + 1) / len(uploaded_files), text=progress_text)
            
        my_bar.empty()
        
        # DataFrame
        df = pd.DataFrame(results)
        df = df.sort_values(by="Score", ascending=False)
        best_candidate = df.iloc[0]
        
        # --- RÉSULTAT GAGNANT (CARTE TECH) ---
        st.markdown(f"""
        <div class="winner-card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="color:rgba(255,255,255,0.7); font-size:0.9rem; text-transform:uppercase; letter-spacing:1px;">Profil le plus pertinent</div>
                    <div class="winner-name">{best_candidate['Candidat']}</div>
                </div>
                <div class="winner-score">{best_candidate['Score']:.2f}% Match</div>
            </div>
            <div style="margin-top:15px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px; font-size:0.95rem;">
                📧 {best_candidate['Email']} &nbsp;&nbsp;|&nbsp;&nbsp; 📱 {best_candidate['Téléphone']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- BOUTON PDF & STATS ---
        col_metrics, col_chart = st.columns([1, 2])
        
        with col_metrics:
            st.markdown("#### Synthèse")
            st.metric("Candidats", len(df))
            st.metric("Score Moyen", f"{df['Score'].mean():.2f}%")
            
            st.markdown("#### Export")
            try:
                pdf_bytes = create_pdf_report(df, job_description)

                if pdf_bytes:
                    st.download_button(
                        label="Télécharger le rapport PDF",
                        data=pdf_bytes,
                        file_name="rapport_analyse.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.error("Impossible de générer le PDF")
            except Exception as e:
                st.error("Erreur PDF")

        with col_chart:
            st.markdown("#### Distribution")
            chart = alt.Chart(df).mark_bar(cornerRadius=4).encode(
                x=alt.X('Candidat', sort='-y'),
                y='Score',
                color=alt.Color('Score', scale=alt.Scale(scheme='viridis'), legend=None),
                tooltip=['Candidat', 'Score', 'Compétences']
            ).properties(height=320)
            st.altair_chart(chart, use_container_width=True)

        # --- TABLEAU COMPLET ---
        st.markdown("#### Détails des candidatures")
        st.data_editor(
            df[['Candidat', 'Score', 'Email', 'Téléphone', 'Compétences']],
            column_config={
                "Score": st.column_config.ProgressColumn(format="%.2f %%", min_value=0, max_value=100),
                "Compétences": st.column_config.TextColumn(width="large"),
            },
            hide_index=True,
            use_container_width=True
        )

elif not uploaded_files:
    st.info("En attente de documents...")