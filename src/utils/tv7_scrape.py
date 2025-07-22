import requests




def get_active_7tv_emote_urls(emoteset_id):

    SET_ID = "01JWETP6HTP150CZ3NF6R22W1N"
    url = "https://7tv.io/v3/gql"

    payload = {
        "operationName": "GetEmoteSet",
        "variables": {"id": SET_ID},
        "query": """
        query GetEmoteSet($id: ObjectID!) {
          emoteSet(id: $id) {
            emotes {
              name
              data {
                host {
               url
              files {
                name
                format
              }
            }
          }
        }
        }
        }
        """
    }

    headers = {"Content-Type": "application/json"}

    res = requests.post(url, json=payload, headers=headers)
    data = res.json()

    emotes = []
    for emote in data["data"]["emoteSet"]["emotes"]:
        name = emote["name"]
        base_url = emote["data"]["host"]["url"]
        largest_file = emote["data"]["host"]["files"][-1]["name"]
        full_url = f"{base_url}/{largest_file}"
        full_url = full_url.replace("4x", "2x")
        emotes.append({"name": name, "url": full_url})
#    return emotes
   
    return emotes
