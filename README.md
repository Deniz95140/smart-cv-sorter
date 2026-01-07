# Smart CV Sorter

Smart CV Sorter est une application d’analyse intelligente de CV basée sur le Machine Learning et le NLP.  
Elle permet de comparer automatiquement des candidatures à une offre d’emploi et de produire un classement pertinent, lisible et exploitable dans un contexte de recrutement.

Le projet combine des modèles de Deep Learning pré‑entraînés avec des règles NLP afin d’extraire des informations clés et de mesurer la similarité sémantique entre un CV et une offre.

---

## Fonctionnalités

- Import de plusieurs CV au format PDF  
- Analyse sémantique CV ↔ offre d’emploi  
- Scoring automatique de pertinence  
- Classement des candidats par score  
- Extraction automatique :
  - Nom et prénom
  - Email
  - Téléphone
  - Compétences techniques
- Visualisation des résultats (tableaux et graphiques)
- Génération d’un rapport PDF professionnel
- Interface moderne développée avec Streamlit

---

## Approche Machine Learning

Le cœur du système repose sur :
- Un modèle Sentence Transformer (`all-MiniLM-L6-v2`)
- La génération d’embeddings sémantiques pour les textes
- Le calcul de similarité cosinus entre CV et offre d’emploi
- Un pipeline NLP comprenant :
  - extraction de texte PDF
  - nettoyage minimal des données
  - extraction de caractéristiques métiers

Il s’agit d’un projet de Machine Learning en inférence, basé sur un modèle de Deep Learning pré‑entraîné.  
Le projet est conçu pour être étendu vers un entraînement supervisé spécifique.

---

## Stack technique

- Python 3.10+
- Streamlit
- Sentence-Transformers
- Scikit-learn
- Pandas
- Altair
- pdfplumber
- FPDF

---

## Structure du projet

smart-cv-sorter/
- app.py            Interface Streamlit
- model.py          Logique ML et similarité sémantique
- utils.py          Extraction PDF, NLP et génération du PDF
- requirements.txt  Dépendances Python
- README.md         Documentation

---

## Lancer le projet en local

1. Cloner le dépôt :
   git clone https://github.com/<username>/smart-cv-sorter.git
   cd smart-cv-sorter

2. Installer les dépendances :
   pip install -r requirements.txt

3. Lancer l’application :
   streamlit run app.py

---

## Objectif du projet

Ce projet a été conçu comme :
- un support technique pour entretien ou soutenance
- une base solide pour un futur modèle ML entraîné

---


## Auteur

Deniz Yuker
