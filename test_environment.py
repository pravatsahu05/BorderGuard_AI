import sys
import platform


print("=" * 50)
print("       BORDERGUARD AI ENVIRONMENT TEST")
print("=" * 50)

print(f"Python version : {sys.version}")
print(f"Python path    : {sys.executable}")
print(f"Platform       : {platform.platform()}")
print(f"Architecture   : {platform.architecture()[0]}")

print("=" * 50)
print("Environment test completed successfully!")
print("=" * 50)
