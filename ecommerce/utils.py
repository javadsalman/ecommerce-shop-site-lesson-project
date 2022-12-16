letter_eq = {
    'ə': 'e',
    'ğ': 'gh',
    'ö': 'o',
    'ü': 'u',
    'ş': 'sh',
    'ç': 'ch',
    'ı': 'i',
}

def convert_slug(text):
    result = ''
    for char in text.lower():
        if char.isalnum():
            result += letter_eq.get(char, char)
        if char.isspace():
            result += '-'
    return result
    