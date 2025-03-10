@echo off
docker exec -it mongo_db mongosh
pause

@REM show dbs - Xem database
@REM show collections - Xem cac collection
@REM use ... - Su dung collection nao
@REM db.<collection>.find().pretty() - Xem ban ghi
