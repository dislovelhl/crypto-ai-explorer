#!/bin/bash
# VPS Deploy Script for CryptoAI Copilot (x402 API)

set -e

echo "🚀 Deploying CryptoAI Copilot x402 API to VPS..."

# Ensure we're root or running with sudo
if [ "$EUID" -ne 0 ]; then
  echo "Please run with sudo"
  exit
fi

# 1. Install prerequisites
apt-get update
apt-get install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx

# 2. Setup user and directory
useradd -m -s /bin/bash cryptoai || true
INSTALL_DIR="/opt/cryptoai"
mkdir -p "$INSTALL_DIR"

# Copy code
cp -r . "$INSTALL_DIR"
chown -R cryptoai:cryptoai "$INSTALL_DIR"

# 3. Setup Virtual Environment
su - cryptoai -c "
cd $INSTALL_DIR
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
"

# 4. Create Systemd Service
cat > /etc/systemd/system/cryptoai.service << EOF
[Unit]
Description=CryptoAI x402 API Server
After=network.target

[Service]
User=cryptoai
Group=cryptoai
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/venv/bin"
ExecStart=$INSTALL_DIR/venv/bin/uvicorn services.x402-api.server:app --host 127.0.0.1 --port 8402
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable cryptoai
systemctl restart cryptoai

# 5. Nginx Proxy Setup (Requires manual certbot run for SSL)
cat > /etc/nginx/sites-available/cryptoai << 'EOF'
server {
    listen 80;
    server_name api.cryptoai-copilot.com;

    location / {
        proxy_pass http://127.0.0.1:8402;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cryptoai /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl restart nginx

echo "✅ Deployment complete!"
echo "API running internally on port 8402."
echo "Nginx proxy configured for api.cryptoai-copilot.com (Port 80)."
echo ""
echo "Next step: Run 'certbot --nginx -d api.cryptoai-copilot.com' to enable HTTPS."
