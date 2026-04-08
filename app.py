from flask import Flask, render_template, request, jsonify
import PyPDF2
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def nettoyer_texte(texte):
    if not texte:
        return ""
    
    # 1. Remplacer les retours à la ligne par des espaces
    texte = texte.replace('\n', ' ')
    
    # 2. Supprimer les numéros de page isolés (ex: " 12 ", " Page 12 ")
    # Cette regex cherche des chiffres entourés d'espaces ou en début de ligne
    texte = re.sub(r'\b\d+\b', '', texte)
    
    # 3. Supprimer les espaces multiples créés par le nettoyage
    texte = re.sub(r'\s+', ' ', texte).strip()
    
    return texte

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier"})
    file = request.files['file']
    if file:
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        pages_data = []
        try:
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    t = page.extract_text()
                    # On applique le nettoyage ici !
                    t_propre = nettoyer_texte(t)
                    
                    if t_propre:
                        pages_data.append({"num": i + 1, "texte": t_propre})
            
            return jsonify({
                "pdf_url": f"/static/uploads/{file.filename}",
                "pages": pages_data
            })
        except Exception as e:
            return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)