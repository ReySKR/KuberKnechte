# KuberKnechte
Abgabe Kubernetes 2026

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

---

#### 2. Docker-Images lokal bauen
Baut die Container-Images für das Backend (`spruch-backend:latest`) und Frontend (`spruch-frontend:latest`):
```bash
./build-docker-images.sh
```

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

---

#### 5. App via Helm deployen
Installiert die Anwendung, Services, ConfigMaps und Ingress-Ressourcen:
```bash
helm install spruch-app helm/spruch-app/
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
  helm uninstall spruch-app
  ```
* **Kind-Cluster komplett entfernen:**
  ```bash
  kind delete cluster
  ```
