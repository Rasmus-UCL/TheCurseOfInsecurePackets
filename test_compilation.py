import os
import py_compile
import sys

def main():
    skip = {'.venv', 'build', 'dist', '__pycache__', '.git', 'Komprimeret arkiv'}
    count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in skip]
        if any(s in root for s in skip):
            continue
        for f in files:
            if f.endswith('.py'):
                p = os.path.join(root, f)
                print(f"Compiling: {p}")
                py_compile.compile(p, doraise=True)
                count += 1
    print(f"SUCCESS: Compiled {count} python files without error.")

if __name__ == "__main__":
    main()
