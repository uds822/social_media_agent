import os
import re

directory = r'c:\Users\RAJAN\Downloads\Social_media_agent'

replacements = {
    r'(?i)eduplatform\s*[\-\–]\s*the\s*foundation': 'Edu Platform',
    r'EduPlatform': 'EduPlatform',
    r'eduplatform': 'eduplatform',
    r'EduPlatform': 'EduPlatform',
    r'theeduplatform\.com': 'eduplatform.com',
    r'(?i)gopalganj,\s*bihar': 'City, State',
    r'(?i)EduPlatformCoaching': 'EduPlatformCoaching',
    r'1234567890': '1234567890'
}

for root, dirs, files in os.walk(directory):
    if '.git' in root or 'node_modules' in root or '__pycache__' in root or '.venv' in root:
        continue
    for file in files:
        if file.endswith('.py') or file.endswith('.js') or file.endswith('.html') or file.endswith('.css') or file.endswith('.md') or file.endswith('.bat') or file.endswith('.sql'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                continue
                
            new_content = content
            for pattern, repl in replacements.items():
                new_content = re.sub(pattern, repl, new_content)
                
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

# Also rename the file if it contains eduplatform
for root, dirs, files in os.walk(directory):
    if '.git' in root or 'node_modules' in root:
        continue
    for file in files:
        if 'eduplatform' in file.lower():
            old_path = os.path.join(root, file)
            new_name = re.sub(r'(?i)eduplatform', 'eduplatform', file)
            new_path = os.path.join(root, new_name)
            os.rename(old_path, new_path)
            print(f"Renamed {old_path} to {new_path}")
