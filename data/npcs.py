"""
=============================================================================
  NPC DIALOGUES — Dialogues des PNJ
=============================================================================
  Les variables {loc_type} et {coord} sont remplacées automatiquement
  par un lieu d'intérêt sur la carte.

  NPC_DIALOGUES     → dans les villages (tavern, blacksmith, etc.)
  NPC_DIALOGUES_WILD → dans la nature (clearing, ruins, dock, etc.)
=============================================================================
"""

NPC_DIALOGUES = {
    "tavern": {
        "barkeep": [
            '"Ale?" The barkeep slides a cracked tankard toward you. "A traveller, eh. You look half-dead already." He leans closer. "Word is there\'s a {loc_type} at {coord}. Folk who went there... didn\'t come back."',
            '"Keep your voice down." The barkeep glances around. "A merchant came through last week, raving about a {loc_type} near {coord}. Said he saw things crawling in the dark. I say stay away."',
            '"You want advice? Head to {coord}. There\'s a {loc_type} there. Dangerous, aye, but those who survive come back richer than kings. Or they don\'t come back at all."',
        ],
        "drunk": [
            'A man slumped over the bar grabs your arm. "I seen it... the {loc_type}... at {coord}..." He shivers. "The dead walk there. They walk and they wait."',
            '"Hic... you look strong enough..." A drunk patron waves vaguely. "Go to {coord}. The {loc_type}... there\'s treasure. Gold. I\'d go myself but... hic... my legs don\'t work so good."',
        ],
        "hooded_figure": [
            'A hooded figure in the corner beckons. "Seek the {loc_type} at {coord}. What you find there will change you. For better or worse." They vanish into shadow before you can reply.',
        ],
    },
    "blacksmith": {
        "blacksmith": [
            'The blacksmith doesn\'t look up from his anvil. "You\'ll need better steel if you\'re heading to {coord}. There\'s a {loc_type} there. The things inside... they don\'t die easy."',
            '"I forged a blade for a knight once. He was bound for the {loc_type} at {coord}." The blacksmith pauses. "The blade came back. He didn\'t."',
            '"Word of advice, stranger. The {loc_type} at {coord} -- don\'t go at night. Not that it matters. It\'s always night down there."',
        ],
    },
    "chapel": {
        "priest": [
            'The priest turns slowly. His eyes are milky and unfocused. "The darkness gathers at {coord}. A {loc_type} festers there like a wound in the earth. Pray before you go. It may be your last chance."',
            '"Child, the dead do not rest at {coord}. The {loc_type} there is cursed. I have blessed many who went to face it. I have buried more."',
            '"I hear confessions from soldiers who returned from {coord}. The {loc_type}... it changed them. They speak of altars and bones and things that should not live."',
        ],
    },
    "square": {
        "old_woman": [
            'An old woman sits by the well, muttering. She looks up as you approach. "The crows fly toward {coord}. Where crows gather, death follows. There\'s a {loc_type} there. Mark my words."',
            '"You\'re not from here." The old woman clutches a dead raven to her chest. "Go to {coord} if you want answers. The {loc_type} holds secrets. But secrets have teeth."',
        ],
        "guard": [
            'A guard leans against the gallows post. "We lost three men at {coord} last month. {loc_type}. Whatever\'s in there, it\'s getting bolder. Could use someone fool enough to go in."',
        ],
    },
    "merchant": {
        "merchant": [
            '"Ah, a customer." The merchant smiles thinly. "If you\'re heading to the {loc_type} at {coord}, you\'ll want potions. Lots of potions. The things down there don\'t bargain."',
            '"I trade with every village in these lands. The one near {coord}? They won\'t go near the {loc_type} anymore. Bad for business, but good for yours -- less competition for whatever\'s inside."',
        ],
    },
}

NPC_DIALOGUES_WILD = {
    "clearing": {
        "hermit": [
            'A gaunt figure crouches by a fire of green flame. "You seek purpose? Go to {coord}. The {loc_type} there calls to those who listen. I heard it once. I will not hear it again."',
        ],
    },
    "ruins": {
        "ghost": [
            'A pale shimmer in the air. A voice, thin as wind: "I fell at {coord}. The {loc_type}... it took everything. Avenge me, or join me."',
        ],
    },
    "courtyard": {
        "dying_knight": [
            'A knight slumps against a broken pillar, bleeding. "The {loc_type} at {coord}... we tried to clear it. Too many of them." He coughs blood. "Finish what we started."',
        ],
    },
    "entrance": {
        "survivor": [
            'A figure stumbles out of the darkness, wild-eyed. "Don\'t... don\'t go deeper." They grip your shoulder. "But if you want real treasure, the {loc_type} at {coord} is worse. And richer."',
        ],
    },
    "dock": {
        "old_sailor": [
            '"The sea\'s been angry lately." The old sailor spits into the water. "Used to take the chalutier out beyond the reef. Can\'t now." He squints at the horizon. "Heard there\'s trouble at the {loc_type} near {coord}."',
            '"That chalutier there? She\'s mine. Seaworthy, aye. But I won\'t sail until things calm down. Heard tales of a {loc_type} at {coord}. Dark tales."',
        ],
    },
}
