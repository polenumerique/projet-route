# projet-route
test IA for GTA like game

## Lancer le jeu

Le jeu (`index.html`) n'a plus de génération procédurale : toute la carte (routes,
portes, parkings, zones piétonnes, bâtiments, décors) vient d'un fichier
`carte.json` que tu construis toi-même, et les véhicules peuvent être
personnalisés via `modeles/vehicules/`. Sans `carte.json`, le jeu refuse de
démarrer et affiche comment en créer un.

1. Lance `serveur.py` (`python serveur.py` sous Windows, `python3 serveur.py`
   sous Linux/macOS) — il ouvre le jeu dans le navigateur et démarre l'API
   locale dont l'éditeur a besoin pour lire/écrire tes fichiers. Un simple
   double-clic sur `index.html` ne suffit pas : ni `carte.json` ni les
   modèles ne peuvent se charger sans serveur local.
2. Ouvre `editeur_jeu.html` (accessible depuis la même adresse que le jeu) :
   - **Bâtiments** / **Décors** / **Véhicules** : assemble des modèles à
     partir de primitives (blocs, cylindres, sphères, toits) et enregistre-les
     directement dans `modeles/`. Un véhicule cible un type existant du jeu
     (berline, camion, moto…) : le jeu remplace sa carrosserie tout en
     gardant les roues, la physique et les statistiques de ce type.
   - **Carte** : place le point de départ, dessine les routes, les portes
     (planque, magasins, garage, hôpital…), les parkings et les zones de
     flânerie piétonne, pioche tes bâtiments/décors dans la bibliothèque,
     puis clique **Enregistrer carte.json**.
3. Recharge `index.html` pour voir les changements (les véhicules personnalisés
   et `carte.json` sont chargés au démarrage).

Des modèles de départ sont fournis dans `modeles/batiments/`, `modeles/decors/`
et `modeles/vehicules/`, et `carte.json` contient une petite carte de démo.
