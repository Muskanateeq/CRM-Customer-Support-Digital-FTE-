#!/bin/bash

# TaskNest Kubernetes Deployment Script
# This script deploys the entire TaskNest application to Kubernetes

set -e

echo "=========================================="
echo "TaskNest Kubernetes Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi

echo -e "${GREEN}✓ kubectl is installed and cluster is accessible${NC}"

# Function to wait for deployment
wait_for_deployment() {
    local namespace=$1
    local deployment=$2
    local timeout=${3:-300}

    echo "Waiting for deployment $deployment in namespace $namespace..."
    kubectl wait --for=condition=available --timeout=${timeout}s \
        deployment/$deployment -n $namespace
}

# Function to wait for statefulset
wait_for_statefulset() {
    local namespace=$1
    local statefulset=$2
    local replicas=$3
    local timeout=${4:-300}

    echo "Waiting for statefulset $statefulset in namespace $namespace..."
    kubectl wait --for=jsonpath='{.status.readyReplicas}'=$replicas \
        --timeout=${timeout}s statefulset/$statefulset -n $namespace
}

# Step 1: Create namespace
echo ""
echo "Step 1: Creating namespace..."
kubectl apply -f k8s/namespace.yaml
echo -e "${GREEN}✓ Namespace created${NC}"

# Step 2: Create ConfigMap and Secrets
echo ""
echo "Step 2: Creating ConfigMap and Secrets..."
echo -e "${YELLOW}⚠ Make sure you've updated k8s/secret.yaml with real values!${NC}"
read -p "Have you updated the secrets? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo -e "${RED}Please update k8s/secret.yaml with real values first${NC}"
    exit 1
fi

kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
echo -e "${GREEN}✓ ConfigMap and Secrets created${NC}"

# Step 3: Deploy PostgreSQL (optional - for dev/test only)
echo ""
read -p "Deploy PostgreSQL in cluster? (yes/no - use 'no' if using external DB like Neon): " deploy_postgres
if [ "$deploy_postgres" = "yes" ]; then
    echo "Deploying PostgreSQL..."
    kubectl apply -f k8s/postgres-deployment.yaml
    wait_for_deployment tasknest postgres 300
    echo -e "${GREEN}✓ PostgreSQL deployed${NC}"
else
    echo -e "${YELLOW}⚠ Skipping PostgreSQL deployment - using external database${NC}"
fi

# Step 4: Deploy ZooKeeper
echo ""
echo "Step 3: Deploying ZooKeeper..."
kubectl apply -f k8s/zookeeper-service.yaml
kubectl apply -f k8s/zookeeper-statefulset.yaml
wait_for_statefulset tasknest zookeeper 3 300
echo -e "${GREEN}✓ ZooKeeper deployed${NC}"

# Step 5: Deploy Kafka
echo ""
echo "Step 4: Deploying Kafka..."
kubectl apply -f k8s/kafka-service.yaml
kubectl apply -f k8s/kafka-statefulset.yaml
wait_for_statefulset tasknest kafka 3 300
echo -e "${GREEN}✓ Kafka deployed${NC}"

# Step 6: Run database migrations
echo ""
echo "Step 5: Running database migrations..."
echo -e "${YELLOW}⚠ Make sure your database is accessible and migrations are ready${NC}"
read -p "Run migrations now? (yes/no): " run_migrations
if [ "$run_migrations" = "yes" ]; then
    # Create a temporary pod to run migrations
    kubectl run migration-job --rm -i --restart=Never \
        --image=your-registry/tasknest-api:latest \
        --env="DATABASE_URL=$(kubectl get secret tasknest-secrets -n tasknest -o jsonpath='{.data.DATABASE_URL}' | base64 -d)" \
        -n tasknest \
        -- python scripts/setup_pgvector.py
    echo -e "${GREEN}✓ Migrations completed${NC}"
else
    echo -e "${YELLOW}⚠ Skipping migrations - run manually later${NC}"
fi

# Step 7: Deploy API
echo ""
echo "Step 6: Deploying API..."
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
wait_for_deployment tasknest tasknest-api 300
echo -e "${GREEN}✓ API deployed${NC}"

# Step 8: Deploy Workers
echo ""
echo "Step 7: Deploying Workers..."
kubectl apply -f k8s/worker-deployment.yaml
wait_for_deployment tasknest tasknest-worker 300
echo -e "${GREEN}✓ Workers deployed${NC}"

# Step 9: Deploy Ingress (optional)
echo ""
read -p "Deploy Ingress? (yes/no): " deploy_ingress
if [ "$deploy_ingress" = "yes" ]; then
    echo "Deploying Ingress..."
    kubectl apply -f k8s/ingress.yaml
    echo -e "${GREEN}✓ Ingress deployed${NC}"
    echo -e "${YELLOW}⚠ Make sure cert-manager and nginx-ingress-controller are installed${NC}"
else
    echo -e "${YELLOW}⚠ Skipping Ingress deployment${NC}"
fi

# Step 10: Verify deployment
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""
echo "Pods:"
kubectl get pods -n tasknest
echo ""
echo "Services:"
kubectl get services -n tasknest
echo ""
echo "Deployments:"
kubectl get deployments -n tasknest
echo ""
echo "StatefulSets:"
kubectl get statefulsets -n tasknest
echo ""

# Get API endpoint
echo "=========================================="
echo "Access Information"
echo "=========================================="
if [ "$deploy_ingress" = "yes" ]; then
    echo "API URL: https://api.tasknest.com"
else
    echo "To access the API, use port-forward:"
    echo "  kubectl port-forward -n tasknest svc/tasknest-api 8000:80"
    echo "  Then access: http://localhost:8000"
fi

echo ""
echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
echo ""
echo "Useful commands:"
echo "  kubectl logs -f -n tasknest deployment/tasknest-api"
echo "  kubectl logs -f -n tasknest deployment/tasknest-worker"
echo "  kubectl get pods -n tasknest -w"
echo "  kubectl describe pod <pod-name> -n tasknest"
