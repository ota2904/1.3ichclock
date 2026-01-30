from license_system import LicenseGenerator

key = 'MINIZ-STD2-UD5C-W3E4-6ESA'
print(f'Key: {key}')
print(f'Length: {len(key)}')
parts = key.split('-')
print(f'Parts: {parts}')
print(f'Part lengths: {[len(p) for p in parts]}')

# Calculate expected checksum
temp_key = ''.join(parts[1:4])
print(f'Temp key: {temp_key}')
expected = LicenseGenerator._calculate_checksum(temp_key)
print(f'Expected checksum: {expected}')
print(f'Actual checksum: {parts[4]}')
print(f'Valid: {LicenseGenerator.validate_key_format(key)}')
