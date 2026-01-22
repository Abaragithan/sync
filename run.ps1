$ErrorActionPreference = "Stop"

$APP = (Get-Location).Path

docker run -it --rm `
  --network host `
  -v "${APP}:/app" `
  sync `
  /bin/bash
