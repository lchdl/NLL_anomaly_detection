from anomaly_detection.utilities.custom_print import print_ts as print
from anomaly_detection.utilities.file_operations import file_exist
import argparse

def main():

    parser = argparse.ArgumentParser(description='A simple anomaly detection algorithm for medical imaging based on multi-atlas image registration and negative log likelihood.')
    parser.add_argument('-s', '--source-images', nargs='+',type=str,required=True)
    parser.add_argument('-t', '--target-image',type=str,required=True)
    parser.add_argument('-o', '--output-dir',required=True, type=str)
    parser.add_argument('--do-n4-correction', choices = ['source', 'target', 'none', 'both'],type=str, default='source')
    
    args = parser.parse_args()

    # passing arguments
    source_images = args.source_images
    target_image = args.target_image
    output_dir = args.output_dir
    
    # OK, now let's do some dirty works :)

    print('source images (%d in total):')
    for source_image in source_images:
        assert file_exist(source_image), 'Error, file "%s" not exist!' % source_image
        print(source_image)
    print('target image:')
    print(target_image)
    print('output directory:')
    print(output_dir)
    exit()



    print('MALS : group registration')
    print('registration start!')
    print('number of workers : %d' % num_workers)
    
    print('creating directory "%s" for saving output images.' % save_dir)
    mkdir(save_dir)
    basedir = cwd()

    source_dataset = load_csv(source_csv,keys=['case','data','mask'])
    target_dataset = load_csv(target_csv,keys=['case','data'])

    normal_cases = len(source_dataset['case'])
    patient_cases = len(target_dataset['case'])

    print('ok, I found %d normal cases, %d patients. Time to do some dirty works...' % (normal_cases, patient_cases))

    task_list = []

    for i in range(normal_cases):
        for j in range(patient_cases):
            source_case_name = source_dataset['case'][i]
            target_case_name = target_dataset['case'][j]
            source_dict = {
                'case': source_case_name,
                'data': source_dataset['data'][i],
                'mask': source_dataset['mask'][i]
            }
            target_dict = {
                'case': target_case_name,
                'data': target_dataset['data'][j]
            }
            task_args = (source_dict, target_dict, save_dir, basedir)
            task_list.append(task_args)

    p = Pool(processes=num_workers)
    p.map(worker_func, task_list)
    p.close()
    p.join()

    print('all finished.')



