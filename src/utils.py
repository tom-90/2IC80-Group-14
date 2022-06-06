# Convert python string to unicode
def stu(str):
    if str == None:
        return str
    return str.decode('utf-8', 'ignore')

# Convert unicode to python string
def uts(str):
    if str == None:
        return str
    return str.encode('latin-1')