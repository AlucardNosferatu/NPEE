import base64
from hashlib import md5

from Crypto import Random
from Crypto.Cipher import AES


def encrypt_pass(message, passphrase=b'RjYkhwzx$2018!'):
    """
    salt随机密码字段，为什么随机？？？
    将bytes_to_key得到的秘钥及补全的明文以及随机字段进行base64加密得到最终的加密密码
    """
    salt = Random.new().read(8)
    key_iv = bytes_to_key(passphrase, salt, 32 + 16)
    key = key_iv[:32]
    iv = key_iv[32:]
    aes = AES.new(key, AES.MODE_CBC, iv)
    encrypted_bytes = base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message).encode()))
    return encrypted_bytes.decode()


def bytes_to_key(my_data, salt, output=48):
    """
    加密方法：
    将秘钥做MD5运算，得到的MD5值若小于需求的48位，将MD5后面加上秘钥再次求MD5值
    直到长度大于需求的48位
    为什么是48位？
    AES-256-CBC模式，秘钥长度必须是32位，偏差值必须是16位 32+16=48
    """
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    my_data += salt
    key = md5(my_data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + my_data).digest()
        final_key += key
    return final_key[:output]


def pad(data):
    """
    填充字段，明文的密码填充到16位，pkcs7填充
    填充字段是当前字段的 长度值 * 长度
    比如6位的密码 填充的内容就是 chr(16 - 6) * (16 - 6)
    """
    block_size = AES.block_size
    length = block_size - (len(data) % block_size)
    return data + (chr(length) * length)
