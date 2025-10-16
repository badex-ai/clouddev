#!/bin/bash

set -e  # Exit immediately if any command exits with a non-zero status
set -o pipefail  # Catch errors in pipelines

# ================== COLORS ==================
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
# ============================================

echo -e "${BLUE}=== Starting Local K8s Setup ===${NC}\n"

# ========== CLEANUP FUNCTION ==========
cleanup() {
  echo -e "${YELLOW}Rolling back: Uninstalling Helm release 'kaban'...${NC}"
  helm uninstall kaban || true
  echo -e "${RED}Rollback complete. Exiting setup.${NC}"
}
trap 'cleanup' ERR  # Trigger rollback if any command fails
# ======================================

# STEP 1: Install Helm Chart
echo -e "${GREEN}Step 1: Installing Helm chart...${NC}"
cd ./infrastructure/k8s

helm install kaban . \
  -f values.yaml \
  -f values-local.yaml \
  -f values-secrets.yaml

echo -e "${GREEN}✓ Helm chart installed successfully${NC}\n"

# Wait for Kubernetes services to come up
echo -e "${YELLOW}Waiting for services to be ready (10s)...${NC}"
sleep 10

# STEP 2: Retrieve Service Cluster IPs
echo -e "${GREEN}Step 2: Getting service IPs...${NC}"
cd ../..  # Return to root

kubectl get service -n local-dev

FRONTEND_IP=$(kubectl get service -n local-dev -o jsonpath='{.items[?(@.metadata.name=="kaban-frontend-service")].spec.clusterIP}')
BACKEND_IP=$(kubectl get service -n local-dev -o jsonpath='{.items[?(@.metadata.name=="kaban-backend-service")].spec.clusterIP}')

if [ -z "$FRONTEND_IP" ] || [ -z "$BACKEND_IP" ]; then
  echo -e "${RED}Error: Could not retrieve service ClusterIPs${NC}"
  echo -e "${YELLOW}Available services:${NC}"
  kubectl get service -n local-dev -o custom-columns=NAME:.metadata.name,CLUSTER-IP:.spec.clusterIP
  exit 1
fi

echo -e "${BLUE}Frontend IP:${NC} $FRONTEND_IP"
echo -e "${BLUE}Backend IP:${NC} $BACKEND_IP\n"

# STEP 3: Safely update /etc/hosts atomically
echo -e "${GREEN}Step 3: Updating /etc/hosts...${NC}"

HOSTS_ENTRY_FRONTEND="$FRONTEND_IP frontend.local"
HOSTS_ENTRY_BACKEND="$BACKEND_IP backend.local"

echo -e "${YELLOW}Preparing atomic /etc/hosts update...${NC}"

# Create temporary file for atomic update (same directory for atomic mv)
TEMP_HOSTS=$(mktemp)

# Copy current hosts file to temp (needs sudo to read /etc/hosts)
sudo cp /etc/hosts "$TEMP_HOSTS"

# Now change ownership to current user so we can work with it
sudo chown $USER:$USER "$TEMP_HOSTS"

# Remove any previous frontend.local or backend.local entries
# Now we can use sed WITHOUT sudo since we own the file
sed -i '/frontend\.local\|backend\.local/d' "$TEMP_HOSTS"

# Add updated entries (no sudo needed)
echo "$HOSTS_ENTRY_FRONTEND" >> "$TEMP_HOSTS"
echo "$HOSTS_ENTRY_BACKEND" >> "$TEMP_HOSTS"

# Verify temp file contains both new entries (no sudo needed)
if ! grep -q "frontend.local" "$TEMP_HOSTS" || ! grep -q "backend.local" "$TEMP_HOSTS"; then
  echo -e "${RED}Error: Verification failed — entries missing from temp hosts file${NC}"
  rm -f "$TEMP_HOSTS"  # Clean up temp file
  exit 1
fi


# Atomically replace /etc/hosts with the verified temp file
echo -e "${YELLOW}Performing atomic replace...${NC}"
sudo mv "$TEMP_HOSTS" /etc/hosts

# Verify changes took effect
echo -e "${GREEN}✓ /etc/hosts updated successfully${NC}\n"
echo -e "${BLUE}Current /etc/hosts entries:${NC}"
grep -E "frontend.local|backend.local" /etc/hosts || {
  echo -e "${RED}Error: Entries not found after replacement${NC}"
  exit 1
}

# =================== SUCCESS ===================
trap - ERR  # Disable rollback trap since everything succeeded
echo -e "\n${GREEN}=== Setup Complete! ===${NC}"
echo -e "${BLUE}Frontend:${NC} http://frontend.local"
echo -e "${BLUE}Backend:${NC} http://backend.local\n"
echo -e "${YELLOW}Check pods with: kubectl get pods -n local-dev${NC}"
# =================================================
