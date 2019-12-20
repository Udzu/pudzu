from pudzu.sandbox.unicode import *

# cf http://www.cesarkallas.net/arquivos/livros/informatica/unicode/ch06.pdf
# split off emoji, math, (hani?) from Common

TYPES = {
    'other': ['Common', 'Inherited'],
    'alphabet': ['Adlam', 'Armenian', 'Avestan', 'Bassa_Vah', 'Braille', 'Carian', 'Caucasian_Albanian', 'Coptic', 'Cyrillic',
                 'Deseret', 'Duployan', 'Elbasan', 'Georgian', 'Glagolitic', 'Gothic', 'Greek', 'Hanifi_Rohingya',
                 'Kayah_Li', 'Latin', 'Lisu', 'Lycian', 'Lydian', 'Medefaidrin', 'Mongolian', 'Mro', 'New_Tai_Lue',
                 'Nko', 'Nyiakeng_Puachue_Hmong', 'Ogham', 'Ol_Chiki', 'Old_Hungarian', 'Old_Italic', 'Old_Permic',
                 'Old_Turkic', 'Osage', 'Osmanya', 'Pau_Cin_Hau', 'Phags_Pa', 'Runic'],
    'abjad': ['Arabic', 'Elymaic', 'Hatran', 'Hebrew', 'Imperial_Aramaic', 'Inscriptional_Pahlavi', 'Inscriptional_Parthian',
              'Mandaic', 'Manichaean', 'Nabataean', 'Old_North_Arabian', 'Old_Sogdian', 'Old_South_Arabian', 'Palmyrene',
              'Phoenician', 'Psalter_Pahlavi',
              'Syriac', 'Tifinagh'],
    'abugida': ['Ahom', 'Balinese', 'Batak', 'Bengali', 'Bhaiksuki', 'Brahmi', 'Buginese', 'Buhid', 'Chakma', 'Cham', 
                'Devanagari', 'Dogra', 'Ethiopic', 'Grantha', 'Gujarati', 'Gunjala_Gondi', 'Gurmukhi', 'Hanunoo',
                'Javanese', 'Kaithi', 'Kannada', 'Kharoshthi', 'Khmer', 'Khojki', 'Khudawadi', 'Lao', 'Lepcha', 'Limbu',
                'Mahajani', 'Makasar', 'Malayalam', 'Marchen', 'Masaram_Gondi', 'Meetei_Mayek',
                'Meroitic_Cursive', 'Meroitic_Hieroglyphs', 'Miao', 'Modi', 'Multani', 'Myanmar', 'Nandinagari', 'Newa',
                'Oriya', 'Rejang'],
    'semi-syllabary': ['Bamum', 'Bopomofo', 'Old_Persian', 'Pahawh_Hmong'],
    'syllabary': ['Cherokee', 'Cypriot', 'Hiragana', 'Katakana', 'Linear_A', 'Linear_B', 'Mende_Kikakui', 'Nushu'],
    'logographic': ['Anatolian_Hieroglyphs', 'Cuneiform', 'Egyptian_Hieroglyphs', 'Han', 'Tangut', 'Yi'],
    'featural': ['Canadian_Aboriginal', 'Hangul', 'SignWriting']
}

ORIGINS = {
    'China': ['Bopomofo', 'Han', 'Lisu', 'Miao', 'New_Tai_Lue', 'Nushu', 'Tangut', 'Yi'],
    'Japan': ['Hiragana', 'Katakana'],
    'Korea': ['Hangul'],
    'Mongolia': ['Mongolian'],
    'Tibet': ['Phags_Pa']
}

SCRIPT_TYPES = { script : type for type,scripts in TYPES.items() for script in scripts }

df = unicode_data()
missing = set(df.Script) - set(SCRIPT_TYPES)
