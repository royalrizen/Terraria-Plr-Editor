from __future__ import annotations

import struct


class BinaryWriter:
    """Write primitive values into a mutable byte buffer."""

    def __init__(self, data: bytearray):
        self.data = data

    def write(self, offset: int, data: bytes) -> None:
        end = offset + len(data)

        if offset < 0 or end > len(self.data):
            raise IndexError(
                f"Write at offset {offset} with "
                f"{len(data)} bytes exceeds buffer size "
                f"{len(self.data)}"
            )

        self.data[offset:end] = data

    def u8(self, offset: int, value: int) -> None:
        if not 0 <= value <= 255:
            raise ValueError(
                "u8 value must be between 0 and 255"
            )

        self.write(
            offset,
            struct.pack("<B", value),
        )

    def i16(self, offset: int, value: int) -> None:
        self.write(
            offset,
            struct.pack("<h", value),
        )

    def i32(self, offset: int, value: int) -> None:
        self.write(
            offset,
            struct.pack("<i", value),
        )

    def i64(self, offset: int, value: int) -> None:
        self.write(
            offset,
            struct.pack("<q", value),
        )

    def f32(self, offset: int, value: float) -> None:
        self.write(
            offset,
            struct.pack("<f", value),
        )