https://openclaw.ai/

- with setup
curl -fsSL https://openclaw.ai/install.sh | bash

- without setup
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

https://kiankyars.github.io/openclawcourse/

- from arch linux enable tunneling
➤ ssh -L 18789:localhost:18789 ssbrpi@172.26.36.108 
- on browser
http://localhost:18789/
- Overview => Gateway access => password => admin => connect

- file
/home/ssbrpi/.openclaw

- openclaw queries
openclaw message send --target +917058033447 --message "Hello from OpenClaw"

.openclaw ➤ openclaw models auth login --provider qwen-portal

 openclaw channels login --channel whatsapp --account default
