#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "Erro: arquivo .env não encontrado. Copie .env.example para .env e preencha os valores."
  exit 1
fi

echo "Pré-requisito: a infraestrutura compartilhada (RabbitMQ, LocalStack) e o"
echo "banco de dados desta API precisam já estar de pé no namespace 'video-infra'"
echo "(repositório video-infra-k8s)."
echo ""

echo "Criando/atualizando Secret da API a partir do .env..."
kubectl delete secret video-management-api-secrets --ignore-not-found
kubectl create secret generic video-management-api-secrets --from-env-file=.env

echo "Aplicando ConfigMap..."
kubectl apply -f k8s/configmap.yaml

echo "Rodando migrations..."
kubectl delete job video-management-api-migrate --ignore-not-found
kubectl apply -f k8s/migration-job.yaml
kubectl wait --for=condition=complete job/video-management-api-migrate --timeout=90s

echo "Aplicando metrics..."
kubectl apply -f k8s/metrics.yaml

echo "Aplicando Deployment da API..."
kubectl apply -f k8s/deployment.yaml

echo "Aplicando Service..."
kubectl apply -f k8s/service.yaml

echo "Aplicando HPA..."
kubectl apply -f k8s/hpa.yaml

echo "Reiniciando pods da API para garantir que pegam config/secret atualizados..."
kubectl rollout restart deployment video-management-api

echo "Deploy da API concluído!"
echo ""
echo "Para acessar localmente: kubectl port-forward svc/video-management-api 8000:80"
