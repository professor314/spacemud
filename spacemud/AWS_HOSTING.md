# Hosting Space MUD on AWS — Complete Guide

This guide walks you through hosting the game on AWS from scratch. No prior AWS experience needed.

---

## What You'll Set Up

- An **EC2 instance** (a virtual server in the cloud) running Ubuntu Linux
- The game server accessible to anyone on the internet
- The web client on port 4001 and telnet on port 4000

**Estimated cost:** ~$5–10/month for a `t3.micro` instance (free tier eligible for the first 12 months of a new AWS account).

---

## Step 1: Create an AWS Account

1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click **Create an AWS Account**
3. Enter your email, choose a password, and pick an account name
4. Enter payment info (you won't be charged if you stay in the free tier)
5. Choose the **Basic (Free)** support plan
6. Wait for account activation (can take a few minutes)

---

## Step 2: Launch an EC2 Instance

1. Sign in to the [AWS Console](https://console.aws.amazon.com)
2. In the search bar at the top, type **EC2** and click it
3. Click **Launch Instance**

### Configure the instance:

**Name:** `space-mud-server`

**Application and OS Images (AMI):** Select **Ubuntu** → **Ubuntu Server 24.04 LTS** (free tier eligible)

**Instance type:** `t3.micro` (free tier eligible, 1 vCPU, 1 GB RAM — enough for a MUD)

**Key pair:** Click **Create new key pair**
- Name: `space-mud-key`
- Type: RSA
- Format: `.pem`
- Click **Create key pair** — it downloads a `.pem` file. **Save this file somewhere safe.** You need it to connect.

**Network settings:** Click **Edit**, then:
- Check **Allow SSH traffic from** → **My IP** (so only you can SSH in)
- Check **Allow HTTP traffic from the internet**
- Check **Allow HTTPS traffic from the internet**

**Storage:** 20 GB gp3 (default is fine)

Click **Launch Instance**.

---

## Step 3: Open Game Ports

The game needs ports 4000 (telnet) and 4001 (web client) open.

1. Go to **EC2 → Instances** and click your instance
2. Click the **Security** tab
3. Click the **Security group** link (something like `sg-xxxxx`)
4. Click **Edit inbound rules**
5. Add two rules:

| Type | Port Range | Source | Description |
|---|---|---|---|
| Custom TCP | 4000 | 0.0.0.0/0 | Telnet game port |
| Custom TCP | 4001 | 0.0.0.0/0 | Web client port |

6. Click **Save rules**

---

## Step 4: Connect to Your Instance

### On Windows (PowerShell):

1. Find your instance's **Public IPv4 address** in the EC2 console (something like `54.123.45.67`)
2. Open PowerShell and navigate to where you saved the `.pem` file
3. Connect:

```powershell
ssh -i space-mud-key.pem ubuntu@YOUR_PUBLIC_IP
```

If you get a permissions error on the key file:

```powershell
icacls space-mud-key.pem /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

Then try the SSH command again.

### On Mac/Linux:

```bash
chmod 400 space-mud-key.pem
ssh -i space-mud-key.pem ubuntu@YOUR_PUBLIC_IP
```

---

## Step 5: Install Dependencies

Once connected to the server via SSH, run these commands:

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install -y python3 python3-pip python3-venv git

# Create a virtual environment
python3 -m venv ~/mudenv
source ~/mudenv/bin/activate

# Install Evennia
pip install evennia
```

---

## Step 6: Upload the Game Files

### Option A: Upload from your local machine using SCP

From your **local** PowerShell (not the SSH session):

```powershell
scp -i space-mud-key.pem -r spacemud ubuntu@YOUR_PUBLIC_IP:~/spacemud
```

### Option B: Use Git

If your code is in a Git repository:

```bash
# On the server
cd ~
git clone YOUR_REPO_URL
cd spacemud
```

---

## Step 7: Set Up the Game on the Server

Back in the SSH session:

```bash
source ~/mudenv/bin/activate
cd ~/spacemud

# Run database migrations
evennia migrate

# Start the server (it will ask you to create a superuser)
evennia start
```

Create the superuser when prompted (name + password, at least 8 characters).

### Load the world content:

```bash
python manage.py shell
```

Then in the Python shell:

```python
import evennia
evennia._init()
from world.batch_code import main
main(type('C', (), {'msg': staticmethod(print)})())
exit()
```

---

## Step 8: Configure Evennia to Accept External Connections

By default, Evennia only listens on localhost. You need to tell it to listen on all interfaces.

Edit the settings file:

```bash
nano ~/spacemud/server/conf/settings.py
```

Add these lines at the bottom:

```python
# Allow external connections
TELNET_INTERFACES = ["0.0.0.0"]
WEBSERVER_INTERFACES = ["0.0.0.0"]
WEBSOCKET_CLIENT_INTERFACE = "0.0.0.0"
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

Restart the server:

```bash
cd ~/spacemud
evennia stop
evennia start
```

---

## Step 9: Connect from Anywhere

### Web client:
Open a browser and go to:
```
http://YOUR_PUBLIC_IP:4001
```

### Telnet:
```
telnet YOUR_PUBLIC_IP 4000
```

Replace `YOUR_PUBLIC_IP` with the public IP from the EC2 console.

---

## Step 10: Keep the Server Running

By default, if you close your SSH session, the server keeps running (Evennia daemonizes). But if the EC2 instance reboots, you need to restart manually.

### Auto-start on boot (optional):

Create a systemd service:

```bash
sudo nano /etc/systemd/system/spacemud.service
```

Paste this:

```ini
[Unit]
Description=Space MUD Evennia Server
After=network.target

[Service]
Type=forking
User=ubuntu
WorkingDirectory=/home/ubuntu/spacemud
Environment="PATH=/home/ubuntu/mudenv/bin:/usr/bin"
ExecStart=/home/ubuntu/mudenv/bin/evennia start
ExecStop=/home/ubuntu/mudenv/bin/evennia stop
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit, then enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable spacemud
sudo systemctl start spacemud
```

Now the game starts automatically when the server boots.

Check status:

```bash
sudo systemctl status spacemud
```

---

## Step 11: Set Up a Domain Name (Optional)

If you want `play.yourgame.com` instead of an IP address:

1. Buy a domain from a registrar (Namecheap, Route 53, Google Domains, etc.)
2. In your DNS settings, create an **A record** pointing to your EC2 public IP:
   - Name: `play` (or `@` for the root domain)
   - Type: A
   - Value: `YOUR_PUBLIC_IP`
   - TTL: 300
3. Wait 5–30 minutes for DNS propagation
4. Connect via `http://play.yourgame.com:4001`

**Note:** If your EC2 instance restarts, the public IP may change. To prevent this, allocate an **Elastic IP** in the EC2 console and associate it with your instance (free while the instance is running).

---

## Troubleshooting

### Can't connect from browser
- Check that ports 4000 and 4001 are open in the Security Group (Step 3)
- Check that `WEBSERVER_INTERFACES` is set to `["0.0.0.0"]` in settings.py (Step 8)
- Check the server is running: `cd ~/spacemud && evennia status`

### Server won't start
- Make sure you're in the virtual environment: `source ~/mudenv/bin/activate`
- Make sure you're in the game directory: `cd ~/spacemud`
- Check logs: `cat ~/spacemud/server/logs/server.log`

### SSH connection refused
- Check that your IP hasn't changed (home IPs rotate). Update the Security Group SSH rule with your current IP.
- Or change the SSH rule source to `0.0.0.0/0` (less secure but always works)

### Instance runs out of memory
- `t3.micro` has 1 GB RAM. If you see out-of-memory errors, upgrade to `t3.small` (2 GB, ~$15/month)
- Or add swap space:
  ```bash
  sudo fallocate -l 1G /swapfile
  sudo chmod 600 /swapfile
  sudo mkswap /swapfile
  sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  ```

---

## Monthly Cost Estimate

| Resource | Cost |
|---|---|
| t3.micro EC2 (free tier first year) | $0 – $8.50/month |
| 20 GB EBS storage | ~$1.60/month |
| Elastic IP (while instance running) | Free |
| Data transfer (first 100 GB/month) | Free |
| **Total** | **$0 – $10/month** |

After the free tier expires, expect ~$10/month for a `t3.micro`.
