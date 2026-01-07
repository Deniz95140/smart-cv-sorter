import pdfplumber
import re
import os
from fpdf import FPDF

# -------------------------------------------------
# OUTIL : NETTOYAGE PUISSANT (ANTI-CRASH)
# -------------------------------------------------
def sanitize_for_fpdf(text):
    if not text:
        return ""
    
    # 1. Remplacer les caractères "Word" problématiques par du standard
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"', 
        "–": "-", "—": "-", "…": "..."
    }
    for k, v in replacements.items():
        text = text.replace(k, v)

    # 2. La méthode RADICALE : On encode en latin-1 et on ignore les erreurs.
    # Cela supprime automatiquement tous les emojis (🚀, ⚡) et caractères chinois/arabes etc.
    # On décode ensuite pour ravoir une string propre.
    return text.encode('latin-1', 'ignore').decode('latin-1')


# -------------------------------------------------
# EXTRACTION TEXTE PDF
# -------------------------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception:
        return ""
    return text.strip()


# -------------------------------------------------
# CONTACT
# -------------------------------------------------
def extract_contact_info(text):
    email = "Non trouvé"
    phone = "Non trouvé"

    # Regex simple et efficace
    email_match = re.search(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text
    )
    if email_match:
        email = email_match.group(0)

    # Regex téléphone (formats français courants)
    phone_match = re.search(
        r'(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}', text
    )
    if phone_match:
        phone = phone_match.group(0)

    return email, phone


# -------------------------------------------------
# NOM CANDIDAT
# -------------------------------------------------
def extract_name_candidate(text, filename):
    forbidden = {
        "alternant", "developpeur", "developer", "analyste", "engineer",
        "stage", "stagiaire", "intern", "cyber", "securite", "soc",
        "informatique", "data", "software", "curriculum", "vitae"
    }

    # Stratégie 1 : Chercher dans les premières lignes du texte
    if text:
        # On regarde les 10 premières lignes max
        for line in text.split("\n")[:10]:
            clean_line = line.strip()
            words = clean_line.lower().split()
            # Un nom a généralement 2 ou 3 mots, pas de chiffres, et pas de mots interdits
            if 2 <= len(words) <= 3:
                if not any(char.isdigit() for char in clean_line):
                    if not any(w in forbidden for w in words):
                        return clean_line.title()

    # Stratégie 2 : Nom du fichier (Fallback)
    name = os.path.splitext(filename)[0]
    name = name.replace("_", " ").replace("-", " ")
    # Nettoyage des mots clés dans le nom du fichier
    name = re.sub(
        r'\b(cv|curriculum|vitae|resume|profil|candidature)\b',
        '', name, flags=re.IGNORECASE
    ).strip()
    
    return name.title() if name else "Candidat Inconnu"


# -------------------------------------------------
# COMPETENCES
# -------------------------------------------------
def extract_skills(text):
    # Liste de mots-clés (Tu peux en rajouter)
    keywords = [
        "Python", "Java", "SQL", "HTML", "CSS", "React", "Angular", "Vue",
        "Docker", "Kubernetes", "Linux", "Git", "AWS", "Azure",
        "Splunk", "SIEM", "Bash", "Powershell", "C++", "C#",
        "Cybersécurité", "Sysmon", "CrowdSec", "Fail2ban", "Network", "TCP/IP"
    ]

    found = []
    t = text.lower()
    # On cherche les mots entiers pour éviter les faux positifs (ex: "C" dans "Carotte")
    # Note: Pour simplifier ici on fait un check simple, mais on peut utiliser des regex \b
    for k in keywords:
        # Astuce : on met des espaces autour pour éviter de trouver "Java" dans "Javascript" si on veut être strict
        # Mais ici un simple check 'in' suffit pour commencer
        if k.lower() in t:
            found.append(k)

    # On retire les doublons éventuels et on formatte
    return ", ".join(sorted(list(set(found)))) if found else "Non détectées"


# -------------------------------------------------
# PDF FINAL (ROBUSTE)
# -------------------------------------------------
def create_pdf_report(df, job_desc):
    try:
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 16)
                self.cell(0, 10, "Rapport de Recrutement", 0, 1, "C")
                self.set_font("Arial", "I", 10)
                self.cell(0, 10, "Généré par Smart CV Sorter", 0, 1, "C")
                self.ln(5)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f"Page {self.page_no()}", 0, 0, "C")

        pdf = PDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # CONTEXTE (Description du poste)
        pdf.set_font("Arial", "B", 12)
        # Couleur gris clair pour le fond
        pdf.set_fill_color(240, 240, 240) 
        pdf.cell(0, 10, "Contexte du Poste", 0, 1, fill=True)
        
        pdf.set_font("Arial", size=10)
        # On nettoie la description (enlève les emojis 🚀 etc)
        clean_desc = sanitize_for_fpdf(job_desc)
        # On coupe si c'est trop long pour éviter de prendre 3 pages
        pdf.multi_cell(0, 5, clean_desc[:800] + ("..." if len(clean_desc)>800 else ""))
        pdf.ln(8)

        if len(df) == 0:
            return None

        # TOP CANDIDAT
        best = df.iloc[0]
        pdf.set_font("Arial", "B", 12)
        # Couleur vert clair
        pdf.set_fill_color(220, 255, 220)
        pdf.cell(
            0, 10,
            f"PROFIL RECOMMANDE : {sanitize_for_fpdf(best['Candidat'])}",
            0, 1, fill=True
        )
        pdf.set_font("Arial", "I", 10)
        pdf.cell(0, 8, f"Score de pertinence : {best['Score']:.2f}%", 0, 1)
        pdf.ln(5)

        # TABLEAU DES CANDIDATS
        pdf.set_font("Arial", "B", 12)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(0, 10, "Détails des Candidatures", 0, 1, fill=True)
        pdf.ln(2)

        for i, row in enumerate(df.itertuples(), start=1):
            # Ligne Nom + Score
            pdf.set_font("Arial", "B", 11)
            pdf.cell(
                0, 8,
                f"{i}. {sanitize_for_fpdf(row.Candidat)}  ({row.Score:.2f}%)",
                0, 1
            )
            
            # Détails (Email, Tel, Skills)
            pdf.set_font("Arial", size=9)
            # Indentation légère
            pdf.set_x(15) 
            pdf.cell(0, 5, f"Contact : {sanitize_for_fpdf(row.Email)} | {sanitize_for_fpdf(str(row.Téléphone))}", 0, 1)
            
            pdf.set_x(15)
            # Multi_cell pour les skills car ça peut être long
            pdf.multi_cell(0, 5, f"Skills : {sanitize_for_fpdf(row.Compétences)}")
            
            # Petit trait de séparation
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(2)

        # On retourne les bytes en latin-1 (ignore les erreurs d'encodage restantes)
        return pdf.output(dest="S").encode("latin-1", "ignore")

    except Exception as e:
        print(f"Erreur PDF : {e}")
        return None