# Changelog

## 0.1.14
- Cleanup: removed the test options `live_refresh`, `timestamps` and
  `framerate`, the detailed `>>> stats` line and the AES-CBC experiment.
  Leftover values in your configuration are ignored.
- Kept: XM heartbeat (`heartbeat`, default 3 s), DRW packet reordering and
  arrival-time timestamps. Same code as the upstream pull request.

## 0.1.13
- Restore PPPP DRW packet order on the video channel and drop duplicates.
  Retransmitted or reordered UDP packets corrupted frames (grey picture with
  only the top rows decoded).

## 0.1.11
- Send the XM heartbeat (cmd 2001) every 3 s. Without it the HomeStation ends
  every live session after about 120 s.

## 0.1.10
- ffmpeg stamps frames with their arrival time instead of a fixed framerate.
- Add-on points at the saschaweiss fork.
