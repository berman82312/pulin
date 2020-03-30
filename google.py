prime_str = '23571113'
prime_list = [2,3,5,7,11,13]
max_prime = 13
max_length = 8

def find_next_prime():
    global max_prime, max_length, prime_str, prime_list
    current = max_prime + 1
    while True:
        is_prime = True
        for prime in prime_list:
            rest = current % prime
            if rest == 0:
                is_prime = False
                break

        if is_prime:
            max_prime = current
            prime_list.append(current)
            current = str(current)
            max_length += len(current)
            prime_str += current
            break
        else:
            current += 1

def solution(i):
    # Your code here
    start = i
    end = i + 5
    while max_length < end:
        find_next_prime()
    return prime_str[start:end]
