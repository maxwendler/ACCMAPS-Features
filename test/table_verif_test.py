import sys
import os.path as path
import unittest
# allows for import from parent folder
sys.path.append(path.abspath("../"))
import integrity
HEADERS_PATH = "./data/headers.csv"

class TestTable(unittest.TestCase):
    
    def test_headers(self):
        
        os_path = path.abspath(HEADERS_PATH)
        if not path.exists(os_path):
            print("Header test input file not found at " + HEADERS_PATH + "!")
            return

        # reading this way removes explicit newline characters
        input_f = open(HEADERS_PATH, "r")
        lines = input_f.read().splitlines()
        input_f.close()
        
        # TC1: Continously full cells without trailing empty ones.
        # Expected: valid header, 4 true header cells
        res, header_cells = integrity.verify_header(lines[0])
        self.assertEquals(True, res)
        self.assertEquals(4, len(header_cells))
            
        # TC2: Continously full cells with trailing empty ones.
        # Expected: valid header, 4 true header cells
        res, header_cells = integrity.verify_header(lines[1])
        self.assertEquals(True, res)
        self.assertEquals(4, len(header_cells))

        # TC3: Not continously full cells without trailing empty ones.
        # Expected: invalid header
        res, header_cells = integrity.verify_header(lines[2])
        self.assertEquals(False, res)

        # TC3: Not continously full cells with trailing empty ones.
        # Expected: invalid header
        res, header_cells = integrity.verify_header(lines[3])
        self.assertEquals(False, res)

if __name__ == '__main__':
    unittest.main()
