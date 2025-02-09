from string import ascii_letters

from pudzu.pillar import *
from pudzu.utils import replace_map
from graphviz import Digraph

ENGLISH = "one,two,three,four,five,six,seven,eight,nine,ten,eleven,twelve,thirteen,fourteen,fifteen,sixteen,seventeen,eighteen,nineteen,twenty,twenty-one,twenty-two,twenty-three,twenty-four,twenty-five,twenty-six,twenty-seven,twenty-eight,twenty-nine,thirty,thirty-one,thirty-two,thirty-three,thirty-four,thirty-five,thirty-six,thirty-seven,thirty-eight,thirty-nine,forty,forty-one,forty-two,forty-three,forty-four,forty-five,forty-six,forty-seven,forty-eight,forty-nine,fifty,fifty-one,fifty-two,fifty-three,fifty-four,fifty-five,fifty-six,fifty-seven,fifty-eight,fifty-nine,sixty,sixty-one,sixty-two,sixty-three,sixty-four,sixty-five,sixty-six,sixty-seven,sixty-eight,sixty-nine,seventy,seventy-one,seventy-two,seventy-three,seventy-four,seventy-five,seventy-six,seventy-seven,seventy-eight,seventy-nine,eighty,eighty-one,eighty-two,eighty-three,eighty-four,eighty-five,eighty-six,eighty-seven,eighty-eight,eighty-nine,ninety,ninety-one,ninety-two,ninety-three,ninety-four,ninety-five,ninety-six,ninety-seven,ninety-eight,ninety-nine,hundred"
FRENCH = "un,deux,trois,quatre,cinq,six,sept,huit,neuf,dix,onze,douze,treize,quatorze,quinze,seize,dix-sept,dix-huit,dix-neuf,vingt,vingt et un,vingt-deux,vingt-trois,vingt-quatre,vingt-cinq,vingt-six,vingt-sept,vingt-huit,vingt-neuf,trente,trente et un,trente-deux,trente-trois,trente-quatre,trente-cinq,trente-six,trente-sept,trente-huit,trente-neuf,quarante,quarante et un,quarante-deux,quarante-trois,quarante-quatre,quarante-cinq,quarante-six,quarante-sept,quarante-huit,quarante-neuf,cinquante,cinquante et un,cinquante-deux,cinquante-trois,cinquante-quatre,cinquante-cinq,cinquante-six,cinquante-sept,cinquante-huit,cinquante-neuf,soixante,soixante et un,soixante-deux,soixante-trois,soixante-quatre,soixante-cinq,soixante-six,soixante-sept,soixante-huit,soixante-neuf,soixante-dix,soixante et onze,soixante-douze,soixante-treize,soixante-quatorze,soixante-quinze,soixante-seize,soixante-dix-sept,soixante-dix-huit,soixante-dix-neuf,quatre-vingts,quatre-vingt-un,quatre-vingt-deux,quatre-vingt-trois,quatre-vingt-quatre,quatre-vingt-cinq,quatre-vingt-six,quatre-vingt-sept,quatre-vingt-huit,quatre-vingt-neuf,quatre-vingt-dix,quatre-vingt-onze,quatre-vingt-douze,quatre-vingt-treize,quatre-vingt-quatorze,quatre-vingt-quinze,quatre-vingt-seize,quatre-vingt-dix-sept,quatre-vingt-dix-huit,quatre-vingt-dix-neuf,cent"
GERMAN = "eins,zwei,drei,vier,fünf,sechs,sieben,acht,neun,zehn,elf,zwölf,dreizehn,vierzehn,fünfzehn,sechzehn,siebzehn,achtzehn,neunzehn,zwanzig,einundzwanzig,zweiundzwanzig,dreiundzwanzig,vierundzwanzig,fünfundzwanzig,sechsundzwanzig,siebenundzwanzig,achtundzwanzig,neunundzwanzig,dreiβig,einunddreiβig,zweiunddreißig,dreiunddreißig,vierunddreißig,fünfunddreißig,sechsunddreißig,siebenunddreißig,achtunddreißig,neununddreißig,vierzig,einundvierzig,zweiundvierzig,dreiundvierzig,vierundvierzig,fünfundvierzig,sechsundvierzig,siebenundvierzig,achtundvierzig,neunundvierzig,fünfzig,einundfünfzig,zweiundfünfzig,dreiundfünfzig,vierundfünfzig,fünfundfünfzig,sechsundfünfzig,siebenundfünfzig,achtundfünfzig,neunundfünfzig,sechzig,einundsechzig,zweiundsechzig,dreiundsechzig,vierundsechzig,fünfundsechzig,sechsundsechzig,siebenundsechzig,achtundsechzig,neunundsechzig,siebzig,einundsiebzig,zweiundsiebzig,dreiundsiebzig,vierundsiebzig,fünfundsiebzig,sechsundsiebzig,siebenundsiebzig,achtundsiebzig,neunundsiebzig,achtzig,einundachtzig,zweiundachtzig,dreiundachtzig,vierundachtzig,fünfundachtzig,sechsundachtzig,siebenundachtzig,achtundachtzig,neunundachtzig,neunzig,einundneunzig,zweiundneunzig,dreiundneunzig,vierundneunzig,fünfundneunzig,sechsundneunzig,siebenundneunzig,achtundneunzig,neunundneunzig,einhundert"
SPANISH = "uno,dos,tres,cuatro,cinco,seis,siete,ocho,nueve,diez,once,doce,trece,catorce,quince,dieciséis,diecisiete,dieciocho,diecinueve,veinte,veintiuno,veintidós,veintitrés,veinticuatro,veinticinco,veintiséis,veintisiete,veintiocho,veintinueve,treinta,treinta y uno,treinta y dos,treinta y tres,treinta y cuatro,treinta y cinco,treinta y seis,treinta y siete,treinta y ocho,treinta y nueve,cuarenta,cuarenta y uno,cuarenta y dos,cuarenta y tres,cuarenta y cuatro,cuarenta y cinco,cuarenta y seis,cuarenta y siete,cuarenta y ocho,cuarenta y nueve,cincuenta,cincuenta y uno,cincuenta y dos,cincuenta y tres,cincuenta y cuatro,cincuenta y cinco,cincuenta y seis,cincuenta y siete,cincuenta y ocho,cincuenta y nueve,sesenta,sesenta y uno,sesenta y dos,sesenta y tres,sesenta y cuatro,sesenta y cinco,sesenta y seis,sesenta y siete,sesenta y ocho,sesenta y nueve,setenta,setenta y uno,setenta y dos,setenta y tres,setenta y cuatro,setenta y cinco,setenta y seis,setenta y siete,setenta y ocho,setenta y nueve,ochenta,ochenta y uno,ochenta y dos,ochenta y tres,ochenta y cuatro,ochenta y cinco,ochenta y seis,ochenta y siete,ochenta y ocho,ochenta y nueve,noventa,noventa y uno,noventa y dos,noventa y tres,noventa y cuatro,noventa y cinco,noventa y seis,noventa y siete,noventa y ocho,noventa y nueve,cien"
NORWEGIAN = "en,to,tre,fire,fem,seks,syv,åtte,ni,tee,elleve,tolv,tretten,fjorten,femten,seksten,sytten,atten,nitten,tjue,tjueen,tjueto,tjuetre,tjuetre,tjuefem,tjuenseks,tjuensyv,tjueatte,tjue ni,tretti,trettién,trettito,trettitre,trettifire,trettifem,trettiseks,trettisju,trettiåtte,trettini,førti,førtién,førtito,førtitre,førtifire,førtifem,førtiseks,førtisju,førtiåtte,førtini,femti,femtién,femtito,femtitre,femtifire,femtifem,femtiseks,femtisju,femtiåtte,femtini,seksti,sekstién,sekstito,sekstitre,sekstifire,sekstifem,sekstiseks,sekstisju,sekstiåtte,sekstini,sytti,syttién,syttito,syttitre,syttifire,syttifem,syttiseks,syttisju,syttiåtte,syttini,åtti,åttién,åttito,åttitre,åttifire,åttifem,åttiseks,åttisju,åttiåtte,åttini,nitti,nittién,nittito,nittitre,nittifire,nittifem,nittiseks,nittisju,nittiåtte,nittini,hundre"
DANISH = "en,to,tre,fire,fem,seks,syv,otte,ni,ti,elleve,tolv,tretten,fjorten,femten,seksten,sytten,atten,nitten,tyve,en og tyve,to og tyve,tre og tyve,fire og tyve,fem og tyve,seks og tyve,syv og tyve,otte og tyve,ni og tyve,tredive,en og tredive,to og tredive,tre og tredive,fire og tredive,fem og tredive,seks og tredive,syv og tredive,otte og tredive,ni og tredive,fyrre,en og fyrre,to og fyrre,tre og fyrre,fire og fyrre,fem og fyrre,seks og fyrre,syv og fyrre,otte og fyrre,ni og fyrre,halvtreds,en og halvtreds,to og halvtreds,tre og halvtreds,fire og halvtreds,fem og halvtreds,seks og halvtreds,syv og halvtreds,otte og halvtreds,ni og halvtreds,tres,en og tres,to og tres,tre og tres,fire og tres,fem og tres,seks og tres,syv og tres,otte og tres,ni og tres,halvfjerds,en og halvfjerds,to og halvfjerds,tre og halvfjerds,fire og halvfjerds,fem og halvfjerds,seks og halvfjerds,syv og halvfjerds,otte og halvfjerds,ni og halvfjerds,firs,en og firs,to og firs,tre og firs,fire og firs,fem og firs,seks og firs,syv og firs,otte og firs,ni og firs,halvfems,en og halvfems,to og halvfems,tre og halvfems,fire og halvfems,fem og halvfems,seks og halvfems,syv og halvfems,otte og halvfems,ni og halvfems,et hundrede"

def label(ns, n):
    m = ceil(len(ns) / n)
    n2 = ceil(len(ns) / m)
    return ",\n".join([", ".join(x) for x in generate_batches(map(str, sorted(ns)), n2)])

def plot(name, language, color, translation = None, bold = frozenset()):
    if translation is not None:
        language = replace_map(language.lower(), translation)
    language = replace_any(language, " -", "")
    assert set(language) < set(ascii_letters) | {","}, set(language) - set(ascii_letters) - {","}
    words = language.split(",")
    assert len(words) == 100

    d = { i : len(w) for i,w in enumerate(words, 1) }
    d2 = { a : (b, frozenset({ x for x,y in d.items() if y == a})) for a, b in d.items() }
    d3 = {}
    for a, bc in d2.items():
        d3.setdefault(bc, set()).add(a)
    d4 = { label(a, 5) : str(b) for (b, c), a in d3.items() }

    g = Digraph('G', filename=f'cache/numberwords{name}.gv', format="png")
    g.attr(newrank="True", rankdir="TB", bgcolor="transparent")
    for a in d4.keys():
        if a in map(str, bold):
            g.node(a, label=f"<<b>{a}</b>>", fontcolor=color.to_hex(), color=color.to_hex())
        else:
            g.node(a)
    for a, b in d4.items():
        if a in map(str, bold):
            g.edge(a, b, color=color.to_hex())
        else:
            g.edge(a, b)

    g.render()
    grid = Image.open(f"cache/numberwords{name}.gv.png")
    title = Image.from_text(name.upper(), sans(48, bold=True), color, beard_line=True, padding=15)
    grid = Image.from_column([title, grid])
    return grid

english = plot("in English", ENGLISH, VegaPalette10.RED, bold={4})
french = plot("in French", FRENCH, VegaPalette10.BLUE, {"é": "e"}, bold={3,4,5,6})
spanish = plot("in Spanish", SPANISH, VegaPalette10.GREEN, {"ó": "o", "é": "e"}, bold={4, 5, 6})

ef = english.pad((0,0,french.width-200,0), "white").place(french, (1,0))
grids = Image.from_column([ef, spanish], bg="white")

title = Image.from_text("number of letters in the name of each number from 1 to 100".upper(), sans(56, bold=True), padding=0)
img = Image.from_column([title, grids], bg="white", padding=20)
img.place(Image.from_text("/u/Udzu", sans(24), padding=10).pad((1,1,0,0), "black"), align=1, padding=10, copy=False)
img.save("output/numberwords2.png")


plot("in German", GERMAN, VegaPalette10.RED, {"ü": "u", "ö": "o", "β": "ss", "ß": "ss"}, bold={4}).remove_transparency("white").save("output/numberwords2_german.png")
plot("in Norwegian", NORWEGIAN, VegaPalette10.RED, {"å": "a", "ø": "o", "é": "e"}, bold={2,3,4}).remove_transparency("white").save("output/numberwords2_norwegian.png")
plot("in Danish", DANISH, VegaPalette10.RED, {"å": "a", "ø": "o", "é": "e"}, bold={2,3,4}).remove_transparency("white").save("output/numberwords2_danish.png")
