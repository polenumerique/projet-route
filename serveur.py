#!/usr/bin/env python3
"""
Petit serveur local pour lancer Asphalte Libre.

Nécessaire pour trois raisons :
- le jeu charge carte.json avec fetch(), ce que les navigateurs interdisent
  quand la page est ouverte directement en double-cliquant (file://) ;
- editeur_jeu.html a besoin de lister, renommer, dupliquer et supprimer des
  fichiers dans modeles/, ce qu'une page web ne peut pas faire seule : ce
  script expose une petite API pour ça (voir API_ROOTS ci-dessous), limitée
  aux dossiers modeles/batiments, modeles/decors et modeles/vehicules ;
- le jeu lit aussi cette API au démarrage pour appliquer automatiquement les
  véhicules personnalisés présents dans modeles/vehicules.

Utilisation :
  Windows : double-clique sur serveur.py (si Python est associé aux .py),
            ou ouvre une invite de commandes dans ce dossier et tape :
              python serveur.py
  Linux/macOS : ouvre un terminal dans ce dossier et tape :
              python3 serveur.py

Le script ouvre ensuite automatiquement le jeu dans le navigateur par
défaut, à l'adresse http://localhost:8000/index.html
Pour arrêter le serveur : Ctrl+C dans la fenêtre du terminal.
"""
import http.server
import json
import os
import re
import shutil
import socket
import sys
import threading
import webbrowser

PORT = 8000
PAGE = 'index.html'

# catégories exposées à l'API de gestion des modèles (voir editeur_jeu.html) ;
# le jeu (index.html) lit aussi 'vehicules' au démarrage pour appliquer les
# habillages de véhicules personnalisés (voir loadVehicleOverrides côté jeu)
API_ROOTS = {
    'batiments': 'modeles/batiments',
    'decors': 'modeles/decors',
    'vehicules': 'modeles/vehicules',
}
NAME_RE = re.compile(r'^[a-zA-Z0-9_\-]+\.json$')


def port_disponible(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0


def choisir_port(depart):
    port = depart
    while not port_disponible(port) and port < depart + 20:
        port += 1
    return port


def safe_path(cat, name):
    """Résout un (catégorie, nom de fichier) vers un chemin sûr dans modeles/,
    ou None si la catégorie est inconnue ou le nom de fichier suspect
    (pas de .. , pas de séparateur de dossier, extension .json obligatoire)."""
    root = API_ROOTS.get(cat)
    if root is None or not NAME_RE.match(name or ''):
        return None
    return os.path.join(root, name)


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, '.json': 'application/json'}

    def _json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get('Content-Length', 0) or 0)
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode('utf-8'))

    def do_GET(self):
        if self.path.startswith('/api/modeles'):
            return self.list_models()
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/modeles/renommer':
            return self.rename_model()
        if self.path == '/api/modeles/dupliquer':
            return self.duplicate_model()
        if self.path == '/api/modeles/supprimer':
            return self.delete_model()
        if self.path == '/api/modeles/enregistrer':
            return self.save_model()
        if self.path == '/api/carte/enregistrer':
            return self.save_carte()
        self.send_error(404)

    def list_models(self):
        out = {}
        for cat, root in API_ROOTS.items():
            items = []
            if os.path.isdir(root):
                for fn in sorted(os.listdir(root)):
                    if not fn.endswith('.json'):
                        continue
                    fp = os.path.join(root, fn)
                    entry = {'file': fn, 'size': os.path.getsize(fp), 'mtime': os.path.getmtime(fp)}
                    try:
                        with open(fp, encoding='utf-8') as f:
                            data = json.load(f)
                        entry['name'] = data.get('name', fn)
                        entry['kind'] = data.get('kind', '?')
                        entry['parts'] = len(data.get('parts', []))
                    except Exception as e:
                        entry['error'] = str(e)
                    items.append(entry)
            out[cat] = items
        self._json(200, out)

    def rename_model(self):
        try:
            body = self._read_json_body()
            src = safe_path(body.get('cat'), body.get('name'))
            dst = safe_path(body.get('cat'), body.get('newName'))
            if not src or not dst or not os.path.isfile(src):
                return self._json(400, {'error': 'Requête invalide ou fichier introuvable'})
            if os.path.exists(dst):
                return self._json(409, {'error': 'Un fichier porte déjà ce nom'})
            os.rename(src, dst)
            self._json(200, {'ok': True})
        except Exception as e:
            self._json(500, {'error': str(e)})

    def duplicate_model(self):
        try:
            body = self._read_json_body()
            src = safe_path(body.get('cat'), body.get('name'))
            dst = safe_path(body.get('cat'), body.get('newName'))
            if not src or not dst or not os.path.isfile(src):
                return self._json(400, {'error': 'Requête invalide ou fichier introuvable'})
            if os.path.exists(dst):
                return self._json(409, {'error': 'Un fichier porte déjà ce nom'})
            shutil.copyfile(src, dst)
            self._json(200, {'ok': True})
        except Exception as e:
            self._json(500, {'error': str(e)})

    def save_model(self):
        try:
            body = self._read_json_body()
            dst = safe_path(body.get('cat'), body.get('name'))
            data = body.get('data')
            if not dst or data is None:
                return self._json(400, {'error': 'Requête invalide'})
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            with open(dst, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=1)
            self._json(200, {'ok': True})
        except Exception as e:
            self._json(500, {'error': str(e)})

    def save_carte(self):
        try:
            body = self._read_json_body()
            with open('carte.json', 'w', encoding='utf-8') as f:
                json.dump(body, f, ensure_ascii=False, indent=1)
            self._json(200, {'ok': True})
        except Exception as e:
            self._json(500, {'error': str(e)})

    def delete_model(self):
        try:
            body = self._read_json_body()
            src = safe_path(body.get('cat'), body.get('name'))
            if not src or not os.path.isfile(src):
                return self._json(400, {'error': 'Requête invalide ou fichier introuvable'})
            os.remove(src)
            self._json(200, {'ok': True})
        except Exception as e:
            self._json(500, {'error': str(e)})

    def log_message(self, fmt, *args):
        if not self.path.startswith('/api/'):
            return  # ne pas polluer la console pour les fichiers statiques
        super().log_message(fmt, *args)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = choisir_port(PORT)

    with http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler) as httpd:
        url = f'http://localhost:{port}/{PAGE}'
        print('=' * 60)
        print(' Asphalte Libre — serveur local')
        print('=' * 60)
        print(f' Jeu disponible sur : {url}')
        print(' (editeur_jeu.html (carte / bâtiments / véhicules / décors)')
        print('  est aussi accessible depuis http://localhost:%d/)' % port)
        print()
        print(' Ctrl+C pour arrêter le serveur.')
        print('=' * 60)

        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print('\nArrêt du serveur.')
            sys.exit(0)


if __name__ == '__main__':
    main()
