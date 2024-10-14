def decimal_to_hex(self, decimal_num):
    """
    Convert a decimal number to a 4-digit hexadecimal string.
    
    :param decimal_num: Decimal number (e.g., 612345678901234567)
    :return: 4-digit hexadecimal string
    """
    hex_str = hex(decimal_num)[2:] + '00'  # Remove the '0x' prefix
    return hex_str.zfill(4) # Fill with leading zeros to ensure 4 digits

for i in range(1, 52):
    print(decimal_to_hex(i))