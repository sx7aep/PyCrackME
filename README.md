# Feel Free To Use

You can modify these source code and build your own Crackme!

## About

A Python CrackMe with a modern UI and anti-debugging features.

## Features

- Modern UI built with PyQt5
- Animated interface with loading indicators
- Anti-debugging protection
- Encrypted password verification
- Protection against timing attacks

## Setup & Build

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Build the executable:
   
   For PowerShell:
   ```
   pyinstaller CrackMeChallenge.spec
   ```

3. Run the executable from the `dist` folder

## Challenge

Try to figure out the correct password to unlock the application or CRACK IT!. Any username will work, but the password is the secret you need to crack!

## Hints

1. The password is hardcoded in the application's code
2. Various obfuscation techniques are used to hide the password
3. The application includes anti-debugging