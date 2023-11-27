# Containers

## Dockerize
  Step 1: Run
  `docker compose up -d`
  (with and optional --build option at the end if you have already done the build and to build again)

  No need to manually populate the data as in the steps above. The docker config takes care of that :)

  Step 2: Open the URL in your browser:  
      http://127.0.0.1:5000/ or http://localhost:5000/

## Kubernetes

  - Navigate to the project directory.
  - Apply Kubernetes deployment and service YAML files:
    ```bash
    kubectl apply -f app-deployment.yaml
    kubectl apply -f app-service.yaml
    ```

    - Access Your Application

    Retrieve the external IP (LoadBalancer) or Cluster IP of the service:

    ```bash
    kubectl get service flask-mongo-service
    ```