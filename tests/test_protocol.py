"""Offline tests for heartbeat framing and DRW reordering."""
import random
import struct
import unittest

from Crypto.Cipher import AES

from baseus_bridge import protocol as P


class HeartbeatTest(unittest.TestCase):
    def test_layout(self):
        h = P.build_heartbeat()
        self.assertEqual(len(h), 24)
        self.assertEqual(struct.unpack_from("<I", h, 0)[0], P.MAGIC_TO_DEV)
        self.assertEqual(h[4], 0x10)
        self.assertEqual(h[5], 0xE0)
        self.assertEqual(struct.unpack_from("<H", h, 12)[0], 0)  # no payload
        self.assertEqual(struct.unpack_from("<H", h, 14)[0], P.CMD_HEARTBEAT)


def _stream(key, n_frames=120):
    """Build an encrypted XM A/V byte stream and the frames it carries."""
    rnd = random.Random(1)
    frames, stream = [], bytearray()
    for fn in range(n_frames):
        start = b"\x00\x00\x00\x01\x27" if fn % 25 == 0 else b"\x00\x00\x00\x01\x21"
        nal = start + bytes(rnd.randrange(256) for _ in range(rnd.randrange(300, 6000)))
        frames.append(nal)
        pad = 16 - len(nal) % 16
        blob = AES.new(key, AES.MODE_ECB).encrypt(nal + bytes([pad]) * pad)
        parts = [blob[i:i + 1000] for i in range(0, len(blob), 1000)]
        for i, part in enumerate(parts, 1):
            h = bytearray(24)
            h[0:4] = struct.pack("<I", P.MAGIC_TO_APP)
            h[4], h[5] = 0x11, 1 if fn % 25 == 0 else 2
            struct.pack_into("<HHHH", h, 6, fn, len(parts), i, len(part))
            stream += h + part
    return frames, bytes(stream)


class DrwReorderTest(unittest.TestCase):
    def setUp(self):
        self.key = P.aes_key("secret")
        self.frames, stream = _stream(self.key)
        start = 0xFFA0  # cross the 16-bit index wrap
        self.pkts = [((start + i) & 0xFFFF, stream[o:o + 1024])
                     for i, o in enumerate(range(0, len(stream), 1024))]

    def _run(self, pkts):
        reorder, reasm, out = P.DrwReorder(), P.VideoReassembler(self.key), []
        for idx, chunk in pkts:
            for data in reorder.feed(idx, chunk):
                out.extend(reasm.feed(data))
        return out, reorder

    def test_duplicates_and_swaps_are_repaired(self):
        rnd = random.Random(2)
        noisy = []
        for p in self.pkts[:1] + self.pkts[1:]:
            noisy.append(p)
            if rnd.random() < 0.1:
                noisy.append(p)  # retransmit
        for i in range(1, len(noisy) - 1):  # keep the first packet first
            if rnd.random() < 0.1:
                noisy[i], noisy[i + 1] = noisy[i + 1], noisy[i]
        out, reorder = self._run(noisy)
        self.assertEqual(out, self.frames)
        self.assertGreater(reorder.dups, 0)
        self.assertEqual(reorder.gaps, 0)

    def test_lost_packet_is_skipped(self):
        out, reorder = self._run(self.pkts[:200] + self.pkts[201:])
        self.assertEqual(reorder.gaps, 1)
        self.assertGreaterEqual(len(out), len(self.frames) - 2)
        self.assertLess(len(out), len(self.frames))


if __name__ == "__main__":
    unittest.main()
