@echo off
docker exec -it postgres_db psql -U namdt25  -d orders_db
pause