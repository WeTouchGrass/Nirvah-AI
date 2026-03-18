
kill old processes

if the server wont start because "address already in use", run this:

```
powershell -Command "Get-NetTCPConnection -LocalPort 10000 -EA 0 | % { Stop-Process -Id $_.OwningProcess -Force }"
```



terminal 1 

cd C:\Users\dthun\Nirvah-AI

venv\Scripts\activate

python demo_server.py


terminal 2 

cd C:\Users\dthun\Nirvah-AI\dashboard

npm run dev

"Local: http://localhost:5173/"
"Local: https://localhost:5173/"


terminal 3 — ngrok tunnel

ngrok http 10000

this gives me a public url like `https://xxxx.ngrok-free.app`
url for twilio


 twilio webhook 

 dashboard login

open browser, go to `http://localhost:5173/`
- user: **admin**
- pass: **nirvaah2025**


 messages template

Sunitha Thomas ANC visit 3 BP 138/92 hemoglobin 9.5 weight 58kg IFA 30 tablets next visit PHC Thrissur

 2. bad data pushback

Meera Devi first ANC visit BP 300/120

 3. sos emergency

jalebi


 4. survey mode

SURVEY


