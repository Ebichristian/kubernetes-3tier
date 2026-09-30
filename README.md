# Kubernetes 3-Tier Application

## 1. Project Overview

This project demonstrates deployment of a 3-tier application on Kubernetes using Minikube.

The application consists of:

* React frontend
* Flask backend
* PostgreSQL database
* Nginx as the entry point
* Kubernetes Services for communication
* PersistentVolume/PersistentVolumeClaim for database persistence
* Kubernetes Secret for database credentials
* GitHub Actions for CI/CD

## 2. Architecture

```text
                         User
                          |
                          v
                  Nginx NodePort :30510
                          |
                +---------+---------+
                |                   |
                v                   v
        frontend-service      backend-service
                |                   |
                v                   v
           React Pod          Flask Pods (3)
                                    |
                                    v
                           postgres-service:5432
                                    |
                                    v
                            PostgreSQL Pod
                                    |
                                    v
                              postgres-pvc
                                    |
                                    v
                              PersistentVolume
```

## 3. Project Structure

```text
kubernetes-3tier/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   ├── src/
│   └── start.sh
│
├── backend/
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── k8s/
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── nginx-config.yaml
│   ├── nginx-deployment.yaml
│   ├── nginx-service.yaml
│   ├── postgres-deployment.yaml
│   ├── postgres-pvc.yaml
│   └── postgres-service.yaml
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml
│
└── .gitignore
```

`postgres-secret.yaml` is intentionally excluded from Git because it contains database credentials.

## 4. Minikube Cluster

The application is deployed on a local Minikube cluster.

The backend application was scaled to 3 replicas and Kubernetes scheduled the Pods across the available Minikube nodes.

Check the cluster:

```bash
kubectl get nodes -o wide
```

Check all application Pods:

```bash
kubectl get pods -o wide
```

## 5. Kubernetes Deployments

The project uses separate Deployments for:

* Backend
* Frontend
* Nginx
* PostgreSQL

Check:

```bash
kubectl get deployments
```

Example backend scaling:

```bash
kubectl scale deployment backend-deployment --replicas=3
```

## 6. Kubernetes Services

Services provide stable networking between Pods.

### Frontend

```text
frontend-service:3000
```

### Backend

```text
backend-service:5000
```

### PostgreSQL

```text
postgres-service:5432
```

### Nginx

Nginx is exposed through NodePort:

```text
nginx-service
NodePort: 30510
```

Check services:

```bash
kubectl get svc
```

## 7. Nginx Routing

Nginx acts as the entry point.

Requests are routed as follows:

```text
/
  -> frontend-service:3000

/api/
  -> backend-service:5000
```

The backend Flask application exposes:

```text
/
  -> Flask App Running...
```

Therefore a request to:

```text
/api/
```

through Nginx is forwarded to the Flask `/` endpoint.

## 8. PostgreSQL Database

PostgreSQL runs inside the Kubernetes cluster.

The Flask application connects to PostgreSQL using the Kubernetes Service:

```text
postgres-service:5432
```

The application uses:

```text
DATABASE_URL
```

to connect to the database.

The Flask application periodically checks the database connection and logs:

```text
[DB STATUS] connected
```

## 9. Persistent Storage

Database data is stored using a PersistentVolumeClaim.

```text
PostgreSQL
    |
    v
postgres-pvc
    |
    v
PersistentVolume
```

Check the PVC:

```bash
kubectl get pvc
```

Expected:

```text
STATUS: Bound
```

The database persistence was tested by creating data, deleting the PostgreSQL Pod, allowing Kubernetes to recreate it, and checking the data again.

The data remained available after the Pod recreation.

## 10. Kubernetes Secret

Database credentials are stored in the Kubernetes Secret:

```text
postgres-secret
```

The Secret contains:

```text
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL
```

The application Deployment references the Secret:

```yaml
envFrom:
  - secretRef:
      name: postgres-secret
```

The Flask application reads the connection string using:

```python
os.getenv("DATABASE_URL")
```

The Secret file containing the real credentials is excluded from Git using `.gitignore`.

Check the Secret:

```bash
kubectl get secret postgres-secret
```

## 11. Application to Database Communication

The complete communication flow is:

```text
Nginx
  |
  v
backend-service
  |
  v
Flask
  |
  v
DATABASE_URL
  |
  v
postgres-service:5432
  |
  v
PostgreSQL
```

This confirms that Kubernetes Service DNS names are used instead of Pod IP addresses.

## 12. Docker Images

Backend image:

```text
ebichristian/flask-ci:<commit-sha>
```

Frontend image:

```text
ebichristian/react-ci:<commit-sha>
```

The Git commit SHA is used as the image tag so that the deployed image can be traced back to the source commit.

## 13. GitHub Repository

The source code, Dockerfiles, Kubernetes manifests, and GitHub Actions workflow are stored in the GitHub repository:

```text
https://github.com/Ebichristian/kubernetes-3tier
```

The following are intentionally excluded:

```text
node_modules/
build/
venv/
actions-runner/
k8s/postgres-secret.yaml
.env
```

## 14. GitHub Actions CI/CD

A self-hosted GitHub Actions runner is configured on the Ubuntu machine because Minikube is running locally on that machine.

The CI/CD flow is:

```text
Developer
   |
   | git push
   v
GitHub Repository
   |
   v
GitHub Actions
   |
   v
Self-hosted Runner
   |
   +--> Checkout code
   |
   +--> Build Flask Docker image
   |
   +--> Build React Docker image
   |
   +--> Load images into Minikube
   |
   +--> Apply Kubernetes manifests
   |
   +--> Update Deployment images
   |
   +--> Check rollout status
   |
   +--> Run application smoke tests
   |
   v
Kubernetes
```

The workflow is triggered whenever code is pushed to the `main` branch.

## 15. Pod Failure Test

A backend Pod was intentionally deleted:

```bash
kubectl delete pod <backend-pod-name>
```

The Deployment/ReplicaSet automatically created a replacement Pod.

This demonstrated Kubernetes self-healing.

Verify:

```bash
kubectl get pods -l app=backend
```

## 16. Application Scaling Test

The backend was scaled from 1 replica to 3 replicas:

```bash
kubectl scale deployment backend-deployment --replicas=3
```

Verify:

```bash
kubectl get deployment backend-deployment
```

The backend Service then showed three endpoints.

## 17. Database Persistence Test

A test table was created:

```text
persistence_test
```

Data was inserted into PostgreSQL.

The PostgreSQL Pod was deleted and recreated.

The same data was queried again successfully.

This demonstrated that the database data was stored on persistent storage instead of only inside the original Pod.

## 18. Service Connectivity Tests

### Nginx to Frontend

```bash
curl "$(minikube service nginx-service --url)/"
```

### Nginx to Backend

```bash
curl "$(minikube service nginx-service --url)/api/"
```

Expected:

```text
Flask App Running...
```

### Backend to PostgreSQL

Check:

```bash
kubectl logs deployment/backend-deployment
```

Expected:

```text
[DB STATUS] connected
```

## 19. Useful Troubleshooting Commands

### Check Pods

```bash
kubectl get pods -o wide
```

### Check Deployment

```bash
kubectl get deployments
```

### Check Services

```bash
kubectl get svc
```

### Check Service Endpoints

```bash
kubectl get endpoints backend-service
```

### Describe a Pod

```bash
kubectl describe pod <pod-name>
```

### Check Logs

```bash
kubectl logs <pod-name>
```

### Check PVC

```bash
kubectl get pvc
```

### Check PV

```bash
kubectl get pv
```

### Check Secret

```bash
kubectl get secret postgres-secret
```

### Check Rollout

```bash
kubectl rollout status deployment/backend-deployment
```

### Check Rollout History

```bash
kubectl rollout history deployment/backend-deployment
```

### Roll Back a Deployment

```bash
kubectl rollout undo deployment/backend-deployment
```

## 20. Common Problems Encountered

### Docker build context error

Running:

```bash
docker build ... backend/
```

from inside the `backend` directory caused a path error.

Correct:

```bash
docker build ... .
```

when already inside `backend/`.

### GitHub authentication error

GitHub HTTPS Git operations do not accept the normal account password. GitHub CLI authentication or a Personal Access Token can be used.

### Self-hosted runner not executing jobs

The runner must be running:

```bash
cd ~/project/kubernetes-3tier/actions-runner
./run.sh
```

The runner should show:

```text
Listening for Jobs
```

### Kubernetes Secret appearing as untracked

The real Secret file contains credentials and must be excluded:

```text
k8s/postgres-secret.yaml
```

Add it to `.gitignore`.

## 21. Final Architecture

```text
                         GitHub
                            |
                         git push
                            |
                     GitHub Actions
                            |
                   Self-hosted Runner
                            |
                    +-------+-------+
                    |               |
                  Docker         Minikube
                                    |
                             Nginx NodePort
                                    |
                       +------------+------------+
                       |                         |
                       v                         v
                Frontend Service         Backend Service
                       |                         |
                       v                         v
                  React Pod              Flask Pods (3)
                                                 |
                                                 v
                                         PostgreSQL Service
                                                 |
                                                 v
                                         PostgreSQL Pod
                                                 |
                                                 v
                                              PVC
                                                 |
                                                 v
                                              PV
```

## 22. Conclusion

This project demonstrates a complete local Kubernetes 3-tier deployment with:

* Containerized React frontend
* Containerized Flask backend
* PostgreSQL database
* Nginx entry point
* Kubernetes Deployments and Services
* Persistent database storage
* Kubernetes Secrets
* Service-based application communication
* GitHub source control
* GitHub Actions CI/CD
* Self-healing
* Application scaling
* Database persistence testing
* Service connectivity testing
* Deployment troubleshooting
