import pandas as pd
import chardet
import os

def analyze_file_encoding(file_path):
    """Analyse l'encodage d'un fichier"""
    print(f"=== ANALYSE DU FICHIER : {file_path} ===")
    
    # Lire le fichier en bytes
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    
    # Détecter l'encodage
    result = chardet.detect(raw_data)
    print(f"Encodage détecté : {result}")
    
    # Essayer de lire avec pandas
    try:
        if file_path.endswith('.xlsx'):
            df = pd.read_excel(file_path)
            print("✅ Fichier Excel lu avec succès")
            print(f"Dimensions : {df.shape}")
            print(f"Colonnes : {list(df.columns)}")
        else:
            df = pd.read_csv(file_path)
            print("✅ Fichier CSV lu avec succès")
            print(f"Dimensions : {df.shape}")
            print(f"Colonnes : {list(df.columns)}")
    except Exception as e:
        print(f"❌ Erreur lors de la lecture : {e}")
    
    print("\n" + "="*50)

# Exemple d'utilisation
if __name__ == "__main__":
    # Remplacez par le chemin de votre fichier
    file_path = "votre_fichier.xlsx"
    
    if os.path.exists(file_path):
        analyze_file_encoding(file_path)
    else:
        print(f"Fichier {file_path} non trouvé")
        print("Modifiez le chemin dans le script") 