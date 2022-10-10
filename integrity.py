from io import TextIOWrapper
import os.path as path
from typing import Dict, Tuple
import pygtrie as trie

# wrapper function for: 'open if exists, exit if not'
def open_file(path_str: str) -> TextIOWrapper:
    os_path = path.realpath(path_str)
    if not path.exists(os_path):
        print("File not found at " + path_str + "!")
        exit()
    return open(path_str, "r")

# checks if cells of provided header line are filled continously
# returns: check result, list of continous non-empty cells for valid headers
def verify_header(header: str) -> Tuple[bool, list]:
    cell_strs = header.split("|")
    # find position of last non-empty cell
    cell_idx = -1
    for cell in cell_strs:
        if cell == "":
            break
        cell_idx += 1
    true_header_cells = cell_strs[:(cell_idx + 1)]
    # verif. success if no empty cell / only one after the non-empty ones
    if cell_idx == len(cell_strs) - 1:
        return True, true_header_cells
    # if other non-empty cell occurs: failure
    # else: success
    else:
        for empty_cell_idx in range(cell_idx + 1, len(cell_strs)):
            cell = cell_strs[empty_cell_idx]
            if cell != "":
                return False, []
        return True, true_header_cells

# Parses csv file of feature from given path into prefix tree (trie).
# Also checks syntax and content:
# - valid header (exit if not)
# If do_validate == true:
# - prints non-empty lines without name attribute value to console
# - prints non-header lines with values in columns beyond the ones specified by header to console
def read_file_to_check(path: str, do_validate=True) -> trie.CharTrie:

    file = open_file(path)
    # reading this way removes explicit newline characters
    lines = file.read().splitlines()
    file.close()

    # parse HEADER: names for attributes of features (name is key & exluded) #
    header = lines[0]
    # header verification
    isValidHeader, true_header_cells = verify_header(header)
    if not isValidHeader:
        print("The provided file does not have a valid table header.")
        exit()
    attr_num = len(true_header_cells)
    attr_names = lines[0].split("|")[1:attr_num]
    
    # parse features into dict-like trie: feat_name (key) -> attribute dict (value)
    no_name_feats = {}
    too_many_attr_feats = []
    res_trie = trie.CharTrie()
    for i in range(1, len(lines)):
        feat_line = lines[i]
        
        # split in cells & remove any spaces / ' / " occuring from manual oversight / export 
        cell_strs = list(map( lambda str: str.strip().strip('"').strip("'"), feat_line.split("|") ))
        feat_name = cell_strs[0]

        # checking syntax and content of table body rows
        if do_validate:
            # check if there are more attribute values than attributes & save line if
            last_val_idx = 0
            for j in range(1, len(cell_strs)):
                if cell_strs[j] != "":
                    last_val_idx = j
            if (last_val_idx + 1) > attr_num:
                too_many_attr_feats.append(feat_line)

        # check if feature name exists & save line if not
        # needs to be done anyways, see below
        if feat_name == "":
            no_name_feats[i] = feat_line
        # save feature in trie for lookup
        # can only be saved for lookup with name, as it's key in trie
        else:
            feat_attrs = cell_strs[1:attr_num]
            feat_attrs_dict = {}
            for j in range(len(attr_names)):
                feat_attrs_dict[attr_names[j]] = feat_attrs[j]
            res_trie[feat_name] = feat_attrs_dict

    # Output of faulty feature lines.
    if do_validate:
        if len(no_name_feats) > 0:
            print("Feature lines without name in " + path + " :\n")
            for line_num in no_name_feats.keys():
                print(str(line_num) + ": " + no_name_feats[line_num] + "\n")
            print("\n")
        
        if len(too_many_attr_feats) > 0:
            print("Feature lines with too many attributes in " + path + " :\n")
            for line in too_many_attr_feats:
                print(line + "\n")
            print("\n")

    return res_trie

# Checks if the given features match w.r.t. attribute values except their name; considering only matches in the 
# attributes of origin_attrs.
# Returns a fault statement if mismatch is found, otherwise "".
def compare_attr_vals(origin_attrs: Dict[str, str], feat_attrs: Dict[str, str], feat_name: str) -> str:
    unmatched_attrs = []
    for attr in origin_attrs.keys():
        if origin_attrs[attr] != feat_attrs[attr]:
            unmatched_attrs.append(attr)
    if len(unmatched_attrs) > 0:
        unmatched_attrs_str = ""
        for i in range(len(unmatched_attrs) - 1):
            unmatched_attrs_str += unmatched_attrs[i] + ", "
        unmatched_attrs_str += unmatched_attrs[len(unmatched_attrs) - 1]
        return "Mismatch of following attributes of feature " + "'" + feat_name + "': " + unmatched_attrs_str + "\n"
    else:
        return ""         

# Class containing the validation functions.
# Acts as temporary storage for prefix-trees of analyzed CSV files, so they can be loaded only once for all the validations.
# Each validation function writes found issues in a file in ./results, if any are found.
class FileValidator:
    def __init__(self) -> None:
        # Prefix trees ('tries') storing manually sorted & altered features.
        self.indoor = read_file_to_check("./data/indoor.csv")
        self.outdoor = read_file_to_check("./data/outdoor.csv")
        self.buildings = read_file_to_check("./data/buildings.csv")
        self.renamed = read_file_to_check("./data/renamed.csv", False)
        self.edited = read_file_to_check("./data/edited.csv", False)
        self.original = read_file_to_check("./data/Alignment.csv", False)
    
    # Check if all features from Alignment.csv are present in the manually produced files; may be with new name
    # Or if its deletion is documented.
    def validate_forward_existance(self):    
        log_lines = []
        for origin_feat_name in self.original.keys():
            origin_feat_attrs = self.original[origin_feat_name]
            # to show something is happening
            print(origin_feat_name)
            if origin_feat_name != "":
                # Look up existance of original name in the output prefix trees;
                # check if both feature entries match in the attributes of the original Alignment.csv
                if origin_feat_name in self.indoor.keys():
                    compare_res = compare_attr_vals(origin_feat_attrs, self.indoor[origin_feat_name], origin_feat_name)
                    if compare_res != "":
                        log_lines.append(compare_res)
                elif origin_feat_name in self.outdoor.keys():
                    compare_res = compare_attr_vals(origin_feat_attrs, self.outdoor[origin_feat_name], origin_feat_name)
                    if compare_res != "":
                        log_lines.append(compare_res)
                elif origin_feat_name in self.buildings.keys():
                    compare_res = compare_attr_vals(origin_feat_attrs, self.buildings[origin_feat_name], origin_feat_name)
                    if compare_res != "":
                        log_lines.append(compare_res)
                elif origin_feat_name in self.renamed.keys():
                    # Look up existance of altered name in the output prefix trees;
                    # check if both feature entries match in the attributes of the original Alignment.csv
                    new_feat_name = self.renamed[origin_feat_name]["neuer Name"]
                    if new_feat_name in self.indoor.keys():
                        # compare attribute values
                        compare_res = compare_attr_vals(origin_feat_attrs, self.indoor[new_feat_name], origin_feat_name)
                        if compare_res != "":
                            log_lines.append(compare_res)
                    elif new_feat_name in self.outdoor.keys():
                        # compare attribute values
                        compare_res = compare_attr_vals(origin_feat_attrs, self.outdoor[new_feat_name], origin_feat_name)
                        if compare_res != "":
                            log_lines.append(compare_res)
                    elif new_feat_name in self.buildings.keys():
                        # compare attribute values
                        compare_res = compare_attr_vals(origin_feat_attrs, self.buildings[new_feat_name], origin_feat_name)
                        if compare_res != "":
                            log_lines.append(compare_res)
                    # no check for documented deletion as features were only renamed when not deleting them
                    # i.e. only remaining possible is that feature is missing
                    else:
                        log_lines.append("Missing feature: " + origin_feat_name + "\n")
                # feature not found under original or altered name 
                # check if its deletion is documented, in which case everything's fine
                elif origin_feat_name in self.edited.keys():
                    if "Loeschung" not in self.edited[origin_feat_name]["Korrektur"]:
                        log_lines.append("Missing feature: " + origin_feat_name + "\n")
                # otherwise: feature is missing
                else:
                    log_lines.append("Missing feature: " + origin_feat_name + "\n")

        # only print issue log if there are any
        if len(log_lines) > 0:
            log_file = open("./results/forward_existance_issues_log.csv", "w")
            for line in log_lines:
                log_file.write(line)
            log_file.close()
            print("Issues that have been found were output to ./results/forward_existance_issues_log.csv!")
        else:
            print("No issues were found!")    
    
    # Check if all features present in the manually produced (may be under altered name) files were in
    # the original Alignment.csv (under their original name).
    # Check if features only occur once. 
    def validate_backward_existance(self):
        log_lines = []
        feats = self.indoor.keys() + self.buildings.keys() + self.outdoor.keys()
        checked_feats = {"$this is a set, linter!$"} 
        for feat_name in feats:
            # to show something is happening
            print(feat_name)
            # discover feature existing in multiples
            if feat_name in checked_feats:
                log_lines.append("Feature that exists multiple times: " + feat_name + "\n")
                pass
            
            # figure out if lookup under altered or original name
            has_old_name = False
            old_feat_name = ""
            for old_feat_idx in self.renamed.keys():
                if self.renamed[old_feat_idx]["neuer Name"] == feat_name:
                    has_old_name = True
                    old_feat_name = old_feat_idx

            # lookup in data of Alignment.ccsv
            if not has_old_name:
                if feat_name not in self.original.keys():
                    log_lines.append("Feature that's not in original Alignment.csv: " + feat_name + "\n")
            else:
                if old_feat_name not in self.original.keys():
                    log_lines.append("Feature that's not in original Alignment.csv: " + feat_name + "\n")

            checked_feats.add(feat_name)
        
        # only print issue log if there are any
        if len(log_lines) > 0:
            log_file = open("./results/backward_existance_issues_log.csv", "w")
            for line in log_lines:
                log_file.write(line)
            log_file.close()
            print("Issues that have been found were output to ./results/backward_existance_issues_log.csv!")
        else:
            print("No issues were found!")    
        
    # Checks if features with documented deletion are in fact not part of manually created tables 
    # (may have altered name, even if it shouldn't be the case, see line 182).
    def validate_deletion(self):
        log_lines = []
        for feat_name in self.edited.keys():
            # to show something is happening
            print(feat_name) 
            if "Loeschung" in self.edited[feat_name]["Korrektur"]:
                is_deleted = True
                # lookup under altered or original name
                if feat_name not in self.renamed.keys():
                    is_deleted = not (feat_name in self.indoor.keys() or feat_name in self.outdoor.keys() or feat_name in self.buildings.keys())
                else:
                    new_feat_name = self.renamed[feat_name]["neuer Name"]
                    is_deleted = not (new_feat_name in self.indoor.keys() or new_feat_name in self.outdoor.keys() or new_feat_name in self.buildings.keys())
                if not is_deleted:
                    log_lines.append("Feature existing despite claimed deletion:" + feat_name + "\n")
        
        # only print issue log if there are any
        if len(log_lines) > 0:
            log_file = open("./results/deletion_issues_log.csv", "w")
            for line in log_lines:
                log_file.write(line)
            log_file.close()
            print("Issues that have been found were output to ./results/deletion_issues_log.csv!")
        else:
            print("No issues were found!")      

if __name__ == "__main__":
    validator = FileValidator()
    # can be turned into comments to validate selectively
    validator.validate_forward_existance()
    validator.validate_deletion()
    validator.validate_backward_existance()

    # Log number of input and output features as well as number of deletions.
    # Log difference of numbers: If input_num - deletions - output_num = 0, consistency is indicated. 
    file = open("./results/feature_counts.csv", "w")
    input_feat_num = len(validator.original.keys())
    file.write("Number of original features: " + str(input_feat_num) + "\n")
    output_feat_num = len(validator.indoor.keys()) + len(validator.outdoor.keys()) + len(validator.buildings.keys())
    file.write("Number of output features: " + str(output_feat_num) + "\n")
    deletion_num = 0
    for origin_feat_name in validator.edited.keys():
        if "Loeschung" in validator.edited[origin_feat_name]["Korrektur"]:
            deletion_num += 1
    file.write("Number of deletions: " + str(deletion_num) + "\n")
    feat_num_diff = input_feat_num - deletion_num - output_feat_num
    file.write("Difference in feature number: " + str(feat_num_diff))
    file.close()