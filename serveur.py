#!/usr/bin/env python3
"""
Petit serveur local pour lancer Asphalte Libre.

Nécessaire car le jeu charge carte.json avec fetch(), ce que les
navigateurs interdisent quand la page est ouverte directement en
double-cliquant (file://). En servant le dossier en http://, le
chargement de la carte fonctionne normalement.

Utilisation :
  Windows : double-clique sur serveur.py (si Python est associé aux .py),
            ou ouvre une invite de commandes dans ce dossier et tape :
              python serveur.py
  Linux/macOS : ouvre un terminal dans ce dossier et tape :
              python3 serveur.py

Le script ouvre ensuite automatiquement le jeu dans le navigateur par
défaut, à l'adresse http://localhost:8000/bulle_de_route.html
Pour arrêter le serveur : Ctrl+C dans la fenêtre du terminal.
"""
import http.server
import os
import socket
import sys
import threading
import webbrowser

PORT = 8000
PAGE = 'bulle_de_route.html'


def port_disponible(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) != 0


def choisir_port(depart):
    port = depart
    while not port_disponible(port) and port < depart + 20:
        port += 1
    return port


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = choisir_port(PORT)

    handler = http.server.SimpleHTTPRequestHandler
    handler.extensions_map.setdefault('.json', 'application/json')

    with http.server.ThreadingHTTPServer(('127.0.0.1', port), handler) as httpd:
        url = f'http://localhost:{port}/{PAGE}'
        print('=' * 60)
        print(' Asphalte Libre — serveur local')
        print('=' * 60)
        print(f' Jeu disponible sur : {url}')
        print(' (les éditeurs .html du dossier sont aussi accessibles')
        print('  depuis http://localhost:%d/)' % port)
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
