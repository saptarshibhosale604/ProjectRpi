# todo
## main02.py
- rendere not comfy with 
    - list type renderer
    - table

# Temp
Here are 10 queries to try:

Show a dashboard with 10 raspberry pi parameters
Show a dashboard with CPU, RAM, Disk, and Network usage
Create a table of 5 development tasks with their status and priority
Show server health gauges for CPU, memory, temperature, and disk I/O
Display progress bars for frontend, backend, testing, and deployment completion
Show a set of system alerts: one info, one warning, one error, one success
Create a dashboard showing team members and their current task status
Show cards for daily active users, uptime percentage, error rate, and response time
Create a list of 7 things to do for launching a mobile app
Display a user registration form with name, email, password, and role fields
Show a Raspberry Pi sensor dashboard with temperature, humidity, light level, and battery gauges

# run ollama as docker image
docker rm -f ollama

docker run -d \
  --name ollama \
  -p 11434:11434 \
  -e OLLAMA_MAX_LOADED_MODELS=1 \
  -v ollama:/root/.ollama \
  alpine/ollama

docker ps

curl http://localhost:11434

docker logs -f ollama

tail -f log-.log
tail -f 

docker exec -it ollama sh


curl http://localhost:11434/api/chat  \
-d '{ \
"model":"llama3.2", \
"messages":[ \
{ \
"role":"user", \
"content":"Hello" \
} \
], \
"stream":false \
}'

