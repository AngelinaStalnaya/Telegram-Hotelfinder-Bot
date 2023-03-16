#Python basic diploma

### <center>_Hotel finder telegram bot_

___
Hotel finder telegram bot is a bot written on Python using aiogram library for dealing with telegram API.

##Installation 
___
The minimum requirement for this bot is that your virtual machine supports Python 3.7 or above.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all the dependencies in your project.
 
1. _Before_ exploring the bot\`s features _create a new project_ in your interpreter and _add a virtual environment_  in it. F.e.: <br>
 ![](../../Ангелина/Desktop/photo for readme/1.png)
2. _Make a clone_ of the git repository with the Hotel finder telegram bot project  in your new project. <br>
![](../../Ангелина/Desktop/photo for readme/clone.png) <br>

Please make sure the release file is unpacked, so you shall see the following files and directories:

```
database/                work with database
site_api/                work with site API
tgbot_api/               work with telegram API
main.py                  start file
README.md                this file
requirements.txt         requirements checker     
settings.py              basic settings
```
3. For the proper work of the bot _install the requirements_ from requirements.txt in your virtual environment by: <br>
`pip install -r requirements.txt`
4. _Create_ a new file in a current directory named _'.env'_ and keep it open.
5. Open your telegram account, find the 'BotFather' bot in a search bar, start it. Follow the instructions of the BotFather to _create your new bot_.<br>
We recommend you to add a description, commands to the menu and other stuff to your bot after all other preparing.
6. After receiving a  _unique token, copy it_, then _move to the file '.env'_ in your project. <br>
![](../../Ангелина/Desktop/photo for readme/telega bot your token.png)<br>
Add the line in the file as follows: <br>
`BOT_TOKEN='<your token here>'` <br>
7. _Move to [rapidapi.com](https://rapidapi.com/)_ in a browser, create an account or sign in if you have one already. 
In category 'Travel' _choose 'Hotels' API_, select a suitable subscription in page 'Pricing'. <br>
![](../../Ангелина/Desktop/photo for readme/api sit e.png)
8. Move to page 'Endpoints', choose any endpoint to test. In section 'Code Snippets' _copy the value of 'X-RapidApi-Key'_. <br>
![](../../Ангелина/Desktop/photo for readme/apikey.png)

In file '.env' in your project _add a line_ as follows:

`SITE_API='<your X-RapidApi-Key here>'`
9. Move back to the section 'Code Snippets' and _copy the value of 'X-RapidAPI-Host'_. <br>
![](../../Ангелина/Desktop/photo for readme/apihost.png)

in file '.env' in your project _add the next line_:

`HOST_API='<your host here>'`

> Save the result and pay attention to the statistics on site API calls. Create a new account on [rapidapi.com](https://rapidapi.com/) if needed.


##Usage
___
> Activate your virtual environment if needed.

The Hotel finder telegram bot comes with the following command in  a command line: <br>
``` python
python main.py
```
Then move to your telegram bot to test bot\`s commands (/start, /history and else.) <br>
![](../../Ангелина/Desktop/photo for readme/telega bot your bot.png)

Currently, the Hotel finder telegram bot project supports execution of the next custom commands:
* history - for showing 10 last research request of the user;
* bestprice - for searching available hotels in location for current price and max-limit from the center of the location;
* lowprice - for searching  the cheapest available hotels in the location;
* highprice - for searching lux available hotels in the location

Three last commands support the option of sending photos of  each hotel.
>All the prices are presented for 1 room for 2 adults.
 

## License
___
The Hotel finder telegram bot is open-sourced code licensed under the [MIT](https://choosealicense.com/licenses/mit/) 
2023 Angelina Stalnaya

## Maintainers
___
> @AngeliaStalnaya