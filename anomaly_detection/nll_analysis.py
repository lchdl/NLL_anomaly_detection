from numpy.lib.utils import source
from anomaly_detection.utilities.external_call import run_shell
from anomaly_detection.utilities.custom_print import print_ts as print
from anomaly_detection.utilities.file_operations import cp, file_exist, gfd, gfn, join_path, mkdir
from anomaly_detection.utilities.registration_helper import image_registration, save_nifti_with_header
from anomaly_detection.utilities.image_operations import cutoff
from anomaly_detection.utilities.basic_data_io import get_nifti_header, load_nifti_simple
from anomaly_detection.utilities.image_operations import min_max_norm, mean_filter, median_filter, group_mean, group_std
from skimage.exposure import match_histograms
import numpy as np
import argparse

def nll(source_image_path, reference_image_paths, reference_mask_paths,
    mean_filter_size=(1,1,1), median_filter_size=(5,5,5), min_std = None):

    x_prime = min_max_norm(load_nifti_simple(source_image_path))
    if mean_filter_size!=(1,1,1):
        x_prime = mean_filter(x_prime,mean_filter_size)

    # calculate each x and save
    list_of_x_i = []
    sample_size = len(reference_image_paths)
    for i in range(sample_size):
        reference_path = reference_image_paths[i]
        x_i = min_max_norm(load_nifti_simple(reference_path))
        if mean_filter_size!=(1,1,1):
            x_i = mean_filter(x_i,mean_filter_size)
        list_of_x_i.append(x_i)
    # calculate NLL anomaly score
    sigma = group_std(list_of_x_i)
    if min_std == None: 
        sigma += 0.00001 # add a small number to avoid division by zero
    else: 
        sigma = np.where(sigma<min_std, min_std, sigma)
    mu = group_mean(list_of_x_i)
    anomaly = np.power(x_prime-mu,2)/(2*np.power(sigma,2)) + np.log(sigma*2.506)  # sqrt(2*pi) = 2.506
    # load masks and apply
    m_i = [load_nifti_simple(item) for item in reference_mask_paths]
    weight = group_mean(m_i)
    anomaly = anomaly * weight
    # median filtering (if required)
    if median_filter_size!=(1,1,1):
        anomaly = median_filter(anomaly, median_filter_size)
    return anomaly


#####################################
# entry point for the whole program #
#####################################

def main():

    parser = argparse.ArgumentParser(
        description='A simple anomaly detection algorithm for medical imaging '
        'based on multi-atlas image registration and negative log likelihood.')
    parser.add_argument('-s', '--source-images', nargs='+', type=str, required=True)
    parser.add_argument('-t', '--target-image', type=str, required=True)
    parser.add_argument('-o', '--output-dir', type=str, required=True)
    parser.add_argument('-c', '--do-n4-correction', choices = ['source', 'target', 'none', 'both'], type=str, default='source')
    parser.add_argument('-a', '--do-intensity-adaptation', action='store_true', default=True)

    args = parser.parse_args()

    # passing arguments
    source_images = args.source_images
    target_image = args.target_image
    output_dir = args.output_dir
    do_n4_correction = args.do_n4_correction
    do_intensity_adaptation = args.do_intensity_adaptation
    
    print('source images (%d in total):' % len(source_images), source_images)
    print('target image:', target_image)
    print('output directory:', output_dir)

    # OK, now let's do some dirty works...

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
                run_shell('N4BiasFieldCorrection -c [300x300x300x300] -i %s -o %s' % (source_image, target_location))
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

    #########################
    # do image registration #
    #########################

    source_images_after_reg = []
    brain_masks_after_reg = []
    print('start image registration ...')
    reg_dir = mkdir(join_path(output_dir,'registered'))
    for source_image, source_brain_mask in zip(source_images_after_n4, source_brain_masks):
        source_case = gfn(source_image, no_extension=True)
        target_case = gfn(target_image, no_extension=True)
        output_image = join_path(reg_dir, '%s_to_%s.nii.gz' % (source_case, target_case))
        output_mask = join_path(reg_dir, '%s_to_%s_mask.nii.gz' % (source_case, target_case))
        if file_exist(output_image) and file_exist(output_mask):
            pass
        else:
            image_registration(source_image, source_brain_mask, target_image_after_n4, output_image, output_mask)
        source_images_after_reg.append(output_image)
        brain_masks_after_reg.append(output_mask)

    ##############################
    # image intensity adaptation #
    ##############################
    
    adapt_dir = mkdir(join_path(output_dir,'adapted'))
    adapted_reference_images = []
    if do_intensity_adaptation:
        for source_image in source_images_after_reg:
            print('do intensity adaptation for image "%s".' % source_image)
            output_image = join_path(adapt_dir, gfn(source_image))
            if file_exist(output_image):
                print('already processed.')
            else:
                data = load_nifti_simple(source_image)
                thresh_hi = cutoff(data,0.99)
                print('intensity range of "%s" is between [%.2f, %.2f].' % (source_image,data.min(),data.max()))
                print('99%% intensity threshold = %.2f.' % thresh_hi)
                print('start histogram matching...')
                target = load_nifti_simple(target_image_after_n4)
                matched = match_histograms(data, target)
                save_nifti_with_header(matched, get_nifti_header(source_image), output_image)
                print('saved to "%s".' % output_image)
            adapted_reference_images.append(output_image)
    else:
        raise NotImplementedError('not implemented yet...')
    
    final_target_image = target_image_after_n4


    ###########################
    # calculate anomaly score #
    ###########################

    print('calculating anomaly score...')
    mean_filter_size = (1,1,1)
    median_filter_size = (1,1,1)
    # I disabled mean and median filtering (set them to (1,1,1)), however, if you want the result becomes 
    # smoother, you can set median_filter_size=(5,5,5). I haven't tried the effect when setting mean filter
    # size larger than (1,1,1), but it is interesting and worth considering.
    print('mean filter size:', mean_filter_size)
    print('median filter size:', median_filter_size)
    anomaly = nll(final_target_image, adapted_reference_images, brain_masks_after_reg, 
        mean_filter_size=mean_filter_size, median_filter_size=median_filter_size)
    anomaly_save_path = join_path(output_dir, 'anomaly.nii.gz')
    save_nifti_with_header(anomaly, get_nifti_header(final_target_image), anomaly_save_path)
    print('anomaly score for "%s" is saved to "%s".' % (target_image, anomaly_save_path))

