def isPalindrome(s: str):
    rev = s[::-1]
        
    if rev == s:
        return True
    else:
        return False



s: str = input()

s = s.lower()

cleans = ""

for i in s:
    if i.isalnum() and i != " ":
        cleans += i

print(isPalindrome(s))
