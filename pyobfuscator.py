generic_import = """
import base64

def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return "".join("\\\\x%02x" % ord(x) for x in enc)

def decode(key, enc):
    dec = []
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)
"""
runtime_modifier = """
import subprocess, sys
%s
if sys.argv[0] != "-c":
    self = open(sys.argv[0], "wb")
    self.write(decode("%s","%s"))
    self.close()
    subprocess.Popen(["python", sys.argv[0]]).communicate()
"""
import os
import subprocess
import sys
import random
import time
exec generic_import

def _compile(path):
    DEVNULL = open(os.devnull, 'w')
    filename = os.path.split(path)[1].split(".")[0]
    process = subprocess.Popen(["python", "-c", "import %s" % filename], stdout=DEVNULL, stderr=DEVNULL)
    process.communicate()
    time.sleep(1)
    if not process.returncode > -1:
        process.kill()
    try:
        read = open(path + "c", "rb")
        _content = read.read()
        read.close()
        os.remove(path + "c")
    except Exception as e:
        print e
        return ""
    return _content

def random_password(lenght=32):
    charset = "abcdefghijklmnoprstuvxyzABCDEFGHIJKLMNOPQRSTUVXYZ0123456789"
    return "".join(charset[random.randint(0, len(charset)-1)] for x in range(0, lenght))

def overwrite(path, content):
    w = open(path, "wb")
    w.write(content)
    w.close()

def copyfile(path1, path2):
    w = open(path1, "rb")
    w2 = open(path2, "wb")
    w2.write(w.read())
    w.close()
    w2.close()

if __name__ == "__main__":
    print "PyObfuscator - Simple Python encrypter/obfuscator (oneshot-file) \n"
    if len(sys.argv) == 2:
        pyfile = sys.argv[1]
        if os.path.isfile(pyfile):
            newdir = os.path.split(pyfile)[0]
            os.chdir(newdir if newdir != "" else ".")
            enc = "encrypt_%s" % os.path.split(pyfile)[1]
            copyfile(os.path.split(pyfile)[1], enc)
            print "[+] Compiling source code..."
            compiled = _compile(enc)
            if compiled == "":
                print "[-] Error while compiling first stage"
                sys.exit(-1)
            print "[+] Generating unique password..."
            password = random_password()
            print "[+] Generating self modifying code"
            overwrite(enc, runtime_modifier % (generic_import, password, encode(password, compiled)))
            print "[+] Compiling self modifying code"
            compiled = _compile(enc)
            if compiled == "":
                print "[-] Error while compiling second stage"
                sys.exit(-1)
            print "[+] Saving file as '%s'" % enc
            overwrite(enc, compiled)
        else:
            sys.stderr.write("Error: file %s not found\n" % pyfile)
    else:
        sys.stderr.write("Usage: %s <python file>\n" % sys.argv[0])
