# The Forest Fools - Roadmap

Objectif final : transformer le jeu terminal actuel en jeu Python avec interface graphique, menu principal, intro avec pixel art/musique, terminal integre, sauvegarde, puis build final en `.exe`.

## Phase 1 - Nettoyage du projet

- [x] Ajouter un `.gitignore`.
- [x] Ignorer ou supprimer les fichiers `__pycache__`.
- [x] Clarifier les fichiers utiles du projet.
- [x] Ajouter un `README.md` simple.
- [x] Decider quoi faire des fichiers backup (`gamebackup.py`, `game_old_backup.py`).

## Phase 2 - Preparation du moteur

- [x] Definir la direction : interface passive, terminal central actif.
- [x] Garder les commandes existantes comme seule source de controle.
- [x] Ajouter `process_command()` pour envoyer une commande au moteur et recuperer les messages.
- [x] Ajouter un historique de messages pour le futur terminal graphique.
- [x] Ajouter `get_ui_state()` pour exposer les panneaux passifs :
  - [x] joueur / stats / equipement
  - [x] carte
  - [x] contexte actuel
  - [x] combat actuel
- [x] Transformer le combat en rencontre active controlee par commandes.
- [x] Supprimer le blocage du combat par `input()` cache.
- [x] Garder le contenu existant dans `data/`.

## Phase 3 - Interface Pygame

- [x] Creer une fenetre de jeu.
- [x] Ajouter un menu principal controle au clavier.
- [x] Ajouter les options de menu :
  - [x] `New Game`
  - [x] `Continue` placeholder jusqu'a la Phase 6
  - [x] `Options` placeholder jusqu'au polish
  - [x] `Quit`
- [x] Creer l'interface principale selon le dessin :
  - [x] Panneau gauche : joueur, equipement, stats.
  - [x] Panneau central : terminal de commandes.
  - [x] Panneau droit haut : carte du monde.
  - [x] Panneau droit bas : infos contexte / combat.
- [x] Ajouter une zone de saisie pour taper les commandes.
- [x] Afficher les reponses du jeu dans le terminal graphique.
- [x] Garder les panneaux non interactifs : seul le terminal central controle le jeu.

## Phase 4 - Intro cinematique

- [x] Lancer l'intro apres `New Game`.
- [x] Ajouter placeholders pixel art tant que les vrais assets ne sont pas prets.
- [x] Charger automatiquement les pixel arts du dossier `assets/images/intro/` si presents.
- [x] Supporter les animations par frames separees (`_000`, `_001`, etc.).
- [x] Ajouter texte avec apparition progressive.
- [x] Ajouter support musique d'ambiance `assets/music/intro.ogg`.
- [x] Permettre de passer l'intro avec une touche.
- [x] Faire une transition vers l'interface principale.
- [x] Documenter les formats dans `ASSET_GUIDE.md`.

## Phase 4.5 - Creation de personnage

- [x] Ajouter un ecran apres l'intro avant le debut du jeu.
- [x] Garder le controle 100% clavier.
- [x] Ajouter choix de race : `Human`, `Elf`, `Lizardfolk`.
- [x] Ajouter choix de genre : `Male`, `Female`.
- [x] Ajouter choix de classe : `Warrior`, `Mage`.
- [x] Appliquer les bonus au joueur :
  - [x] mage : plus de mana et de puissance magique, moins de melee
  - [x] guerrier : plus de melee et de resistance
- [x] Afficher les deux versions homme/femme de la race choisie.
- [x] Mettre un glow sur le personnage selectionne.
- [x] Documenter les PNG attendus pour les personnages.

## Phase 5 - Assets

- [x] Creer les dossiers :
  - [x] `assets/images/`
  - [x] `assets/music/`
  - [x] `assets/sounds/`
  - [x] `assets/ui/`
  - [x] `assets/images/character_select/`
  - [x] `assets/images/characters/`
- [ ] Ajouter les pixel arts.
- [ ] Ajouter les musiques.
- [ ] Ajouter des sons optionnels : clic, combat, achat, mort, victoire.
- [ ] Ajouter une icone pour le `.exe`.

## Phase 5.5 - Cartes fixes et progression

- [x] Remplacer le monde genere aleatoirement par des cartes fixes.
- [x] Ajouter `Mosswake Isle` comme ile de tutoriel.
- [x] Ajouter un village, une mairie, une foret, Slime Hollow et un port sur l'ile.
- [x] Rendre Slime Hollow revelable par le maire seulement apres le niveau 2.
- [x] Ajouter le maire et le `Harbor Pass`.
- [x] Bloquer le depart de l'ile tant que le Slime King n'est pas vaincu.
- [x] Ajouter la commande `sail`.
- [x] Ajouter `Mainland of Elarion` comme continent.
- [x] Garder l'ile en grille 10x10.
- [x] Garder le continent comme vue globale sans grille jouable.
- [x] Ajouter les regions jouables en grilles 26x26.
- [x] Diviser le continent en 4 regions : Crownvale, Greenmarch, Scalefen, Ashenreach.
- [x] Ajouter la commande `zoom` pour voir l'ile, le continent ou une region.
- [x] Ajouter `cd {region}` avec verification du pass regional.
- [x] Cacher les symboles des lieux tant qu'ils ne sont pas visites ou reveles.
- [x] Ajouter quadrillage et case joueur clignotante sur les cartes pixel art.
- [x] Preparer `assets/images/maps/` pour les pixel arts de cartes.
- [ ] Ajouter les vraies images pixel art des cartes.
- [x] Ecrire les missions des seigneurs pour debloquer les autres regions.
- [x] Crownvale : vaincre le Hollow Baron pour obtenir le Greenmarch Pass.
- [x] Greenmarch : vaincre le Thornwell Warden pour obtenir le Scalefen Pass.
- [x] Scalefen : vaincre la Mirejaw Matriarch pour obtenir le Ashenreach Pass.
- [x] Ashenreach : reveler la piste finale vers le Dragon Lair.

## Phase 6 - Sauvegarde

- [ ] Ajouter `New Game`.
- [ ] Ajouter `Save Game`.
- [ ] Ajouter `Continue` / chargement de partie.
- [ ] Sauvegarder l'etat du joueur.
- [ ] Sauvegarder la position.
- [ ] Sauvegarder la carte.
- [ ] Sauvegarder l'inventaire.
- [ ] Sauvegarder l'etat de la quete du dragon.
- [ ] Sauvegarder les ennemis/loots deja nettoyes.
- [ ] Ajouter une sauvegarde automatique optionnelle.

## Phase 7 - Gameplay a finir

- [ ] Ameliorer la quete principale.
- [ ] Ajouter un vrai ecran de victoire apres le dragon.
- [ ] Ajouter le retour au roi apres victoire.
- [ ] Equilibrer ennemis, or, XP et objets.
- [ ] Ajouter plus de dialogues.
- [ ] Utiliser la zone libre pour journal, quetes, inventaire rapide ou evenements.

## Phase 8 - Polish

- [ ] Ameliorer les couleurs et bordures.
- [ ] Ajouter animations simples.
- [ ] Ajouter options audio.
- [ ] Ajouter mode plein ecran / fenetre.
- [ ] Ajouter raccourcis clavier.
- [ ] Rendre l'interface lisible sur plusieurs tailles d'ecran.

## Phase 9 - Build `.exe`

- [ ] Configurer PyInstaller.
- [ ] Inclure les fichiers Python.
- [ ] Inclure les assets.
- [ ] Inclure les fonts.
- [ ] Inclure l'icone.
- [ ] Generer `dist/TheForestFools.exe`.
- [ ] Tester l'executable sur le PC.
- [ ] Corriger les chemins d'assets si besoin.
- [ ] Preparer une version finale partageable.

## Notes de direction

- Le projet reste en Python.
- L'interface graphique sera faite avec Pygame.
- L'interface est passive : seul le terminal central controle le jeu.
- Le joueur tape toujours les commandes existantes.
- Les pixel arts seront fournis separement.
- L'objectif est de garder le moteur existant et de construire une interface autour, pas de tout recommencer.
