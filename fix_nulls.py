with open('app/services.py', 'rb') as f:
    content = f.read()

cleaned = content.replace(b'\x00', b'')

with open('app/services.py', 'wb') as f:
    f.write(cleaned)

print("Null bytes removed successfully")
