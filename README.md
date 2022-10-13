# SSRSM web site [ssrsm.mk](https://ssrsm.mk)

## Dev mode
Run build on file change
```bash
while inotifywait -e close_write src/**/* src/*; do python3 ./build.py; done
```

## Templating Language details
[link](https://gist.github.com/VlatkoStojkoski/169b9ec984d63b1bbb8755dd13d793cc)