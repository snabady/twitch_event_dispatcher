# twitch_event_dispatcher
to install twitch-cli:
```sh
#!/bin/bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo >> /home/sna/.bashrc
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> /home/sna/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
sudo pacman -S base-devel
brew install twitchdev/twitch/twitch-cli 
twitch configure
twitch token
twitch mock-api generate
```
copy your generated credentials and userID into .env_twitch_cli
