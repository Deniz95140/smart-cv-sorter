from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st

@st.cache_resource
def load_model():
    """
    Charge le modèle Sentence-Transformer.
    On utilise @st.cache_resource pour ne le charger qu'une seule fois
    au démarrage (sinon l'app serait lente à chaque clic).
    """
    # 'all-MiniLM-L6-v2' est un modèle très rapide et performant pour la similarité
    model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

def calculate_similarity(text_cv, text_job):
    """
    Calcule le score de similarité (0 à 100%) entre le CV et l'offre.
    """
    model = load_model()
    
    # 1. On transforme les textes en vecteurs (listes de nombres)
    # On met tout dans une liste car le modèle attend une liste de phrases
    embeddings = model.encode([text_cv, text_job])
    
    # 2. On récupère les deux vecteurs
    vector_cv = embeddings[0].reshape(1, -1)
    vector_job = embeddings[1].reshape(1, -1)
    
    # 3. Calcul de la similarité cosinus
    # Le résultat est une matrice [[score]], on prend la valeur [0][0]
    score = cosine_similarity(vector_cv, vector_job)[0][0]
    
    # On retourne un pourcentage arrondi
    return round(score * 100, 2)