from __future__ import annotations

import io
import struct


class BinaryReader:
    """Read primitive values from a byte sequence."""

    def __init__(self, data: bytes):
        self.stream = io.BytesIO(data)

    def tell(self) -> int:
        return self.stream.tell()

    def remaining(self) -> int:
        current = self.stream.tell()

        self.stream.seek(0, io.SEEK_END)
        end = self.stream.tell()

        self.stream.seek(current)

        return end - current

    def read(self, size: int) -> bytes:
        data = self.stream.read(size)

        if len(data) != size:
            raise EOFError(
                f"Unexpected end of file at offset {self.tell()}"
            )

        return data

    def u8(self) -> int:
        return struct.unpack("<B", self.read(1))[0]

    def i16(self) -> int:
        return struct.unpack("<h", self.read(2))[0]

    def u16(self) -> int:
        return struct.unpack("<H", self.read(2))[0]

    def i32(self) -> int:
        return struct.unpack("<i", self.read(4))[0]

    def i64(self) -> int:
        return struct.unpack("<q", self.read(8))[0]

    def f32(self) -> float:
        return struct.unpack("<f", self.read(4))[0]

    def boolean(self) -> bool:
        return self.u8() != 0

    def read_7bit_int(self) -> int:
        result = 0
        shift = 0

        while True:
            byte = self.u8()

            result |= (byte & 0x7F) << shift

            if not byte & 0x80:
                return result

            shift += 7

            if shift >= 35:
                raise ValueError(
                    "Invalid 7-bit encoded integer"
                )

    def cs_string(self) -> str:
        length = self.read_7bit_int()

        if length == 0:
            return ""

        return self.read(length).decode(
            "utf-8",
            errors="replace",
        )