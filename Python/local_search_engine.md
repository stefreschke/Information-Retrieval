

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

### Apache Tika
Bei Apache Tika handelt es sich um ein Framework um Inhalte zu erkennen und zu analysieren. Es ist in der Lage Text und Metadaten aus über tausend verschiedenen Arten von Dateien zu extrahieren
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
import operator
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
    def __init__(self, url, length, id, textList):
        self.url = url
        self.length = length
        self.id = id
        self.score = 0.
        self.textList = textList
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

### buildIndex
Die Methode _buildIndex_ baut - wie der Name bereits vermuten lässt - den Index auf. Dabei dient ein Dictionary als Basis-Datenstruktur.

Der erste Schritt stellt das Iterieren über alle Directories dar. Gestartet wird bei Linux-Systemen im Root-Directory, unter Windows-Systemen muss über jede Partition iteriert werden. Als nächstes wird über alle Dateien in den Verzeichnissen iteriert. Für jede Datei wird durch python-magic ermittelt, ob es sich um ein pdf-Dokument handelt. Ist ein Dokument vom Typ _pdf_, wird mithilfe von tika der Text aus dem pdf-Dokument extrahiert. 

Für jede entdeckte pdf-Datei wird ein Zähler erhöht, welcher eine eindeutige Dokumenten-ID darstellt. Anschlißend wird mittels der Hilfsmethode _\__processText_ der Text der pdf-Dateien normalisiert. Diese Methode wird weiter unten genauer betrachtet.

Die letzten Schritte beinhalten das Anlegen eines neuen Dokumenten-Objekts, welches in das Dictionary _docHashmap_ eingefügt wird. Zudem wird die Dokumenten-ID mithilfe der Hilfsmethode  _\__addToIndex_ dem Dictionary _hasmap_ hinzugefügt, welches den eigentlichen Index enthält.


```python
def buildIndex(self):
    
    #startDirectories = self._getStartDirectories()
    startDirectories = [r"M:\Studium"]
    mime = magic.Magic(mime=True)
    
    for directory in startDirectories:
        for root, _, files in os.walk(directory):
            for file in files:
                
                path = os.path.abspath(os.path.join(root, file))
                
                try:
                    if mime.from_file(path) == "application/pdf":

                        fileData = parser.from_file(path)
                        rawText = fileData['content']
                        self.fileCount += 1
                    
                        processedText = self._preprocessText(rawText)
                        document = Document(path, len(processedText), self.fileCount, processedText)
                        self.docHashmap.update({self.fileCount : document})
                        self._addToIndex(self.fileCount, processedText)
                except:
                    continue
                    
    return

Index.buildIndex = buildIndex
```

### Hilfsmethoden
In diesem Abschnitt werden die genutzten Hilfsmethoden vorgestellt und am Code erklärt, wie die Funktionsweise implementiert wurde.

#### _getStartDirectories
Die Methode <i>\_getSartDirectories</i> liefert eine Liste der Start-Verzeichnisse, abhängig vom Betriebssystem auf dem die Suchmaschine läuft, zurück. In diesen Verzeichnissen werden nach pdf-Dateien gesucht, welche in den Index mit einfließen. Falls das zugrunde liegende Betriebssystem ein Linux-basiertes System ist, wird die Liste <i>["/"]</i> zurückgegeben, da das Verzeichnis _/_ immer das root-Verzeichnis ist. Bei auf Windows basierenden Systemen gibt es wiederrum mehrere Partitionen, welche immer mit einem Großbuchstaben abgekürtzt, und somit auch mehrere root-Verzeichnisse.

Zuerst wird geprüft welches Betriebssystem vorliegt. Bei einem auf Linux basierenden System wird einfach eine List mit dem Element _"/"_ erstellt. Bei einem auf Windows basierenden Betriebssystem ist das erstellen der Startverzeichnisse aufwendiger. Hierbei werden alle Großbuchstaben darauf geprüft eine Partition zu sein. Dies wird mithilfe der _os.path.exists_-Methode realisiert. Ist ein Großbuchstabe tatsächliche eine Partition auf dem Computer, so wird er in der Liste gespeichert. Jedoch wird an den Großbuchstaben noch der String _":\\"_ angehangen, damit die _buildIndex_-Methode mit den Elementen als Start-Verzeichnisse arbeiten kann.


```python
def _getStartDirectories(self):

    if platform.system() == "Linux":
        directories = ["/"]
        
    elif platform.system() == "Windows":
        directories = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
        
    else:
        raise EnvironmentError
        
    return directories

Index._getStartDirectories = _getStartDirectories
```

#### _addToIndex

Die Methode <i>\_addtoIndex</i> soll die Dokumenten ID zu den invertierten Index der in dem Dokument vorkommenden Terme hinzufügen. Hierfür bekommt die Methode eine Liste von Termen die in einem PDF-Dokument vorkommen und die zum Dokumente gehörige Document ID als Parameter übergeben.

Für jeden Term in der Liste _terms_ wird dazu der zum Term gehörige Eintrag im invertierten Index 

Schlägt der Versuch, die Menge für den Term _term_ aus dem Dictionary zu holen, fehl, existiert noch keine Menge. In diesem Fall wird eine neue Menge erstellt und für den Term _term_ ein Eintrag im Dictionary hinzugefügt, der auf die neu erstellte Menge referenziert.


```python
def _addToIndex(self, documentID, terms):
    
    for term in terms:
        
        try:
            docSet = self.hashmap[term]
            docSet.add(documentID)
            self.hashmap.update({term : docSet})
            
        except KeyError:
            docSet = {documentID}
            self.hashmap.update({term : docSet})
    
Index._addToIndex = _addToIndex
```

#### _preprocessText
Diese Methode dient der Vorverarbeitung der Texte, die in den pdf-Dokumenten stehen. Hierfür wird der Text eines PDF-Dokumentes an den Parameter _text_ übergeben. Als erster Schritt wird der gesamte Text in Lower-Case (Kleinschreibung) gesetzt, damit später bei der Suche die Groß- bzw. Kleinschreibung irrelevant ist. Das Ergebnis wird in der Variable _lowerText_ gespeichert.
Im nächsten Schritt werden alle Zahlen aus _lowerText_ entfernt und in _prepText_ gespeichert, da Zahlen für die Textsuche nicht von Bedeutung sind.

Als nächstes wird mithilfe der Klasse _RegexpTokenizer_, die durch die nltk-Bibliothek zur Verfügung gestellt wird, der String _prepText_ in eine Liste von Tokens aufgespalten. Was als Token gewertet wird, wird mithilfe einer _regular expression_ definiert, im Deutschen regulärer Ausdruck genannt. Ein regulärer Ausdruck ist eine Zeichenkette, welche eine Menge von bestimmten Zeichenketten beschreibt. Der gewünschte reguläre Ausdruck wird dem Konstruktor der _RegexpTokenizer_-Klasse in Form eines raw Strings übergeben. Ein raw String ist ein String, welcher mit einem _r_ am Anfang gekennzeichnet ist und ein Backslash (\\) als ein Literal behandelt und nicht als ein Escape-Zeichen. Dies ist bei regulären Ausdrücken nützlich, da in diesen viel mit Backslashes gearbeitet wird.

Im Folgenden wird der raw String bzw. reguläre Ausdruck näher betrachtet, um zu verstehen, was als ein Token gewertet wird. Der erste Teil des regulären Ausdrucks _[a-zA-Z]+-\$_ definiert alle Buchstabenketten mit einen oder mehreren Elementen, die mit einem Bindestrich enden, als Token. Die eckigen Klammern werden bei regulären Ausdrücken genutzt, um eine Zeichenauswahl zu definieren. Das bedeutet, dass ein Zeichen aus dieser Auswahl dann an dieser Stelle steht. Mithilfe von Quantoren kann definiert werden, wie viele Zeichen einer Auswahl hintereinander stehen dürfen. Das Pluszeichen ist genau so ein Quantor, welcher aussagt, dass mindestens ein oder mehrere Zeichen der Zeichenauswahl hintereinander vorkommen muss.
Das Dollarzeichen definiert das Ende einer Zeichenkette. Dadurch das ein Bindestrich vor das Dollarzeichen des regulären Ausdrucks gesetzt haben, bedeutet der reguläre Teilausdruck _-$_, dass die Zeichenkette auf einem Bindestrich endet. Bei dem |-Zeichen handelt es sich um eine logische Oderverknüpfung, die es ermöglicht, mehrere reguläre Ausdrücke zu verknüpfen. In unserem Fall _\w+_.
Der zweite reguläre Ausdruck _\w+_ definiert alle alphanumerischen Zeichenketten mit einem oder mehreren Elementen als Token. Hierbei ist _\w_ eine vordefinierte Zeichenklasse für den regulären Ausdruck <i>[a-zA-Z_0-9]</i> und beinhaltet außer alphanumerische Werte auch noch den Unterstrich. Das Pluszeichen ist hier wieder der Quantor, welcher aussagt, dass aus dieser Zeichenklasse ein oder mehrere Zeichen hintereinander vorkommen muss.
Mithilfe der _tokenize_-Methode wird der reguläre Ausdruck auf den String _prepText_ angewendet. Jeder Substring des mitgegebenen Strings, der den regulären Ausdruck erfüllt, wird an die Liste _tokenList_ angefügt.

Der Grund warum die Wörter, die auf einem Bindestrich enden, bei der Tokenerzeugen extra beachtet werden, ist der, dass die Wörter, welche bei Zeilenumbrüchen getrennt werden, wieder zusammengefügt werden sollen. In der for-Schleife werden diese Tokens auf die Eigenschaft hin, auf einem Bindestrich zu enden, geprüft und gegebenenfalls zusammengesetzt. Dazu wird der Bindestrich aus dem Token entfernt und mit dem nächsten Token in der Tokenliste verknüpft (_token[:-1]+tokenList[index+1]_). Die Tokenliste wird darauf hin aktualisiert. Der neu zusammengesetzte Token ersetzt den Token mit dem Bindestrich und der nächste Token der Liste wird gelöscht. 

Diese Methode ist jedoch nicht immer korrekt, denn es kann auch folgender Fall eintreten: Eine Zeile endet zum Beispiel mit _Damen-_ und die nächste Zeile geht mit _und Herrenschuhe_ weiter. In diesem Fall ist der Bindestrich gewollt, der Algorithmus fügt jedoch die Wörter _Damen_ und _und_ zu einem Wort zusammen. Da davon auszugehen ist, dass dieser Fall selten eintritt, wurde er aber vernachlässigt.


```python
def _preprocessText(self, text):
    
    lowerText = text.lower()
    
    prepText = re.sub(r'\d+', '', lowerText)
            
    tokenizer = RegexpTokenizer(r'[a-zA-Z]+-$|\w+')
    tokenList = tokenizer.tokenize(prepText)
    
    for token in tokenList:
        if token[-1] == '-':
            
            index = tokenList.index(token)
            compositeWord = token[:-1]+tokenList[index+1]
            tokenList[index] = compositeWord
            del tokenList[index+1]
            
    return tokenList
    
Index._preprocessText = _preprocessText
```

# retrieve
Die retrieve-Methode dient der Suche. Die Idee dabei ist, dass der Nutzer ein oder mehrere Schlagworte eingeben kann, auf deren Basis die am besten passenden Dokumente zurückgeliefert werden. Auch die Schlagworte werden den gleichen Normalisierungs-Prozess durchlaufen wie die Texte der Dokumente.

Zunächst wird der Such-String des Nutzers mittels der bereits bekannten Methode _\__preprocessText_ normalisiert. Im zweiten Schritt wird eine leere Menge angelegt, in der die Dokumenten-IDs, die zu den Termen gefunden werden, gespeichert. Mithilfe der for-Schleife wird über _processedStrings_ iteriert. Für jedes Wort wird versucht, die Menge aller Dokumenten-IDs zu dem Term _word_ aus dem Index zu beschaffen. Existiert die Menge zu dem Term _word_, wird die Vereinigung der bereits in der Menge _result_ stehenden Dokumenten-IDs und der mit dem Term _word_ gefundenen Dokumenten-IDs gebildet. Existiert der Term _word_ nicht als Key im Index, wird beim nächsten Term der Liste _processedStrings_ fortgefahren.


```python
def retrieve(self, searchString):
 
    processedStrings = self._preprocessText(searchString)
    result = set()
    df = {}
    helpDict = {}
    resultList = []
    
    for word in processedStrings:
        try:
            documents = set(self.hashmap[word])
            df[word] = len(documents)
            result = result.union(documents)
        except KeyError:
            continue
    
    for document in result:
        doc = ind.docHashmap[document]
        doc.tf_idf(processedStrings,df)
        helpDict[doc.id] = doc.score
        
    sortedDict = sorted(helpDict.items(), key=operator.itemgetter(1))
    
    for key,_ in sortedDict:
        resultList.append(ind.docHashmap[key].url)
        
    return resultList[::-1]

Index.retrieve = retrieve
```

# TF-IDF
Die tf_idf-Methode wird in die Dokumentenklasse implementiert Für die Berechnung des TF-IDF-Maßes werden folgende Werte benötigt:

- die Terme, welche gesucht werden bzw. in die Query eingegeben wurden
- für jeden Term die Anzahl der Vorkommnisse im Dokument
- für jeden Term die Anzahl der Dokumente, welche für den einen Term gefunden wurden (Document Frequency)
- die Anzahl der Dokumente in der Kollektion
- d


```python
def tf_idf(self, termList, df):
    
    tfDict = {}
    for term in termList:
        tfDict[term] = 0
    
    ind = Index()
        
    for term in self.textList:
        if term in termList:
            tfDict[term] = tfDict[term]+1

    for key, value in df.items():
        idf = math.log((ind.fileCount+1/value+1),10)
        tfDict[key] = tfDict[key]*idf
    
    self.score = sum(tfDict.values())

Document.tf_idf = tf_idf
```


```python
ind = Index()
ind.buildIndex()
```


```python
resultSet = ind.retrieve("Python Stroetmann")
if resultSet:
    for elem in resultSet:
        if elem.split('.')[1] != 'dat':
            print(elem)
```

    M:\Studium\Wissenbasierte Systeme\artificial-intelligence.pdf
    M:\Studium\Algorithmen\algorithms.pdf
    M:\Studium\Praxisbericht_2\Monitoring-LAPTOP-2NADN4MG-2.pdf
    M:\Studium\Praxisbericht_2\Monitoring.pdf
    M:\Studium\Statistik\statistik.pdf
    M:\Studium\Analysis\analysis.pdf
    M:\Studium\Praxisbericht_2\Monitoring-LAPTOP-2NADN4MG.pdf
    M:\Studium\Logik\logic.pdf
    M:\Studium\Lineare Algebra\lineare-algebra.pdf
    M:\Studium\Studienarbeit\irbookonlinereading.pdf
    M:\Studium\Java\Klausurrelevant.pdf
    M:\Studium\Java\Folien.pdf
    M:\Studium\IT-Sicherheit\Vorlesungen\2_Web_Anwendungen.pdf
    M:\Studium\Big Data\Vorlesung\BigDataAnalytics-Lecture-05.pdf
    M:\Studium\Big Data\Vorlesung\BigDataAnalytics-Lecture-04.pdf
    M:\Studium\Formale Sprachen & Automaten\KIT_Formale-Sprachen[881].pdf
    M:\Studium\Datenbanken II\2018_Book_SQLServer2017QueryPerformanceT.pdf
    M:\Studium\Praxisbericht_3\Bewertung\Drucken.pdf
    M:\Studium\Praxisbericht_3\Bewertung\Ablauf_und_Reflexion_der_Praxisphase_Teil_B.pdf
    M:\Studium\Web Engineering 2\1.2-HTTP.pdf
    
