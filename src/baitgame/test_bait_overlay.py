import requests, time

for i in range(5):
    requests.post("http://localhost:8787/fishing", json={
        "name": f"Player{i}",
        "result": i * 2,
        "fishingTime": 2000 + i * 500
    })
    time.sleep(1)
