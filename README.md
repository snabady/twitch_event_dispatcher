# twitch_event_dispatcher
first install twitch-cli for detailed information check  [Twitch Docs](https://dev.twitch.tv/docs/cli/)
```sh
#!/bin/bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo >> /home/$foo/.bashrc
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/$foo/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
sudo pacman -S base-devel
brew install twitchdev/twitch/twitch-cli 
twitch configure
twitch token
twitch mock-api generate
```
copy your generated credentials and userID into .env_twitch_cli
$HOME/.config/twitch-cli/.twitch-cli.env
then start the twitch-mocking-service and the websocket to listen for the events.
```sh
twitch mock-api start -p 5555 &
twitch event websocket start -p 5556 &
```
check .env file u should be ready to run
main.py
