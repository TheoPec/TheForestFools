# The Forest Fools - Asset Guide

Ce guide explique les formats a utiliser pour remplacer les placeholders de la Phase 4 par tes vrais pixel arts, sprites et musiques.

## Regle generale

- Format image recommande : `.png`
- Pixel art : dessiner petit, exporter net, sans flou.
- Ratio intro/menu recommande : `16:9`
- Taille recommandee : `320x180`
- Taille plus detaillee possible : `640x360`
- Le jeu agrandit les images automatiquement en gardant le style pixel art.

## Direction artistique actuelle

Le projet part maintenant sur un style moins sombre :

- ciel bleu
- vallee verte
- chateau sur une montagne
- champs en bas de l'image
- fantasy aventure, pas horror pur
- une menace qui arrive doucement dans l'intro

Le menu doit donner envie d'entrer dans le monde avant que le danger apparaisse.

## Menu principal

Le menu peut utiliser une image fixe ou une animation.

Image fixe :

```text
assets/images/menu/menu_bg.png
```

Animation par frames :

```text
assets/images/menu/menu_bg_000.png
assets/images/menu/menu_bg_001.png
assets/images/menu/menu_bg_002.png
...
```

Recommandation :

- `320x180`
- `4 a 8 frames` pour une petite animation
- environ `6 FPS`
- composition conseillee :
  - ciel bleu sur la moitie haute
  - montagne au fond
  - chateau sur la montagne
  - vallee/champs en bas
  - petite route qui part vers le chateau
  - assez d'espace lisible au centre/bas pour le menu texte

Animation simple possible :

- nuages qui bougent legerement
- herbe/champs qui ondulent
- drapeau du chateau qui bouge

Important : evite de mettre trop de details au centre bas, parce que le menu s'affiche par-dessus.

## Intro cinematique

Il y a 5 scenes prevues. Le pixel art prend tout l'ecran et le texte apparait par-dessus en bas.

Chaque image doit etre lisible meme avec une bande sombre transparente en bas pour le texte.

Le menu et la scene 1 doivent pouvoir etre la meme image. Si tu fournis seulement `assets/images/menu/menu_bg.png`, le jeu peut deja reutiliser ce visuel pour la premiere scene.

### Scene 1 - The Quiet Valley

Image fixe :

```text
assets/images/intro/01_valley.png
```

Animation :

```text
assets/images/intro/01_valley_000.png
assets/images/intro/01_valley_001.png
...
```

Quoi dessiner :

- meme composition que le menu : vallee lumineuse, chateau, champs, riviere, village
- ciel bleu, monde vivant, paix apparente
- aucun danger visible ou presque

Texte associe :

```text
The valley was peaceful.
Green fields stretched beneath the castle.
No one believed the old legends anymore.
```

### Scene 2 - The First Sign

```text
assets/images/intro/02_burning_road.png
```

ou :

```text
assets/images/intro/02_burning_road_000.png
assets/images/intro/02_burning_road_001.png
...
```

Quoi dessiner :

- route de terre au lever du jour
- charrette renversee ou abimee
- petite fumee au loin derriere les collines
- ambiance inquiete mais pas horror
- pas d'armee visible

Texte associe :

```text
Then the roads began to burn.
No army was seen.
Only smoke rising beyond the hills.
```

### Scene 3 - Silent Towers

```text
assets/images/intro/03_silent_towers.png
```

ou :

```text
assets/images/intro/03_silent_towers_000.png
assets/images/intro/03_silent_towers_001.png
...
```

Quoi dessiner :

- collines avec tours de guet en bois
- lanternes eteintes
- pas de gardes visibles
- foret calme au loin
- brume legere, mystere, pas horreur

Texte associe :

```text
The watchtowers fell silent.
No bells rang.
No guards returned.
```

### Scene 4 - The King's Question

```text
assets/images/intro/04_council.png
```

ou :

```text
assets/images/intro/04_council_000.png
assets/images/intro/04_council_001.png
...
```

Quoi dessiner :

- salle du conseil du chateau
- vieux roi inquiet
- grande carte du royaume sur une table en bois
- bougies, parchemins, symboles de foret
- lumiere douce du matin par une fenetre

Texte associe :

```text
The king did not ask for war.
He asked for someone brave enough to enter the forest.
Or foolish enough.
```

### Scene 5 - Forest Fools

```text
assets/images/intro/05_forest_fools.png
```

ou :

```text
assets/images/intro/05_forest_fools_000.png
assets/images/intro/05_forest_fools_001.png
...
```

Quoi dessiner :

- entree d'une ancienne foret
- chemin etroit entre de tres grands arbres
- racines visibles
- brume legere
- petites lumieres vertes/dorees mysterieuses
- silhouette possible du joueur devant le chemin, petite

Texte associe :

```text
They called them Forest Fools.
Scouts, wanderers, forgotten names.
The ones who walked where kingdoms ended.
```

## Combien de pixel arts faire ?

Minimum pour remplacer toute l'intro :

- `1` image de menu
- `5` images intro

Total minimum : `6 images`, ou `5 images` si tu reutilises exactement l'image du menu comme `01_valley`.

Version animee simple :

- menu : `4 a 8 frames`
- chaque scene intro : `3 a 8 frames`

Total conseille si tu veux une intro animee mais raisonnable : environ `25 a 45 frames`.

Idees d'animation simples :

- `01_valley` : nuages, herbe, drapeau
- `02_burning_road` : fumee qui bouge, petites flammes
- `03_silent_towers` : brume ou lanternes eteintes qui oscillent legerement
- `04_council` : bougies qui tremblent
- `05_forest_fools` : petites lumieres, brume, feuilles

## Creation de personnage

Apres l'intro, le jeu affiche un ecran de creation controle uniquement au clavier.

Il y a :

- race : `Human`, `Elf`, `Lizardfolk`
- genre : `Male`, `Female`
- classe : `Warrior`, `Mage`

Le joueur voit les deux personnages de la race choisie, homme et femme. Le personnage selectionne recoit deja un glow dans le jeu, donc tes PNG n'ont pas besoin d'avoir un effet lumineux integre.

### Fond de creation

Le plus propre est de travailler en 3 couches :

- `background.png` : le decor seulement
- `{race}_female_{class}.png` : personnage femme transparent, assis sur le rocher
- `{race}_male_{class}.png` : personnage homme transparent, debout

Important : ne fusionne pas les personnages dans le fond si tu veux un glow propre autour du personnage selectionne.

Image fixe :

```text
assets/images/character_select/background.png
```

Le fond de creation est une image fixe. Il ne reprend pas le fond du menu.

Recommandation :

- ratio `16:9`
- `320x180` minimum
- `640x360` si tu veux plus de detail
- style lumineux comme le menu
- assez lisible en haut pour les choix race/genre/classe
- scene conseillee : l'homme assis sur un rocher a gauche, la femme debout a droite
- le fond peut deja contenir le rocher, l'herbe, la lumiere et l'ambiance generale
- garde des zones libres pour poser les deux PNG personnages par-dessus
- pas de voile noir ni de gros cercle lumineux dans le fond

### Portraits/personnages

Images fixes attendues :

```text
assets/images/characters/human_male.png
assets/images/characters/human_female.png
assets/images/characters/elf_male.png
assets/images/characters/elf_female.png
assets/images/characters/lizardfolk_male.png
assets/images/characters/lizardfolk_female.png
```

Version avec tenue differente selon la classe :

```text
assets/images/characters/human_female_warrior.png
assets/images/characters/human_female_mage.png
assets/images/characters/human_male_warrior.png
assets/images/characters/human_male_mage.png
assets/images/characters/elf_female_warrior.png
assets/images/characters/elf_female_mage.png
assets/images/characters/elf_male_warrior.png
assets/images/characters/elf_male_mage.png
assets/images/characters/lizardfolk_female_warrior.png
assets/images/characters/lizardfolk_female_mage.png
assets/images/characters/lizardfolk_male_warrior.png
assets/images/characters/lizardfolk_male_mage.png
```

Le jeu cherche d'abord la version avec classe (`race_gender_class.png`). Si elle n'existe pas, il retombe sur l'ancien nom (`race_gender.png`), puis sur un placeholder.

Animations possibles :

```text
assets/images/characters/human_male_000.png
assets/images/characters/human_male_001.png
...
```

Puis pareil pour chaque race/genre.

Recommandation :

- PNG avec fond transparent
- format vertical
- `128x192`, `160x240` ou `192x256`
- femme : pose assise, prevue pour etre posee sur le rocher a gauche
- homme : pose debout, prevu pour etre place dans l'espace a droite
- personnage entier ou presque entier, avec assez d'espace transparent autour pour le glow
- mage et guerrier peuvent avoir la meme pose, mais la tenue doit changer

Musique optionnelle pour cet ecran :

```text
assets/music/character_select.ogg
```

Si ce fichier manque, le jeu continue simplement avec la musique deja lancee.

## Cartes du monde

Le jeu utilise maintenant des cartes fixes :

- `Mosswake Isle` : petite ile de tutoriel
- `Mainland of Elarion` : grand continent coupe en 4 regions

Le panneau carte peut afficher une image pixel art si tu la poses ici :

```text
assets/images/maps/mosswake.png
assets/images/maps/continent.png
```

Images optionnelles pour les zooms de region :

```text
assets/images/maps/crownvale.png
assets/images/maps/greenmarch.png
assets/images/maps/scalefen.png
assets/images/maps/ashenreach.png
```

Si une image manque, le jeu affiche automatiquement la carte en grille.

Fond/cadre papier optionnel derriere la carte :

```text
assets/images/maps/map_paper.png
assets/images/maps/mosswake_paper.png
assets/images/maps/continent_paper.png
assets/images/maps/crownvale_paper.png
assets/images/maps/greenmarch_paper.png
assets/images/maps/scalefen_paper.png
assets/images/maps/ashenreach_paper.png
```

`map_paper.png` sert de cadre commun pour toutes les cartes. Un fichier specifique comme `mosswake_paper.png` remplace seulement le cadre de cette carte.

Recommandation pour le cadre papier :

- ratio plutot horizontal, environ `3:2` ou `16:9`
- centre assez vide pour poser la map
- bordure parchemin/ancienne carte
- espace en haut pour le nom de la carte
- pas de quadrillage dans le papier, le jeu ajoute deja la grille
- pas d'icones de lieux dans le cadre

Recommandation :

- ratio `1:1`, donc une image carree
- `512x512` minimum
- `1024x1024` si tu veux beaucoup de details
- style lisible, couleurs claires, routes visibles
- pense la carte comme une vraie carte vue du dessus, pas comme un paysage
- ne dessine pas les icones de village/port/donjon directement dans l'image de base si tu veux que le jeu les revele plus tard
- l'image de base doit surtout montrer les formes : eau, terre, forets, montagnes, routes, plage

Grilles logiques :

```text
Mosswake Isle : 10x10
Mainland of Elarion : 52x52
Chaque region zoomee : 26x26
```

Le jeu ajoute lui-meme :

- un quadrillage discret
- une case joueur qui clignote doucement
- des symboles seulement sur les lieux deja visites ou reveles par dialogue

Les lieux caches ne doivent pas etre visibles au debut. Sur Mosswake, le village et la foret sont connus au depart, mais Slime Hollow et Southwake Port ne sont pas marques tant que le maire ne les revele pas.

Coordonnees importantes actuelles :

```text
Mosswake Isle
E5 Greenhollow Village
D6 Old Fern Forest
F8 Slime Hollow
G5 Southwake Port

Mainland of Elarion
D23 Crownport
M12 Crownvale Capital
H9 Crownvale Keep
Q17 Fairmeadow Village
V4 Northwatch Woods
S20 Sunmere Woods
AJ9 Greenmarch Village
M32 Scalefen Marshhold
AM42 Ashenreach Dragon Lair
```

Commandes liees :

```text
map
zoom island
zoom continent
zoom crownvale
zoom greenmarch
zoom scalefen
zoom ashenreach
cd greenmarch
cd scalefen
cd ashenreach
sail
```

Pour changer de region avec `cd greenmarch`, `cd scalefen` ou `cd ashenreach`, le joueur doit avoir le pass correspondant.

## Spritesheets

Pour l'instant, le jeu lit surtout des frames separees (`_000`, `_001`, etc.).

Format conseille pour tes sprites plus tard :

- personnage portrait : `128x128`, PNG transparent
- petits sprites de personnage : `32x32` ou `48x48`
- ennemis : `64x64` ou `96x96`
- animations simples : `4 a 8 frames`

On pourra ajouter la lecture de spritesheets en Phase 8 si tu preferes travailler en une seule image.

## Musique

Format recommande :

```text
assets/music/intro.ogg
```

Le jeu accepte aussi :

```text
assets/music/intro.wav
assets/music/intro.mp3
```

Recommandation audio :

- meilleur choix : `.ogg`
- `44.1 kHz`
- mono ou stereo
- boucle propre si possible
- duree conseillee : `45 a 120 secondes`

Pourquoi `.ogg` : bon pour Pygame, leger, propre pour une musique de jeu.

## Sons

Pas encore branches partout, mais format conseille :

```text
assets/sounds/click.wav
assets/sounds/hit.wav
assets/sounds/victory.wav
```

Recommandation :

- `.wav`
- `44.1 kHz`
- court, entre `0.1` et `2 secondes`

## UI

Elements utiles plus tard :

```text
assets/ui/player_portrait.png
assets/ui/frame_player.png
assets/ui/frame_terminal.png
assets/ui/frame_map.png
assets/ui/frame_info.png
```

Recommandation :

- portrait joueur : `128x128`
- icone executable : `256x256`, `.ico` plus tard pour PyInstaller

## Notes importantes

- Tous les fichiers sont optionnels pour l'instant.
- Si un fichier manque, le jeu affiche un placeholder.
- Les noms de fichiers doivent etre exactement ceux de ce guide.
- Garde les images en pixel art net, sans anti-aliasing.
