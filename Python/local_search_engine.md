

```python
from IPython.core.display import HTML, display
display(HTML('<style>.container { width:100%; !important } </style>'))
```


<style>.container { width:100%; !important } </style>


# Beispiel-Implementierung: Lokale Suchmaschine

## Ziel der Beispiel-Implementierung
Im Folgenden wird eine Anwendung der zuvor theoretisch diskutierten Inhalte vorgestellt. Dabei soll eine lokale Suchmaschine entwickelt werden, welche in der Lage ist, pdf-Dateien auf einem lokalen Computer-System zu parsen, in einen invertierten Index aufzunehmen sowie Suchanfragen eines Benutzers sinnvoll zu beantworten. <br>
Zur Relevanz-Bestimmung der Dokumente wird das TF-IDF-Maß, welches bereits vorgestellt wurde, genutzt. Um den Index zu speichern, wird die von Python mitgelieferte Datenstruktur "dictionary", welche im Grunde eine Hashmap ist, genutzt.
Weiter werden einige Bibliotheken eingesetzt, welche einige Vorarbeit leisten und damit den Code der Beispiel-Implementierung auf das Wesentliche beschränken. So soll die grundlegende Arbeitsweise eines Information Retrieval-Systems dargelegt werden.

## Genutzte Bibliotheken
Bevor mit der eigentlichen Implementierung der lokalen Suchmaschine begonnen werden kann, müssen einige Bibliotheken eingebunden werden. Darunter fallen Apache Tika, das Math-Modul von Python, os (um auf die Directories zugreifen zu können), python-magic, regular expressions (re) (und noch weitere, bei Bedarf einfügen!). <br>

### Tika
Tika liefert eine Parser, mit dessen Hilfe der Text aus - unter anderem - pdf-Dateien extrahiert werden kann.
Mit dem Aufruf _parser.from_\__file(file)_ kann eine pdf-Datei in reinen Text umgewandelt werden. Die Funktion liefert ein Dictionary zurück, welches einen Key _content_ besitzt, über den auf den Inhalt der pdf-Datei zugegriffen werden kann.

### python-magic
Mittels python-magic ist es möglich, unabhängig von der Dateiendung, den Typ einer Datei zu ermitteln. Dies hat den Vorteil, dass die Suchmaschine sowohl unter Windows, als auch unter Unix-Systemen, alle pdf-Dateien finden kann, da unter Unix die Dateiendung keine garantierten Rückschlüsse auf den Typ der Datei zulässt.

### nltk
Die Bibliothek nltk (natural language toolkit) wird verwendet, um die Eingabetexte der Dokumente und die Eingaben des Nutzers zu normalisieren. Zudem wird Stemming mithilfe von nltk durchgeführt, um Wörter auf ihren Wortstamm zurückzuführen. In den unteren Methoden wird näheres über die genutzten Operationen erläutert.



```python
from tika import parser
import magic
import math
import os
import string
import platform
import re
from nltk.tokenize import RegexpTokenizer
```

## Die Document-Klasse
Das Speichern er für das Retrieval wichtigen Informationen, geschieht mittels einer Document-Klasse. Diese Klasse hält alle Attribute, die wichtig sind, um das TF-IDF-Maß berechnen zu können. Diese Attribute sind:
- url
- length
- id

Die Variable _url_ ist ein String und enthält den Pfad zum Dokument, welches durch das entsprechende Document-Objekt repräsentiert wird. _length_ ist ein Integer und beinhaltet die Anzahl der Wörter, die in dem Dokument vorkommen und _id_ ist die eindeutige Dokumenten-ID, zu der weiter unten noch genaueres gesagt wird.


```python
class Document:
    def __init__(self, url, length, id):
        self.url = url
        self.length = length
        self.id = id
        self.score = {}
```

## Der Index
Nachdem die benötigten Bibliotheken bekannt sind, kann der Index implementiert werden. Bevor dieser jedoch aufgebaut werden kann, sind einige Vorarbeiten nötig, die durch die vorgestellten Bibliotheken gestützt werden.
Der Index wird im Folgenden als Klasse implementiert. Diese beinhaltet die folgenden Methoden, die in den folgenden Abschnitten genauer diskutiert werden:
- buildIndex()
- retrieve()
- calcTFIDF()

Weiter werden die folgenden Member-Variablen benötigt:
- hashmap
- fileCount
- docHashmap

Die Member-Variable _hashmap_ ordnet allen Termen eine Menge von eindeutigen Dokumenten-IDs zu, in denen sie vorkommen. Im Dictionary _docHashmap_ werden die Dokuemnten-IDs als Key genutzt, um eine Zurodnung von Dokumenten-IDs auf Document-Objekte zu ermöglichen. Die Variable _fileCount_ ist ein Integer und wird für jedes gefundene Dokument um _1_ hochgezählt. Damit ist diese Variable qualifiziert als eindeutige Dokumenten-ID zu fungieren, wofür sie genutzt wird.



```python
class Index:
    hashmap = {} #dictionary
    fileCount = 0 #integer, Gesamtzahl aller gefunden Dateien
    docHashmap = {}
```

## buildIndex
Die Methode _buildIndex_ baut - wie der Name bereits vermuten lässt - den Index auf. Dabei dient ein Dictionary als Basis-Datenstruktur.

Der erste Schritt stellt das Iterieren über alle Directories dar. Gestartet wird bei Linux-Systemen im Root-Directory, unter Windows-Systemen muss über jede Partition iteriert werden. Als nächstes wird über alle Dateien in den Verzeichnissen iteriert. Für jede Datei wird durch python-magic ermittelt, ob es sich um ein pdf-Dokument handelt. Ist ein Dokument vom Typ _pdf_, wird mithilfe von tika der Text aus dem pdf-Dokument extrahiert. 

Für jede entdeckte pdf-Datei wird ein Zähler erhöht, welcher eine eindeutige Dokumenten-ID darstellt. Anschlißend wird mittels der Hilfsmethode _\__processText_ der Text der pdf-Dateien normalisiert. Diese Methode wird weiter unten genauer betrachtet.

Die letzten Schritte beinhalten das Anlegen eines neuen Dokumenten-Objekts, welches in das Dictionary _docHashmap_ eingefügt wird. Zudem wird die Dokumenten-ID mithilfe der Hilfsmethode  _\__addToIndex_ dem Dictionary _hasmap_ hinzugefügt, welches den eigentlichen Index enthält.


```python
def buildIndex(self):
    # alle Start-Verzeichnisse holen
    #start = self._getStartDirectories()
    #start = ["F:/Jonas/Uni"]
    start = ["C:/Users/marle/OneDrive/Studium"]
    # Magic-Instanz erstellen, um Datei-Typ bestimmen zu können
    mime = magic.Magic(mime=True)
    
    for s in start:
        for root, _dir, files in os.walk(s):
            for f in files:
                path = os.path.abspath(os.path.join(root, f))
                try:
                    if mime.from_file(path) == "application/pdf":
                        #print("pdf")
                    # in Text umwawndeln und tokenization durchführen
                        #print(path)
                        fileData = parser.from_file(path)
                        rawText = fileData['content']
                        self.fileCount += 1
                    
                        processedText = self._preprocessText(rawText)
                        document = Document(path, len(processedText), self.fileCount)
                        self.docHashmap.update({self.fileCount : document})
                        self._addToIndex(self.fileCount, processedText)
                except:
                    continue
                    
    return

Index.buildIndex = buildIndex
```

### Hilfsmethoden
In diesem Abschnitt werden die genutzten Hilfsmethoden kurz vorgestellt. Diese werden jedoch nicht in der Tiefe behandelt, wie die drei Haupt-Methoden behandelt werden. 

#### _getStartDirectories
Die Methode _\__getSartDirectories_ liefert eine Liste zurück, welche abhängig vom Betriebssystem, auf dem die Suchmaschine läuft, die Start-Verzeichnisse zurückgibt, in denen nach pdf-Dateien gesucht werden soll. Falls das zugrunde liegende Betriebssystem ein Linux-basiertes System ist, wird die Liste __["/"]__ zurückgegeben, falls ein Windows-System zugrundeliegt, wird die Liste aller Partitionen zurückgegeben.


```python
def _getStartDirectories(self):
    start = []
    
    if platform.system() == "Linux":
        start.append("/")
    elif platform.system() == "Windows":
        start = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    else:
        raise EnvironmentError
        
    return start

Index._getStartDirectories = _getStartDirectories
```

#### _addToIndex

Diese Methode bekommt als Argumente eine Liste von Termen, die in einem pdf-Dokument vorkommen. Zudem wird eine eindeutige Dokumenten-ID übergeben.

Für jeden Term in _terms_ wird versucht, eine Menge mit Dokumenten-IDs aus dem Index zu holen. Existiert bereits eine Menge, wird kein Fehler geworfen.

Schlägt der Versuch, die Menge für den Term _term_ aus dem Dictionary zu holen, fehl, existiert noch keine Menge. In diesem Fall wird eine neue Menge erstellt und für den Term _term_ ein Eintrag im Dictionary hinzugefügt, der auf die neu erstellte Menge referenziert.


```python
def _addToIndex(self, documentID, terms):
    for t in terms:
        try:
            docs = self.hashmap[t]
            docs.add(documentID)
            self.hashmap.update({t : docs})
        except KeyError:
            docs = {documentID}
            self.hashmap.update({t : docs})
    
Index._addToIndex = _addToIndex
```

#### _preprocessText
Diese Methode dient der Vorverarbeitung der Texte, die in den pdf-Dokumenten stehen. Als erster Schritt wird der gesamte Text in Lower-Case gesetzt, damit bei der Suche später die Groß- bzw. Kleinschreibung unwichtig ist.
Im nächsten Schritt werden alle Zahlen aus dem Text entfernt.

Als nächstes wird mithilfe der Klasse _RegexpTokenizer_, die die nltk-Bibliothek mitliefert, der String _txt_ in eine Liste von Tokens aufgespalten. Was als Token gewertet wird, wird mithilfe einer _regular expression_ definiert, die dem Konstruktor des _RegexpTokenizer_ mitgegeben. Mithilfe der _tokenize_-Methode wird die _regular expression_ auf den übergebenen String angewendet. Jeder Substring des mitgegebenen Arguments, der die _regular expression_ erfüllt, wird einer Liste angefügt. Diese Liste enthält am Ende der Verarbeitung alle Substrings von _txt_, die nur Buchstaben enthalten oder nur Buchstaben enthalten und mit einem Bindestrich (-) enden. 

Der Bindestrich ist wichtig, da mit dessen Hilfe, alle Wörter gefunden werden können, die im Text aufgrund eines Zeilenumbruchs getrennt wurden. Diese Wörter werden innerhlab der for-Schleife zusammengefügt und der Bindestrich wird entfernt.

Diese Methode ist jedoch nicht immer korrekt, denn es kann auch folgender Fall eintreten: Eine Zeile endet mit z.B. Damen-, die nächste Zeile geht mit z.B. und Herrenschuhe weiter. In diesem Fall ist der Bindestrich gewollt, der Algorithmus fügt jedoch die Wörter _Damen_ und _und_ zu einem Wort zusammen. Da dieser Fall jedoch sehr selten auftritt, wird in Kauf genommen, dass ab und zu die Wörter falsch zusammengefügt werden.


```python
def _preprocessText(self, txt):
    # lower all:
    txt = txt.lower()
    
    # remove digits
    txt = re.sub(r'\d+', '', txt)
            
    # tokenize the text
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+-$|\w+')
    result = tokenizer.tokenize(txt)
    
    # concatenate divided words
    for word in result:
        if word[-1] == '-':
            ind = result.index(word)
            corrected = word[:-1]+result[ind+1]
            result[ind] = corrected
            del result[ind+1]
    return result
    
Index._preprocessText = _preprocessText
```

#### retrieve
Die retrieve-Methode dient der Suche. Die Idee dabei ist, dass der Nutzer ein oder mehrere Schlagworte eingeben kann, auf deren Basis die am besten passenden Dokumente zurückgeliefert werden. Auch die Schlagworte werden den gleichen Normalisierungs-Prozess durchlaufen wie die Texte der Dokumente.

Zunächst wird der Such-String des Nutzers mittels der bereits bekannten Methode _\__preprocessText_ normalisiert. Im zweiten Schritt wird eine leere Menge angelegt, in der die Dokumenten-IDs, die zu den Termen gefunden werden, gespeichert. Mithilfe der for-Schleife wird über _processedStrings_ iteriert. Für jedes Wort wird versucht, die Menge aller Dokumenten-IDs zu dem Term _word_ aus dem Index zu beschaffen. Existiert die Menge zu dem Term _word_, wird die Vereinigung der bereits in der Menge _result_ stehenden Dokumenten-IDs und der mit dem Term _word_ gefundenen Dokumenten-IDs gebildet. Existiert der Term _word_ nicht als Key im Index, wird beim nächsten Term der Liste _processedStrings_ fortgefahren.


```python
def retrieve(self, searchString):
    # pre-processing
    processedStrings = self._preprocessText(searchString)
    result = set()
    for word in processedStrings:
        try:
            documents = set(self.hashmap[word])
            result = result.union(documents)
        except KeyError:
            continue
    return result

Index.retrieve = retrieve
```


```python
ind = Index()
ind.buildIndex()
```


```python

```

# Probleme

- er findet *.dat-Dateien
- Kontext der Wörter nicht einbezogen
- Vereinigung der Ergebnismengen sorgen dafür, dass Ergebnisse für $t_1 \cup t_2 \cup .. \cup t_n$ zurückgegeben werden -> kann durch Gewichtung verbessert/umgangen werden
- kein Stemming bisher
- Queries mit einem Buchstaben finden viele Dokumente (vor allem Formeln etc.) -> durch Stemming gelöst, falls nicht gewollt

- Index.build() braucht sehr lange -> parallelisieren?
- Index muss jedes Mal neu aufgebaut werden -> via Pickle, JSON oder XML speichern und ziehen bei Start des Programms


```python
def tf_idf(self, searchString):
    tfDict = {}
    ind = Index()
    termList = ind._preprocessText(searchString)
    for term in termList:
        tfDict[term] = 0
        
    fileData = parser.from_file(self.url)
    rawText = fileData['content']
    rawTextList = ind._preprocessText(rawText)
    
    for term in rawTextList:
        if term in termList:
            tfDict[term] = tfDict[term]+1
            
    self.score = tfDict

Document.tf_idf = tf_idf
```


```python
resultSet = ind.retrieve("information retrieval")
#for result in resultSet:
    #print(ind.docHashmap[result].url)
for document in resultSet:
    doc = ind.docHashmap[document]
    doc.tf_idf("information retrieval")
    print(doc.score)
```

    {'information': 16, 'retrieval': 1}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 0, 'retrieval': 1}
    {'information': 4, 'retrieval': 0}
    {'information': 0, 'retrieval': 5}
    {'information': 6, 'retrieval': 0}
    {'information': 4, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 5, 'retrieval': 0}
    {'information': 13, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 8, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 444, 'retrieval': 54}
    {'information': 2, 'retrieval': 0}
    {'information': 5, 'retrieval': 0}
    {'information': 8, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 5, 'retrieval': 0}
    {'information': 3, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 6, 'retrieval': 0}
    {'information': 6, 'retrieval': 0}
    {'information': 3, 'retrieval': 0}
    {'information': 5, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 3, 'retrieval': 0}
    {'information': 6, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 15, 'retrieval': 1}
    {'information': 3, 'retrieval': 0}
    {'information': 15, 'retrieval': 0}
    {'information': 16, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 3, 'retrieval': 0}
    {'information': 595, 'retrieval': 711}
    {'information': 4, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 2, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    {'information': 154, 'retrieval': 1}
    {'information': 1, 'retrieval': 0}
    {'information': 1, 'retrieval': 0}
    


```python

```
