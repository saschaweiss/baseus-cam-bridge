# Changelog

## 0.1.13
- Restore PPPP DRW packet order on the media channels and drop duplicates.
  Retransmitted or reordered UDP packets corrupted frames (grey picture with
  only the top rows decoded).
- Decrypt AES-CBC frames (EnType 4) in addition to AES-ECB.
- Detailed `>>> stats` line every 20 s: reject reasons, codec flags,
  duplicate/reorder/gap counters, channel-2 traffic.

## 0.1.12
- `>>> stats` line with emitted, partial and rejected frames.
- New option `timestamps`: `wallclock` (default) or `fixed` (uses `framerate`).

## 0.1.11
- Send the XM heartbeat (cmd 2001) every 3 s. Without it the HomeStation ends
  every live session after about 120 s. New option `heartbeat` (0 = off).
- `live_refresh` is off by default; re-opening the stream made the HomeStation
  drop the session.

## 0.1.10
- ffmpeg stamps frames with their arrival time instead of a fixed framerate.
- Experimental option `live_refresh`.
- Add-on points at the saschaweiss fork.
