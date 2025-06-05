def isPalindrome(s: str):
    rev = s[::-1]
        
    if rev == s:
        return True
    else:
        return False



s: str = input()

s = s.lower()

print(isPalindrome(s))
