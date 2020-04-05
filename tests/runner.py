import unittest
import subprocess

BASEPATH="/home/mikael/workspace/formula"
BINARY=f"{BASEPATH}/.venv/bin/python"

class Tester(unittest.TestCase):

    def run_file(self, filepath):
        proc = subprocess.run([BINARY, f"{BASEPATH}/main.py", "--test", f"{BASEPATH}/tests/{filepath}"],
                             capture_output=True, cwd=BASEPATH)
        stdout = proc.stdout.decode("utf-8")
        stderr = proc.stderr.decode("utf-8")
        if proc.returncode != 0:
            print(f"test {filepath} failed")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
        return proc.returncode, stdout, stderr

    def test_exit(self):
        self.run_file("do_exit.test")

    def test_basic(self):
        self.run_file("basic.test")

    #def test_die(self):
    #    self.run_file("die.test")

    #def test_tutorial_nokill(self):
    #    self.run_file("tutorial_nokill.test")

if __name__ == "__main__":
    unittest.main()