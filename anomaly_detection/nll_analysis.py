from anomaly_detection.utilities.external_call import run_shell
from anomaly_detection.utilities.custom_print import print_ts as print
from anomaly_detection.utilities.file_operations import cp, file_exist, gfd, gfn, join_path, mkdir
from anomaly_detection.registration_helper import image_registration
from scipy.stats import cumfreq
from skimage.exposure import match_histograms
import argparse


def main():

    parser = argparse.ArgumentParser(
        description='A simple anomaly detection algorithm for medical imaging '
        'based on multi-atlas image registration and negative log likelihood.')
    parser.add_argument('-s', '--source-images', nargs='+', type=str, required=True)
    parser.add_argument('-t', '--target-image', type=str, required=True)
    parser.add_argument('-o', '--output-dir', type=str, required=True)
    parser.add_argument('-c', '--do-n4-correction', choices = ['source', 'target', 'none', 'both'], type=str, default='source')
    parser.add_argument('-m', '--do-histogram-matching', action='store_true', default=True)

    args = parser.parse_args()

    # passing arguments
    source_images = args.source_images
    target_image = args.target_image
    output_dir = args.output_dir
    do_n4_correction = args.do_n4_correction
    do_histogram_matching = args.do_histogram_matching
    
    print('source images (%d in total):' % len(source_images), source_images)
    print('target image:', target_image)
    print('output directory:', output_dir)

    # OK, now let's do some dirty works :)

    ############################
    # N4 bias field correction #
    ############################

    print('bias field correction ...')
    n4_dir = mkdir(join_path(output_dir,'n4_corrected'))
    source_images_after_n4 = []
    target_image_after_n4 = ''

    # check if source images need to do N4 correction
    if do_n4_correction == 'source' or do_n4_correction == 'both':
        print('do N4 correction for source images.')
        for source_image in source_images:
            target_location = join_path(n4_dir, gfn(source_image))
            if file_exist(target_location) == False:
                run_shell('N4BiasFieldCorrection -c [200x200x200x200] -i %s -o %s' % (source_image, target_location))
            source_images_after_n4.append(target_location)
    else:
        print('no need to do N4 correction for source images.')
        for source_image in source_images:
            target_location = join_path(n4_dir, gfn(source_image))
            if file_exist(target_location) == False:
                cp(source_image, target_location) # copy source image to target location
            source_images_after_n4.append(target_location)
    
    # check if target image needs to do N4 correction
    if do_n4_correction == 'target' or do_n4_correction == 'both':
        print('do N4 correction for target image.')
        target_location = join_path(n4_dir, gfn(target_image))
        if file_exist(target_location) == False:
            run_shell('N4BiasFieldCorrection -c [200x200x200x200] -i %s -o %s' % (target_image, target_location))
        target_image_after_n4 = target_location
    else:
        print('no need to do N4 correction for target image.')
        target_location = join_path(n4_dir, gfn(target_image))
        if file_exist(target_location) == False:
            cp(target_image, target_location)
        target_image_after_n4 = target_location

    ###################
    # skull-stripping #
    ###################

    print('extract brain masks ...')
    source_brain_masks = []
    for source_image in source_images_after_n4:
        source_image_brain = join_path(gfd(source_image),gfn(source_image,no_extension=True)+'_brain.nii.gz')
        source_image_brain_mask = join_path(gfd(source_image),gfn(source_image,no_extension=True)+'_brain_mask.nii.gz')
        if file_exist(source_image_brain_mask) == False:
            run_shell('bet %s %s -m -n' % (source_image,source_image_brain))
        source_brain_masks.append(source_image_brain_mask)

    # do image registration
    print('start image registration ...')
    reg_dir = mkdir(join_path(output_dir,'registered'))
    for source_image, source_brain_mask in zip(source_images_after_n4, source_brain_masks):
        source_case = gfn(source_image, no_extension=True)
        target_case = gfn(target_image, no_extension=True)
        output_image = join_path(reg_dir, '%s_to_%s.nii.gz' % (source_case, target_case))
        output_mask = join_path(reg_dir, '%s_to_%s_mask.nii.gz' % (source_case, target_case))
        if file_exist(output_image) and file_exist(output_mask):
            continue
        else:
            image_registration(source_image, source_brain_mask, target_image_after_n4, output_image, output_mask)

    

    # # check if source images need to do histogram matching
    # hist_match_dir = mkdir(join_path(output_dir,'histogram_matched'))
    # if do_histogram_matching:
    #     for 







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



