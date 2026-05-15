#!/bin/bash

# Configurações
URL=<URL>
TOKEN=<TOKEN>

# Quantidade de "ondas" de ataque
ONDAS=50
REQS_POR_ONDA=20

echo "🚀 Iniciando teste de carga agressivo no EKS..."
echo "Monitorando HPA em tempo real..."

for i in $(seq 1 $ONDAS)
do
   echo "🌊 Onda $i de $ONDAS: disparando $REQS_POR_ONDA requisições simultâneas..."
   
   for j in $(seq 1 $REQS_POR_ONDA)
   do
      # O '&' ao final envia a requisição para o background
      curl -s -o /dev/null -w "%{http_code} " \
           -X GET "$URL" \
           -H "accept: application/json" \
           -H "Authorization: Bearer $TOKEN" &
   done
   
   # Pequena pausa para não travar o seu MacBook, mas manter a pressão no EKS
   sleep 0.5
done

wait
echo -e "\n\n✅ Teste finalizado. Verifique o HPA no terminal ao lado!"