from anomaly_detection.utilities.file_operations import file_exist
import csv
import pickle
import nibabel as nib
import numpy as np

def load_csv(file_path, key_names):
    parsed_dataset = {}
    
    with open(file_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file,delimiter=',',quotechar='"')
        table_head = None
        for row in csv_reader:
            if table_head is None: 
                table_head = row
            else:
                for key in key_names:
                    if key not in table_head:
                        raise Exception('Cannot find key name "%s" in CSV file "%s". Expected key names can be %s.' % \
                            (key,file_path, table_head))
                    else:
                        column_index = table_head.index(key)
                        if key not in parsed_dataset:
                            parsed_dataset[key] = [] # create list
                        parsed_dataset[key].append(row[column_index])

    return parsed_dataset

def save_pkl(obj, pkl_path):
    with open(pkl_path,'wb') as f:
        pickle.dump(obj,f)

def load_pkl(pkl_path):
    content = None
    with open(pkl_path,'rb') as f:
        content = pickle.load(f)
    return content

def load_nifti_simple(path, return_type='float32'):
    if return_type is None:
        return nib.load(path).get_fdata()
    else:
        return nib.load(path).get_fdata().astype(return_type)

def save_nifti_simple(data,path): # save NIFTI using the default header
	nib.save(nib.Nifti1Image(data.astype('float32'),affine=np.eye(4)),path)

def get_nifti_header(nii_path):
    return nib.load(nii_path).header.copy()

def get_nifti_data(nii_path, return_type='float32'):
    return nib.load(nii_path).get_fdata().astype(return_type)

def save_nifti_with_header(data, header, path):
    nib.save(nib.nifti1.Nifti1Image(data.astype('float32'), None, header=header),path)

# synchronize NIFTI file header
def sync_nifti_header(source_path, target_path, output_path):
    target_header = nib.load(target_path).header.copy()
    source_data = nib.load(source_path).get_fdata()
    save_nifti_with_header(source_data, target_header, output_path)

