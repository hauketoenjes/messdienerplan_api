# Messdienerplan API

Eine in Django umgesetzte REST-API zum Verwalten und generieren von Messdienerplänen. Ein Webinterface passend zur API
kann hier gefunden werden: [messdienerplan_webinterface](https://github.com/hauketoenjes/messdienerplan_webinterface).

## Installation

### Docker / docker-compose

Bei jedem commit in dieser Repository wird automatisch von einer GitHub Action ein Docker Container gebaut, der in der
GitHub Container Registry hochgeladen wird und verwendet werden kann. Um diesen mit einer Datenbank zu verwenden, sollte
die
`docker-compose.yml` verwendet werden.

#### 1. Voraussetzungen

- Docker muss installiert sein (Informationen zur Installation unter: [Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose muss installiert sein (Informationen zur Installation
  unter: [Install Docker Compose](https://docs.docker.com/compose/install/))

#### 2. `docker-compose.yml` und `sample.env` herunterladen und vorbereiten

In den Ordern wechseln, wo die Datenbankdateien und die compose abgelegt werden sollen.

```shell
$ mkdir messdienerplan-api && cd messdienerplan-api
```

`docker-compose.yml` und `sample.env` herunterladen (Per Befehl oder per Browser Download).

```shell
$ wget \
  https://raw.githubusercontent.com/hauketoenjes/messdienerplan_api/main/docker-compose.yml \
  https://raw.githubusercontent.com/hauketoenjes/messdienerplan_api/main/sample.env
```

`sample.env` in `.env` umbenennen (Damit sie gelesen werden kann)

```shell
$ mv sample.env .env
```

`.env` im Editor öffnen und Variablen füllen. Weiter Informationen zu den benötigten Variablen stehen in der `.env`
oder `sample.env` Datei.

```shell
$ nano .env
```

#### 3. Hinweise für den Einsatz in Produktion

- Es wird empfohlen nicht den Docker-Tag `latest` als Version für die MariaDB Datenbank zu verwenden, da nicht abzusehen
  ist, ob es in Zukunft Änderungen an der API oder Sonstige Breaking Changes gibt.

  Weiter Informationen über die verfügbaren Versionen (Tags) für das MariaDB Docker Image findet man
  hier: [Docker Hub](https://hub.docker.com/_/mariadb)

  Um die Version zu ändern, muss der `latest` Tag in der `docker-compose.yml` geändert werden.

#### 4. Starten der docker-compose

Um die Docker Container zu starten, muss folgender Befehl im Verzeichnis mit der in Schritt 2
heruntergeladenen `docker-compose.yml` ausgeführt werden:

`-d` für den detached mode, um die Container im Hintergrund laufen zu lassen. Kann auch zu Debug Zwecken weggelassen
werden, weil die Logs Ausgaben dann direkt in der Console landen.

```shell
$ docker-compose up -d
```

Django legt jetzt automatisch das Datenbankschema an, erstellt den Superuser und startet den Server.

- Der Server ist dann auf `http://localhost:8080` erreichbar.
- Der Admin-Login ist unter `http://localhost:8080/admin` zu finden

#### Eventuelle Probleme bei der Installation

- Die Datenbank braucht eine gewisse Zeit beim ersten Start des Stacks. Es kann passieren, dass Django dann einen
  Verbindungsabbruch bekommt und die Datenbank nicht initialisieren kann. Um das zu verhindern, sollte die Datenbank vor
  Django gestartet werden. Das Problem tritt meistens nur beim allerersten Start des Stacks auf. Danach kann man das
  ganze Projekt gemeinsam starten.

## API-Dokumentation

TODO





