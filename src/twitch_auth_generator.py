# get auth-token for xy
#self.

from twitchAPI import Twitch
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.types import AuthScope

APP_ID =""
APP_SECRET = ""
USER_SCOPE = [AuthScope.CHAT_READ, AuthScope.CHAT_EDIT]



async def auth_token_generator(self, twitch: Twitch, USER_SCOPE) -> (str, str):
    redirection_url ="http://localhost:17561"
    auth = UserAuthenticator(twitch, self.scopes,url=redirection_url,  host='0.0.0.0', port=17561)
    token, refresh_token = await auth.authenticate()

    return token, refresh_token



async def run():
    twitch = await Twitch(APP_ID, APP_SECRET)
    helper = UserAuthenticationStorageHelper(twitch, 
                                             USER_SCOPE, 
                                             storage_path=PurePath('/my/new/path/file.json'),
                                             auth_generator_func=auth_token_generator)
    await helper.bind()
# TODO work in progress... finish this for your nerves!
    await twitch.close()

asyncio.run(run())
