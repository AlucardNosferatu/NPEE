import random


def bit_to_list(t, n):
    s = [0 for i in range(n)]
    i = -1
    while t != 0:
        s[i] = t % 2
        t = t >> 1
        i -= 1
    return s


def bin4digits_dec(bin_list):
    sum_dec_bin4digits = 0
    for i in range(0, 4):
        if bin_list[i] == 1:
            sum_dec_bin4digits += 2 ** (3 - i)
    return sum_dec_bin4digits


weights = [128, 64, 32, 16, 8, 4, 2, 1, 0.5, 0.25, 0.125, 0.0625]
hex_table = [
    '0', '1', '2', '3',
    '4', '5', '6', '7',
    '8', '9', 'A', 'B',
    'C', 'D', 'E', 'F'
]

selected = []

size = random.randrange(1, len(weights) + 1)

while len(selected) < size:
    new_selected = random.choice(weights)
    if new_selected not in selected:
        selected.append(new_selected)
selected.sort(reverse=True)
sum_dec = 0
template_bin = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for weight in selected:
    sum_dec += weight
    digit = weights.index(weight)
    template_bin[digit] = 1

exponent_val = 7 - template_bin.index(1)
template_bin = template_bin[template_bin.index(1):]
exponent_bits = bit_to_list(exponent_val + 127, 8)
result_bin = [0] + exponent_bits + template_bin[1:]
while len(result_bin) < 32:
    result_bin.append(0)
result_str = []
for i in range(0, 32, 4):
    # print(result_bin[i:i + 4])
    result_str.append(hex_table[bin4digits_dec(result_bin[i:i + 4])])
print(sum_dec)

fuck = input('your answer:')
while fuck != ''.join(result_str):
    if fuck == 'fuck':
        break
    print('wrong!')
    fuck = input('your answer (or type "fuck" for the answer):')

print()
print('Your input: ' + fuck)
if fuck == ''.join(result_str):
    print('Bingo!')
else:
    print('LOL')
print('the answer is: ' + ''.join(result_str) + 'H')
# print(size)
# print(exponent_val)
# print(selected)
# print(exponent_bits)
# print(template_bin)
# print(result_bin)
