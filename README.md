# projet-route
test IA for GTA like game

## Lancer le jeu

Le jeu (`index.html`) n'a plus de génération procédurale : toute la carte (routes,
portes, parkings, zones piétonnes, bâtiments, décors) vient d'un fichier
`carte.json` que tu construis toi-même. Sans ce fichier, le jeu refuse de
démarrer et affiche comment en créer un.

1. Ouvre `editeur_batiments_3d.html` / `editeur_decors_3d.html` pour créer ou
   adapter des modèles (des exemples sont dans `modeles/batiments/` et
   `modeles/decors/`), et exporte-les en `.json`.
2. Ouvre `editeur_carte_3d.html` : place le point de départ, dessine les
   routes, les portes (planque, magasins, garage, hôpital…), les parkings et
   les zones de flânerie piétonne, importe et place tes bâtiments/décors,
   puis clique **Exporter carte.json**.
3. Place ce `carte.json` dans le même dossier que `index.html`.
4. Lance `serveur.py` (`python serveur.py` sous Windows, `python3 serveur.py`
   sous Linux/macOS) — il ouvre le jeu dans le navigateur. Un simple
   double-clic sur `index.html` ne suffit pas : le chargement de `carte.json`
   nécessite un serveur local.
