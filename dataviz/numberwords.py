from string import ascii_letters

from pudzu.pillar import *

ENGLISH = "zero,one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,eighteen,nineteen,twenty,twenty-one,twenty-two,twenty-three,twenty-four,twenty-five,twenty-six,twenty-seven,twenty-eight,twenty-nine,thirty,thirty-one,thirty-two,thirty-three,thirty-four,thirty-five,thirty-six,thirty-seven,thirty-eight,thirty-nine,forty,forty-one,forty-two,forty-three,forty-four,forty-five,forty-six,forty-seven,forty-eight,forty-nine,fifty,fifty-one,fifty-two,fifty-three,fifty-four,fifty-five,fifty-six,fifty-seven,fifty-eight,fifty-nine,sixty,sixty-one,sixty-two,sixty-three,sixty-four,sixty-five,sixty-six,sixty-seven,sixty-eight,sixty-nine,seventy,seventy-one,seventy-two,seventy-three,seventy-four,seventy-five,seventy-six,seventy-seven,seventy-eight,seventy-nine,eighty,eighty-one,eighty-two,eighty-three,eighty-four,eighty-five,eighty-six,eighty-seven,eighty-eight,eighty-nine,ninety,ninety-one,ninety-two,ninety-three,ninety-four,ninety-five,ninety-six,ninety-seven,ninety-eight,ninety-nine"
FRENCH = "zéro,un,deux,trois,quatre,cinq,six,sept,huit,neuf,dix,onze,douze,treize,quatorze,quinze,seize,dix-sept,dix-huit,dix-neuf,vingt,vingt et un,vingt-deux,vingt-trois,vingt-quatre,vingt-cinq,vingt-six,vingt-sept,vingt-huit,vingt-neuf,trente,trente et un,trente-deux,trente-trois,trente-quatre,trente-cinq,trente-six,trente-sept,trente-huit,trente-neuf,quarante,quarante et un,quarante-deux,quarante-trois,quarante-quatre,quarante-cinq,quarante-six,quarante-sept,quarante-huit,quarante-neuf,cinquante,cinquante et un,cinquante-deux,cinquante-trois,cinquante-quatre,cinquante-cinq,cinquante-six,cinquante-sept,cinquante-huit,cinquante-neuf,soixante,soixante et un,soixante-deux,soixante-trois,soixante-quatre,soixante-cinq,soixante-six,soixante-sept,soixante-huit,soixante-neuf,soixante-dix,soixante et onze,soixante-douze,soixante-treize,soixante-quatorze,soixante-quinze,soixante-seize,soixante-dix-sept,soixante-dix-huit,soixante-dix-neuf,quatre-vingts,quatre-vingt-un,quatre-vingt-deux,quatre-vingt-trois,quatre-vingt-quatre,quatre-vingt-cinq,quatre-vingt-six,quatre-vingt-sept,quatre-vingt-huit,quatre-vingt-neuf,quatre-vingt-dix,quatre-vingt-onze,quatre-vingt-douze,quatre-vingt-treize,quatre-vingt-quatorze,quatre-vingt-quinze,quatre-vingt-seize,quatre-vingt-dix-sept,quatre-vingt-dix-huit,quatre-vingt-dix-neuf"
GERMAN = "null,eins,zwei,drei,vier,fünf,sechs,sieben,acht,neun,zehn,elf,zwölf,dreizehn,vierzehn,fünfzehn,sechzehn,siebzehn,achtzehn,neunzehn,zwanzig,einundzwanzig,zweiundzwanzig,dreiundzwanzig,vierundzwanzig,fünfundzwanzig,sechsundzwanzig,siebenundzwanzig,achtundzwanzig,neunundzwanzig,dreiβig,einunddreiβig,zweiunddreißig,dreiunddreißig,vierunddreißig,fünfunddreißig,sechsunddreißig,siebenunddreißig,achtunddreißig,neununddreißig,vierzig,einundvierzig,zweiundvierzig,dreiundvierzig,vierundvierzig,fünfundvierzig,sechsundvierzig,siebenundvierzig,achtundvierzig,neunundvierzig,fünfzig,einundfünfzig,zweiundfünfzig,dreiundfünfzig,vierundfünfzig,fünfundfünfzig,sechsundfünfzig,siebenundfünfzig,achtundfünfzig,neunundfünfzig,sechzig,einundsechzig,zweiundsechzig,dreiundsechzig,vierundsechzig,fünfundsechzig,sechsundsechzig,siebenundsechzig,achtundsechzig,neunundsechzig,siebzig,einundsiebzig,zweiundsiebzig,dreiundsiebzig,vierundsiebzig,fünfundsiebzig,sechsundsiebzig,siebenundsiebzig,achtundsiebzig,neunundsiebzig,achtzig,einundachtzig,zweiundachtzig,dreiundachtzig,vierundachtzig,fünfundachtzig,sechsundachtzig,siebenundachtzig,achtundachtzig,neunundachtzig,neunzig,einundneunzig,zweiundneunzig,dreiundneunzig,vierundneunzig,fünfundneunzig,sechsundneunzig,siebenundneunzig,achtundneunzig,neunundneunzig"
SPANISH = "cero,uno,dos,tres,cuatro,cinco,seis,siete,ocho,nueve,diez,once,doce,trece,catorce,quince,dieciséis,diecisiete,dieciocho,diecinueve,veinte,veintiuno,veintidós,veintitrés,veinticuatro,veinticinco,veintiséis,veintisiete,veintiocho,veintinueve,treinta,treinta y uno,treinta y dos,treinta y tres,treinta y cuatro,treinta y cinco,treinta y seis,treinta y siete,treinta y ocho,treinta y nueve,cuarenta,cuarenta y uno,cuarenta y dos,cuarenta y tres,cuarenta y cuatro,cuarenta y cinco,cuarenta y seis,cuarenta y siete,cuarenta y ocho,cuarenta y nueve,cincuenta,cincuenta y uno,cincuenta y dos,cincuenta y tres,cincuenta y cuatro,cincuenta y cinco,cincuenta y seis,cincuenta y siete,cincuenta y ocho,cincuenta y nueve,sesenta,sesenta y uno,sesenta y dos,sesenta y tres,sesenta y cuatro,sesenta y cinco,sesenta y seis,sesenta y siete,sesenta y ocho,sesenta y nueve,setenta,setenta y uno,setenta y dos,setenta y tres,setenta y cuatro,setenta y cinco,setenta y seis,setenta y siete,setenta y ocho,setenta y nueve,ochenta,ochenta y uno,ochenta y dos,ochenta y tres,ochenta y cuatro,ochenta y cinco,ochenta y seis,ochenta y siete,ochenta y ocho,ochenta y nueve,noventa,noventa y uno,noventa y dos,noventa y tres,noventa y cuatro,noventa y cinco,noventa y seis,noventa y siete,noventa y ocho,noventa y nueve"

def plot(name, language, color, translation = None):
    if translation is not None:
        language = replace_map(language.lower(), translation)
    language = replace_any(language, " -", "")
    assert set(language) < set(ascii_letters) | {","}, set(language)
    words = language.split(",")
    assert len(words) == 100
    order = sorted((w,i) for i,w in enumerate(words))

    # very hacky!
    color=color.darken(0.25)
    grid = [[None for i in range(100)] for j in range(100)]
    for j,(w,i) in enumerate(order):
        grid[100-j-1][i] = Rectangle(8, color)
    grid = Image.from_array(grid, bg="white").add_grid((10,10), bg="#CCCCCC")

    ylabels = Rectangle((50, grid.height), "white")
    ylabels.place(Image.from_text("last", sans(16), padding=5).transpose(Image.ROTATE_90), (0.5,0), copy=False)
    ylabels.place(Image.from_text("first", sans(16), padding=5).transpose(Image.ROTATE_90), (0.5,1), copy=False)
    ylabels.place(Image.from_text("alphabetical position", sans(16, italics=True), padding=5).transpose(Image.ROTATE_90), (0.5,0.5), copy=False)
    grid = Image.from_row([ylabels, grid])

    labels = [Rectangle((50,1), "white")] + [Image.from_text(f"{i*10}–{i*10+9}", sans(16), padding=5).pad_to(80, bg="white") for i in range(10)]
    title = Image.from_text(name.upper(), sans(48, bold=True), color, beard_line=True, padding=10)
    grid = Image.from_column([title, grid, Image.from_row(labels)], bg="white")

    return grid

english = plot("English", ENGLISH, VegaPalette10.RED)
french = plot("French*", FRENCH, VegaPalette10.BLUE, {"é": "e"})
german = plot("German", GERMAN, VegaPalette10.PURPLE, {"ü": "ue", "ö": "oe", "β": "ss", "ß": "ss"})
spanish = plot("Spanish", SPANISH, VegaPalette10.GREEN, {"ó": "o", "é": "e"})
grids = Image.from_array([[english, french], [spanish, german]], padding=20, bg="white")

title = Image.from_text("The numbers 0–99 sorted alphabetically in...".upper(), sans(64, bold=True), padding=20)
footer = Image.from_text("* specifically French as spoken in France (Belgian and Swiss French use a decimal system for 60–99)", sans(32, italics=True), padding=20)
img = Image.from_column([title, grids, footer], bg="white")
img.place(Image.from_text("/u/Udzu", sans(24), padding=10).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/numberwords.png")
