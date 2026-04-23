# Machine Vision

### Pictures Unzip Automation (in terminal):
```bash
find pics -name "*.zip" -exec sh -c 'unzip -o "$1" -d "$(dirname "$1")"' _ {} \;
```