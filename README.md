# KuberKnechte
Abgabe Kubernetes 2026

Ein Kubernetes-Stack, der dir zuverlässig sagt, warum sich Aufstehen heute nicht lohnt (passend zum letzten Semester).

- Backend: Zustandslos betriebene FastAPI-REST-API zur Bereitstellung der Datensätze.
- Frontend: Interaktive Benutzeroberfläche auf Basis von Streamlit.
- Orchestrierung: Vollständig deklaratives Helm-Deployment auf einem lokalen Kind-Cluster inklusive NGINX-Ingress-Routing.


## Setup

Lokales Deployment der Spruch-App (FastAPI Backend + Streamlit Frontend) auf einem **Kind**-Cluster via **Helm** inklusive NGINX Ingress Controller.

---

### Voraussetzungen

* Docker
* Kind
* Kubectl
* Helm

---

### Setup & Deployment Schritt für Schritt

#### 1. Kind-Cluster mit Ingress-Port-Mapping erstellen
```bash
kind create cluster --config kind-config.yaml
```
*(Verwendet [`kind-config.yaml`](./kind-config.yaml))*

---

#### 2. Docker-Images lokal bauen
Baut die Container-Images für das Backend (`spruch-backend:latest`) und Frontend (`spruch-frontend:latest`):
```bash
./build-docker-images.sh
```
*(Verwendet [`build-docker-images.sh`](./build-docker-images.sh))*

---

#### 3. Images in den Kind-Cluster laden
Überträgt die lokal gebauten Images in den internen Docker-Speicher von Kind, damit Kubernetes sie ohne externe Registry findet:
```bash
kind load docker-image spruch-frontend:latest
kind load docker-image spruch-backend:latest
```

---

#### 4. Helm Dependencies herunterladen
Lädt abhängige Sub-Charts (NGINX Ingress Controller) in den Ordner `charts/`:
```bash
helm dependency build helm/spruch-app
```
*(Verwendet [`helm/spruch-app/`](./helm/spruch-app/))*

---

#### 5. App via Helm deployen
Installiert die Anwendung, Services, ConfigMaps und Ingress-Ressourcen:
```bash
helm install kuberknechte helm/spruch-app/
```

---

#### 6. Status überprüfen
Warte, bis alle Pods (Frontend, Backend und Ingress-Controller) den Status `Running` (`1/1`) anzeigen:
```bash
kubectl get pods
```

---

### Anwendung aufrufen

Sobald alle Pods laufen, ist die Anwendung direkt im Browser erreichbar:

 **http://localhost**

---

### Aufräumen

* **Helm Release löschen:**
  ```bash
  helm uninstall kuberknechte
  ```
* **Kind-Cluster komplett entfernen:**
  ```bash
  kind delete cluster
  ```

---

## Helm als Technologie aus der CNCF-Landscape

Helm wird als zentraler Paketmanager für den gesamten Anwendungsstack genutzt ([`helm/spruch-app/`](./helm/spruch-app/)). Der Chart bündelt alle Komponenten: Backend- und Frontend-Deployments, Services, ConfigMaps sowie die Ingress-Ressource – und bindet zudem den offiziellen NGINX Ingress Controller als externe Abhängigkeit (Sub-Chart) über die [`Chart.yaml`](./helm/spruch-app/Chart.yaml) ein.

Aus folgenden Gründen ist Helm für unser Projekt sinnvoll:
- **Atomares Lifecycle-Management**: Statt dutzende statische YAML-Dateien (wie in [`deployments/`](./deployments/)) fehleranfällig einzeln auszuführen, kann der gesamte Stack mit einem einzigen Befehl deterministisch ausgerollt und sauber deinstalliert werden.
- **Dynamisches Templating**: Umgebungsspezifische Werte (z. B. Replica-Zahlen, Port-Mappings, Image-Tags) sind in der [`values.yaml`](./helm/spruch-app/values.yaml) parametrisiert und können flexibel für verschiedene Umgebungen überschrieben werden, ohne Manifeste duplizieren zu müssen.
- **Integrierte Dependency-Verwaltung**: Drittanbieter-Infrastruktur wie `ingress-nginx` wird automatisiert geladen und versionsgenau mitinstalliert.
- **Release-Tracking und Rollbacks**: Jedes Deployment ist versioniert; bei Fehlern kann der Zustand sofort und verlässlich auf eine vorherige Release-Version zurückgerollt werden.

---

## 12 Faktoren

Die folgenden Faktoren aus [12factor.net](https://12factor.net/) wurden gezielt ausgewählt, da sie den Kern der Architektur, Paketierung, Konfiguration und Skalierbarkeit unseres Stacks widerspiegeln:

- **I Codebase**
- **II Dependencies**
- **III Config**
- **VI Processes**
- **VII Port Binding**
- **VIII Concurrency**

### Detaillierte Beschreibung der Faktoren

#### 1. Faktor I: Codebase
> *"One codebase tracked in revision control, many deploys."*

* **Prinzip:** Es gibt immer eine 1:1-Zuordnung zwischen der Codebasis und der Anwendung. Aus einem gemeinsamen Versionskontrollsystem (Git) heraus werden verschiedene Deployments (lokale Entwicklung, Staging, Produktion) betrieben.
* **Umsetzung im Projekt:**
  * Die gesamte Codebasis wird in einem zentralen Repository verwaltet.
  * Sowohl das Backend ([`spruch-api/`](./spruch-api/)) als auch das Frontend ([`spruch-frontend/`](./spruch-frontend/)) teilen sich eine gemeinsame Versionshistorie, werden aber modular getrennt paketiert.
  * Durch Helm-Templates ([`helm/spruch-app/templates/`](./helm/spruch-app/templates/)) wird derselbe Code auf unterschiedliche Umgebungen ausgerollt.

---

#### 2. Faktor II: Dependencies
> *"Explicitly declare and isolate dependencies."*

* **Prinzip:** Eine Applikation darf sich niemals auf das implizite Vorhandensein systemweiter Pakete verlassen. Alle Abhängigkeiten müssen exakt deklariert und isoliert werden.
* **Umsetzung im Projekt:**
  * Saubere Definition aller Bibliotheken über die Projektdateien ([`spruch-api/pyproject.toml`](./spruch-api/pyproject.toml) und [`spruch-frontend/pyproject.toml`](./spruch-frontend/pyproject.toml)) (z. B. `fastapi`, `pydantic-settings`, `streamlit`).
  * Deterministische Builds durch Lockfiles ([`spruch-api/uv.lock`](./spruch-api/uv.lock) und [`spruch-frontend/uv.lock`](./spruch-frontend/uv.lock)) mit exakten Checksummen (Hashes) und Versionen.
  * Die Container-Builds ([`spruch-api/Dockerfile`](./spruch-api/Dockerfile) und [`spruch-frontend/Dockerfile`](./spruch-frontend/Dockerfile)) isolieren die Laufzeitumgebung vollständig und synchronisieren deterministisch via `uv sync --frozen --no-cache`.

---

#### 3. Faktor III: Config
> *"Store config in the environment."*

* **Prinzip:** Alles, was sich zwischen Deployments (Dev, Test, Staging, Prod) unterscheidet, ist Konfiguration und gehört **nicht** in den Source Code, sondern in Umgebungsvariablen.
* **Umsetzung im Projekt:**
  * **Backend:** Steuert Dateipfade und Umgebungsmodus über `IS_PROD` und `QUOTE_PATH` in [`spruch-api/settings.py`](./spruch-api/settings.py) via Pydantic Settings.
  * **Frontend:** Ermittelt den API-Endpunkt flexibel über die Variable `QUOTE_ENDPOINT_URL` in [`spruch-frontend/utils.py`](./spruch-frontend/utils.py) (`http://spruch-ip-svc/quote` im Cluster oder `.env` lokal).
  * **Kubernetes/Helm:** Trennung von Code und Konfiguration durch ConfigMaps ([`deployments/spruch-config.yaml`](./deployments/spruch-config.yaml) bzw. [`helm/spruch-app/templates/configmap.yaml`](./helm/spruch-app/templates/configmap.yaml)) und Parameter-Injektion via Helm [`helm/spruch-app/values.yaml`](./helm/spruch-app/values.yaml).

---

#### 4. Faktor VI: Processes
> *"Execute the app as one or more stateless processes."*

* **Prinzip:** Anwendungen müssen als zustandslose (stateless) Prozesse laufen. Daten, die persistent gespeichert werden müssen, gehören in externe Backing-Services (Datenbanken, S3-Storage).
* **Umsetzung im Projekt:**
  * Sowohl das FastAPI-Backend ([`spruch-api/main.py`](./spruch-api/main.py)) als auch das Frontend ([`spruch-frontend/main.py`](./spruch-frontend/main.py)) halten keinen internen Session-Status auf Pod-Ebene.
  * Jeder API-Call (`GET /quote`) liefert unabhängig Daten zurück.
  * Dadurch können Pods im Cluster jederzeit neu gestartet, verschoben oder terminiert werden, ohne dass Datenverlust auftritt.

---

#### 5. Faktor VII: Port Binding
> *"Export services via port binding."*

* **Prinzip:** Die Anwendung ist vollständig autark und bringt ihren eigenen HTTP-Server mit, anstatt in einen externen Webserver (wie Apache Tomcat o. ä.) injiziert zu werden.
* **Umsetzung im Projekt:**
  * **Backend:** Exportiert den REST-Endpunkt direkt über Uvicorn / FastAPI auf Port `80` (definiert im [`spruch-api/Dockerfile`](./spruch-api/Dockerfile)).
  * **Frontend:** Streamlit bindet direkt an Port `8501` (definiert im [`spruch-frontend/Dockerfile`](./spruch-frontend/Dockerfile)).
  * Das Routing und Load Balancing wird außerhalb der Applikation deklarativ durch Kubernetes Services ([`deployments/spruch-ip-svc.yaml`](./deployments/spruch-ip-svc.yaml), [`deployments/spruch-np-svc.yaml`](./deployments/spruch-np-svc.yaml)) und den NGINX-Ingress-Controller ([`helm/spruch-app/templates/ingress.yaml`](./helm/spruch-app/templates/ingress.yaml)) gesteuert.

---

#### 6. Faktor VIII: Concurrency
> *"Scale out via the process model."*

* **Prinzip:** Skalierung erfolgt nicht über das Aufblähen einzelner Prozesse (Vertikal), sondern durch das Hinzufügen weiterer Prozess-Instanzen (Horizontal / Scale-Out).
* **Umsetzung im Projekt:**
  * In den Deployment-Spezifikationen ([`deployments/spruch-deployment-be-v1.yaml`](./deployments/spruch-deployment-be-v1.yaml), [`deployments/spruch-deployment-fe-v1.yaml`](./deployments/spruch-deployment-fe-v1.yaml) sowie [`helm/spruch-app/values.yaml`](./helm/spruch-app/values.yaml)) ist die Skalierung deklarativ auf `replicaCount: 3` gesetzt.
  * Das System kann unter Last problemlos über `kubectl scale` oder Horizontale Pod-Autoscaler (HPA) dynamisch vervielfacht werden.