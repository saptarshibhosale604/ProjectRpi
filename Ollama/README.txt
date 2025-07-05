// // only docker way
// working
docker run -d --rm -v ollama:/root/.ollama -p 11434:11434 --name ollama02 ollama/ollama
docker run -d --rm -v ollama:/root/.ollama -v /home/rpissb/Project/Ollama:/App \
 -p 11434:11434 --name ollama02 ollama/ollama

docker exec -it ollama02 ollama run llama3.2:1b // 1.3 GB, text
TEXT >>> generate 1 stanza poem on music

total duration:       8.049647744s
load duration:        40.62672ms
prompt eval count:    32 token(s)
prompt eval duration: 1.598880679s
prompt eval rate:     20.01 tokens/s
eval count:           44 token(s)
eval duration:        6.40918491s
eval rate:            6.87 tokens/s

docker exec -it ollama02 ollama run --verbose llama3.2:1b // for seeing tokens per minute
docker exec -it ollama02 ollama run --verbose gemma3:4b  // for seeing tokens per minute

docker exec -it ollama02 ollama run gemma3:4b // 3.3gb, text, vision
TEXT >>> generate 1 stanza poem on music

total duration:       15.996778309s
load duration:        103.045508ms
prompt eval count:    16 token(s)
prompt eval duration: 3.669236307s
prompt eval rate:     4.36 tokens/s
eval count:           42 token(s)
eval duration:        12.223595634s
eval rate:            3.44 tokens/s

VISION >>> Describe this image, /App/batman.jpg
Added image '/App/batman.jpg'

total duration:       5m26.171759489s
load duration:        99.104278ms
prompt eval count:    343 token(s)
prompt eval duration: 4m32.679647587s
prompt eval rate:     1.26 tokens/s
eval count:           174 token(s)
eval duration:        53.317782576s
eval rate:            3.26 tokens/s

02 >>> which animal is this? and what is it doing
... ? , /App/cat.jpeg

total duration:       11m3.102336098s
load duration:        19.620606635s
prompt eval count:    798 token(s)
prompt eval duration: 10m15.3177074s
prompt eval rate:     1.30 tokens/s
eval count:           88 token(s)
eval duration:        28.085531532s
eval rate:            3.13 tokens/s

03 >>> how many dices are there?, /App/dice.jpeg
total duration:       4m42.329076461s
load duration:        102.402619ms
prompt eval count:    275 token(s)
prompt eval duration: 4m38.474871916s
prompt eval rate:     0.99 tokens/s
eval count:           13 token(s)
eval duration:        3.750953354s
eval rate:            3.47 tokens/s

>>> explain the image in a paragraph
total duration:       36.606465641s
load duration:        101.422974ms
prompt eval count:    303 token(s)
prompt eval duration: 3.440900157s
prompt eval rate:     88.06 tokens/s
eval count:           109 token(s)
eval duration:        33.062665634s
eval rate:            3.30 tokens/s

>>> what's the color of the dice
total duration:       12.697376753s
load duration:        102.844595ms
prompt eval count:    429 token(s)
prompt eval duration: 3.888829822s
prompt eval rate:     110.32 tokens/s
eval count:           29 token(s)
eval duration:        8.699729939s
eval rate:            3.33 tokens/s

// summary it's taking time to load the image.
But once the image is loaded, it's taking less time to give followup answer



//
docker exec -it ollama ollama run llama3
llama3.2:1b

docker exec -it ollama02 /bin/sh

// // python way
docker build -t ollama-docker-project .
docker run --rm ollama-docker-project
docker run -it --rm ollama-docker-project /bin/sh

docker compose up
docker compose up --build
docker compose run --rm app /bin/sh

curl http://localhost:11435

docker exec -it python_app /bin/sh

docker build -t ollama-docker-project .
docker run -it --rm ollama-docker-project serve -v ollama:/root/.ollama -p 11434:11435 --name ollama03 
docker run -it --rm ollama-docker-project serve -v ollama:/root/.ollama -p 11434:11435 --name ollama03 

ollama-docker-project ollama run llama3.2:1b
docker run -d --rm -v ollama:/root/.ollama -p 11434:11434 --name ollama03 
docker exec -it ollama03 ollama run llama3.2:1b

/
docker exec -it ollama07 /bin/sh
docker exec -it ollama06 ollama run llama3.2:1b

docker run -it --rm   -v ollama:/root/.ollama   -p 11434:11434   --name ollama07   --entrypoint /bin/sh   ollama-docker-project
docker run -it --rm   -v ollama:/root/.ollama   -p 11434:11434   --name ollama07   --entrypoint python app.py   ollama-docker-project

docker run -it --rm \
  -v ollama:/root/.ollama \
  -p 11434:11434 \
  --name ollama07 \
  --entrypoint python \
  ollama-docker-project \
  /App/app.py

//


python app.py

/ WORKING
docker build -t ollama-docker-project .
docker run -d --rm -v ollama:/root/.ollama -p 11434:11434 --name ollama07 ollama-docker-project
docker exec -it ollama07 python /App/app.py
// 
