# jom-kerja
Run process.py as background process on Ubuntu server, it'll send weather and rapidKL service status according to configured time and frequency, as phone notifications through ntfy app. 
Configurable by modifying src/tool.json

Weather API: https://developer.data.gov.my/realtime-api/weather
MTREC rapidKL train status: https://documenter.getpostman.com/view/40279048/2sAYBd67bZ#e012e1dc-fe55-4451-9f98-54a34ab7d8a8
Bus route service status: https://developer.data.gov.my/realtime-api/gtfs-static
