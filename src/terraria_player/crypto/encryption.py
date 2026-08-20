from __future__ import annotations

from Crypto.Cipher import AES

from terraria_player.constants import (
    PLAYER_ENCRYPTION_KEY,
)


def decrypt_player(
    data: bytes,
) -> bytes:
    """
    Decrypt a Terraria player file.

    Terraria player files use AES-CBC with the
    same key for both the key and IV.
    """

    if not data:
        raise ValueError(
            "Empty player file."
        )

    if len(data) % 16 != 0:
        raise ValueError(
            "PLR file size is not a multiple "
            "of 16 bytes."
        )

    cipher = AES.new(
        PLAYER_ENCRYPTION_KEY,
        AES.MODE_CBC,
        PLAYER_ENCRYPTION_KEY,
    )

    decrypted = cipher.decrypt(data)

    if not decrypted:
        raise ValueError(
            "Empty decrypted data."
        )

    # Terraria uses PKCS#7-style padding.
    padding = decrypted[-1]

    if 1 <= padding <= 16:
        if (
            decrypted[-padding:]
            == bytes([padding]) * padding
        ):
            decrypted = decrypted[:-padding]

    return decrypted


def encrypt_player(
    data: bytes,
) -> bytes:
    """
    Encrypt decrypted Terraria player data.

    PKCS#7-style padding is added before
    AES-CBC encryption.
    """

    if not data:
        raise ValueError(
            "Cannot encrypt empty player data."
        )

    padding = 16 - (
        len(data) % 16
    )

    padded = (
        data
        + bytes([padding]) * padding
    )

    cipher = AES.new(
        PLAYER_ENCRYPTION_KEY,
        AES.MODE_CBC,
        PLAYER_ENCRYPTION_KEY,
    )

    return cipher.encrypt(padded)