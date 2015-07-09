<p align="center">
 <img src="https://github.com/kps85/PPSN/blob/master/twittur/static/img/twittur_logo.JPG" alt="twittur - your TUcial network" width="200">
</p>
##**twittur** - *your TUcial network*

######**AUFGABENSTELLUNG**
>*Die SeminarteilnehmerInnen entwickelen eine social-networking Plattform basierend auf einem Webframework einer objekt-orientierten Sprache. Das Projektmanagement basiert auf modernen Praktiken agiler Softwareentwicklung und es sollen typische Werkzeuge aus der Welt der Open Source Entwicklung verwendet werden.*

--

######**ZIEL DES PROJEKTS**
>*Das Team entwickelt im Rahmen eines CIT-Moduls an der TU Berlin binnen neun Wochen ein Social-Network. Das System basiert im Allgemeinen auf der Struktur der TU Berlin und achtet auf festgelegte Sicherheitsrichtlinien. Es wird unter zu Hilfe nahme der Programmiersprache Python, dem Web-Framework Django und Twitter Bootstrap umgesetzt.*

--

######**DAS PROJEKTTEAM**
Rolle | Arbeitsbereich bzw. Funktionsrolle | Vertreter
:----- | :---------------------------------- | :---------
Projektleiter | PO, Projekt-Organisation | Marian Scherz
Wissenschaftlicher Mitarbeiter | Projekt-Koordination | Tim Jungnickel
Wissenschaftlicher Mitarbeiter | Projekt-Unterstützung | Anton Gulenko
 |  | 
Wirtschaftsinformatiker | Scrum-Master, Produkt-Entwicklung | Karl Schmidt
Wirtschaftsinformatiker | Produkt-Entwicklung | Lilia Butenkova
Wirtschaftsinformatiker | Produkt-Entwicklung, Dokumentation | Thomas Tietz
Wirtschaftsinformatiker | Produkt-Entwicklung | Steffen Zerbe
Informatiker | Produkt-Entwicklung, Backend | Willy Cai
Wirtschaftsinformatiker | Produkt-Entwicklung, Dokumentation | Yiming Chen
 |  | 
Wirtschaftsinformatiker, Informatiker | Produkt-Anbindung, Tests | Komillitonen, Studenten

--

######**DIE PROJEKT-INFRASTRUKTUR**
* [Google Sheet] (https://goo.gl/gzIMiu)
 - Diagramme (Kontextmodell, Use-Cases, Klassendiagramm, ...)
 - Dokumentation (Protokoll Meetings)
 - Stakeholderliste
 - Anforderungskatalog
  - `REQ Nr.` entspricht der `Issue ID` in Waffle.io
 - Datenobjektliste (still empty)
 - Glossar (still empty)
* [GitHub Repository 'PPSN'] (https://goo.gl/pAsqLV)
 - readme dient dem Überblick aller relevanten Informationen zum Projekt
 - 'master'-Branch wird zu den entsprechenden Meetings aktualisiert
 - eventuell wird Google Sheet noch in die Projekt Wiki übertragen
* [Waffle.io Issue Organisation] (https://goo.gl/reOBQO)
 - Backlog column dient als Product Backlog
 - Ready column dient als Sprint Backlog
 - `Issue ID` entspricht der `REQ NR.` im Google Sheet
 - **Issue Struktur**: `Titel` = Story = Anforderung aus dem Google Sheet; `Description` = Tasks; `Comments` = Changelog (erledigte Tasks, Änderungen an Story und / oder Tasks)
 - entsprechende Meilensteine sind die zweiwöchigen Präsentationen
* Zur Kommunikation wird 'slack.com' verwendet

--

######**INSTALLATION**
01. Python installieren. (https://www.python.org/doc/)  
   *Auf gesetzte Umgebungsvariabeln achten!*
02. Django installieren (https://docs.djangoproject.com/en/1.8/intro/install/)
03. Gepacktes Repository in gewünschten Ordner entpacken.  
   (ZIP: https://github.com/kps85/PPSN/archive/master.zip)
04. Kommandozeile mit Administratorrechten ausführen.
05. Pillow installieren. (Kommandozeile: `pip install pillow` )
06. Mittels Kommandozeile in den Ordner des entpackten Projekts wechseln, in dem sich die `manage.py` befindet.
07. Folgende Befehler in derselben Reihenfolge ausführen:  
   - `python manage.py makemigrations`    
   - `python manage.py migrate`    
   - `python manage.py runserver`    
08. Im Browser auf die Seite `http://localhost:8000/twittur/install/` gehen
09. Ein gültiges Admin-Passwort und eine gültige TU Berlin E-Mail Adresse angeben und auf `Senden` klicken.
10. Den Admin-Account über den Link, der per E-Mail an die angegebene Adresse geschickt wurde, aktivieren.
11. **Herzlichen Glückwunsch, Sie können jetzt twittur verwenden!**

*In der `views_api.py` können Studiengänge und Co im Dictionary `grp_list` angepasst werden.*

--

<p align="center">
 <img src="https://github.com/kps85/PPSN/blob/master/twittur/static/img/cit_logo.jpg" alt="Complex and Distributed IT Systems" width="100">
</p>

Ein Projekt im Rahmen des [Fachgebiet Komplexe und verteilte IT-Systeme] (https://www.cit.tu-berlin.de/) der TU Berlin. Geplant und entwickelt im Sommersemester 2015.

Das TwitTUr-Logo findet im Rahmen dieses Projektes Verwendung. Es dient lediglich der Identifikation dessen und keinem wirtschaftlichen oder kommerziellen Zwecke.

Icon made by Freepik from www.flaticon.com is licensed under CC BY 3.0. http://www.flaticon.com/free-icon/toucan-tropical-bird_47351 (17.05.2015, 10:52Uhr)
