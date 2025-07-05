
-- working

docker compose up
docker compose logs
docker compose restart glance
--
docker run -it --rm -v "$PWD/config":/app/config alpine sh
docker compose up -d

/etc/timezone:/etc/timezone:ro            # Ensures container timezone sync.
/etc/localtime:/etc/localtime:ro          # Ensures container localtime sync.
    
docker run -it -v ./config:/app/config --rm glanceapp/glance  /bin/sh
