# EEHPH Photo Viewer v2

A simple windows image viewer I wrote when I was 15. Despite my programming knowledge not being as good back then, it's still much better than the default windows image viewer and has a lot of nice features I like. The file date metadata is incorrect since it was reset by the file system at some point, it was written in 2016 ish.

![Demo image](/Assets/demoimage2.png)

## Features

- ~44Mb install size, pretty good for a non-native app, much smaller than whatever electron shit kids are making these days
- Basic image editing (resizing/rotating) built in
- Nice file tree browser, that eventually turned into [tkFileBrowser](https://github.com/jwansek/tkFileBrowser/)
- Nice installer, that actually cleans up itself properly when you uninstall, unlike most applications these days

## Stuff to fix

Things to fix if I can ever get round to it

- [x] Switch to using pyinstaller exclusively over cx_Freeze
- [x] Simplify the loading process so it doesn't have to find itself
- [x] Make a `requirements.txt`
- [ ] Nicer icon
- [x] Replace the file tree with the newer [tkFileBrowser](https://github.com/jwansek/tkFileBrowser/) and try to fix any bugs in it, open the file tree at the correct place. Then it will use the windows API to get the correct icon for a file/directory
- [x] Reload image size on app resizing (not just maximizing)
