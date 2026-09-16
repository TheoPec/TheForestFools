# The Forest Fools

The Forest Fools est un jeu d'exploration dark medieval/gothic en Python.

Le projet actuel est une version terminal : le joueur tape des commandes pour explorer une carte, parler aux PNJ, acheter de l'equipement, combattre des ennemis, trouver du loot et affronter le dragon final.

## Lancer le jeu

Version interface Pygame :

```powershell
python pygame_app.py
```

Version terminal historique :

```powershell
python game.py
```

## Assets

Les formats pour les pixel arts, animations, musiques et sons sont documentes dans `ASSET_GUIDE.md`.

Le jeu cherche deja les fichiers suivants si tu les ajoutes :

- `assets/images/menu/menu_bg.png` ou `menu_bg_000.png`, `menu_bg_001.png`, etc.
- `assets/images/intro/01_valley.png`
- `assets/images/intro/02_burning_road.png`
- `assets/images/intro/03_silent_towers.png`
- `assets/images/intro/04_council.png`
- `assets/images/intro/05_forest_fools.png`
- `assets/images/character_select/background.png`
- `assets/images/characters/human_male.png`
- `assets/images/characters/human_female.png`
- `assets/images/characters/elf_male.png`
- `assets/images/characters/elf_female.png`
- `assets/images/characters/lizardfolk_male.png`
- `assets/images/characters/lizardfolk_female.png`
- `assets/images/characters/human_female_warrior.png`
- `assets/images/characters/human_female_mage.png`
- `assets/images/characters/human_male_warrior.png`
- `assets/images/characters/human_male_mage.png`
- `assets/images/characters/elf_female_warrior.png`
- `assets/images/characters/elf_female_mage.png`
- `assets/images/characters/elf_male_warrior.png`
- `assets/images/characters/elf_male_mage.png`
- `assets/images/characters/lizardfolk_female_warrior.png`
- `assets/images/characters/lizardfolk_female_mage.png`
- `assets/images/characters/lizardfolk_male_warrior.png`
- `assets/images/characters/lizardfolk_male_mage.png`
- `assets/images/maps/mosswake.png`
- `assets/images/maps/continent.png`
- `assets/images/maps/crownvale.png`
- `assets/images/maps/greenmarch.png`
- `assets/images/maps/scalefen.png`
- `assets/images/maps/ashenreach.png`
- `assets/music/intro.ogg`
- `assets/music/character_select.ogg`

## Commandes principales

- `help` : afficher l'aide
- `map` : afficher la carte
- `walkable` ou `paths` : colorier les cases accessibles sur la carte
- `zoom island|continent|region` : changer la vue de carte, par exemple `zoom crownvale`
- `look` : observer l'endroit actuel
- `cd {cell}` : aller vers une case, par exemple `cd D6` ou `cd AA16`
- `cd {region}` : changer de region si tu as le pass, par exemple `cd greenmarch`
- `cd {location}` : entrer dans un lieu
- `cd ..` : revenir en arriere
- `sail` : voyager en bateau depuis un port autorise
- `talk` : parler a un PNJ
- `fight` : combattre
- `search` : fouiller
- `inventory` ou `inv` : afficher l'inventaire
- `equip {item}` : equiper une arme ou armure
- `use {item}` : utiliser un consommable
- `buy {item}` : acheter
- `sell {item}` : vendre
- `sleep` : dormir dans une taverne
- `train` : augmenter le nombre de sorts disponibles
- `quit` : quitter

## Structure du projet

- `game.py` : boucle principale et commandes du jeu
- `data/` : contenu du jeu, objets, ennemis, lieux, dialogues, configuration
- `engine/` : logique de combat, joueur, monde, intro et terminal
- `web/` : site et wiki du jeu
- `patches/` : notes des anciennes versions
- `ROADMAP.md` : plan de transformation vers la version graphique `.exe`

## Direction

La prochaine grande version doit rester en Python, avec une interface Pygame :

- menu principal
- nouvelle partie / chargement
- intro avec pixel art, texte progressif et musique
- creation de personnage apres l'intro : race, genre et classe
- interface avec terminal integre
- panneaux pour joueur, stats, carte et informations
- build final en `.exe`
