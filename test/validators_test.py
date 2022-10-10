import sys
import os.path as path
# allows for import from parent folder
sys.path.append(path.abspath("../"))
import integrity

ORIGINAl_PATH = "./data/original.csv"
DELETIONS_PATH = "./data/edited.csv"
FORWARD_MISSING_PATH = "./data/forward_missing.csv"
FORWARD_WRONG_ATTRS_PATH = "./data/forward_wrong_attrs.csv"
FORWARD_CORRECT_PATH = "./data/forward_correct.csv"
BACKWARD_WRONG_NEW_PATH = "./data/backward_wrong_new.csv"
BACKWARD_CORRECT_PATH = FORWARD_CORRECT_PATH
DELETION_NOT_DONE_PATH = FORWARD_CORRECT_PATH
DELETION_CORRECT_PATH = "./data/deletion_correct.csv"

class TestValidation():
    
    def __init__(self) -> None:
        self.validator = integrity.FileValidator()

    # Only test one variant at a time!
    def test_forward_validation(self):
        
        # log file should note 'a bioreactor ...' and 'a passage on foot ...' are missing
        #self.validator.indoor = integrity.read_file_to_check(FORWARD_MISSING_PATH)
        
        # log file should note missing OSM tags for '(health) clinic ...'
        # self.validator.indoor = integrity.read_file_to_check(FORWARD_WRONG_ATTRS_PATH)
        
        # no issues -> no new log file
        self.validator.indoor = integrity.read_file_to_check(FORWARD_CORRECT_PATH)
        
        self.validator.validate_forward_existance()
    
    # Only test one variant at a time!
    def test_backward_validation(self):

        # log file should note 'abbreviation ...' is not in original file
        # self.validator.indoor = integrity.read_file_to_check(BACKWARD_WRONG_NEW_PATH)

        # no issues -> no new log file
        self.validator.indoor = integrity.read_file_to_check(BACKWARD_CORRECT_PATH)

        self.validator.validate_backward_existance()
    
    # Only test one variant at a time!
    def test_deletion(self):
        self.validator.edited = integrity.read_file_to_check(DELETIONS_PATH)

        # log file should not that 'a passage ...' was not deleted as documented
        # self.validator.indoor = integrity.read_file_to_check(DELETION_NOT_DONE_PATH)

        # no issues -> no log
        self.validator.indoor = integrity.read_file_to_check(DELETION_CORRECT_PATH)

        self.validator.validate_deletion()

# Can test one variant of all at once, or only one variant of one.
if __name__ == '__main__':
    test = TestValidation()
    # test.test_forward_validation()
    # test.test_backward_validation()
    test.test_deletion()