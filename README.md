


## Problems and solutions

If having trouble connecting to MSSQL on mac, 

```
rm -rf $(brew --prefix)/opt/openssl
version=$(ls $(brew --prefix)/Cellar/openssl@1.1 | grep "1.1")
ln -s $(brew --prefix)/Cellar/openssl@1.1/$version $(brew --prefix)/opt/openssl
```

Install on MacOS:

```
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release   
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools
```