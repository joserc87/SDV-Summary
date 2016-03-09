#
# converts base 10 to base 62 for purpose of small URL identifiers
#


CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def dec2big(num):
	assert type(num) in [int,long]
	if num == 0:
		output = CHARS[0]
	elif num > 0:
		base = len(CHARS)
		output = ''
		while num > 0:
			rem = num%base
			output = CHARS[rem] + output
			num = (num-rem)/base
	else:
		raise IOError
	return output

if __name__ == "__main__":
	print dec2big(999999999999)