import nibabel as nib
from anomaly_detection.utilities.external_call import run_shell
from anomaly_detection.utilities.file_operations import abs_path, gfd, rm, join_path, mkdir
from anomaly_detection.utilities.basic_data_io import sync_nifti_header

def generate_registration_command(source, target, warped, 
    interpolation_method='Linear', use_histogram_matching=False,
    deform_type='elastic'):

    assert deform_type in ['elastic', 'rigid+affine'], 'unknown deformation type.'
    assert interpolation_method in ['Linear', 'NearestNeighbor'], 'unknown interpolation method.'
    assert use_histogram_matching in [True, False], 'invalid parameter setting for "use_histogram_matching".'
    
    output_directory = gfd(abs_path(warped))
    mkdir(output_directory)
    output_transform_prefix = join_path(output_directory,'warp_')

    command = 'antsRegistration ' # program name
    command += '--dimensionality 3 ' # 3D image
    command += '--float 1 ' # 0: use float64, 1: use float32
    command += '--collapse-output-transforms 1 '
    command += '--output [%s,%s] ' % (output_transform_prefix,warped)
    command += '--interpolation %s ' % interpolation_method
    command += '--use-histogram-matching %s ' % ( '0' if use_histogram_matching == False else '1')
    command += '--winsorize-image-intensities [0.005,0.995] '
    command += '--initial-moving-transform [%s,%s,1] ' % (target,source)
    command += '--transform Rigid[0.1] '
    command += '--metric MI[%s,%s,1,32,Regular,0.25] ' % (target,source)
    command += '--convergence [1000x500x250x0,1e-6,10] '
    command += '--shrink-factors 8x4x2x1 '
    command += '--smoothing-sigmas 3x2x1x0vox '
    command += '--transform Affine[0.1] '
    command += '--metric MI[%s,%s,1,32,Regular,0.25] ' % (target,source)
    command += '--convergence [1000x500x250x0,1e-6,10] '
    command += '--shrink-factors 8x4x2x1 '
    command += '--smoothing-sigmas 3x2x1x0vox '
    if deform_type == 'elastic':
        command += '--transform SyN[0.1,3,0] '
        command += '--metric CC[%s,%s,1,4] ' % (target,source)
        command += '--convergence [100x70x50x20,1e-6,10] '
        command += '--shrink-factors 8x4x2x1 '
        command += '--smoothing-sigmas 3x2x1x0vox '

    return command

def generate_transform_command(source,reference,transform,output,
    interpolation_method='Linear',inverse_transform=False):

    assert interpolation_method in ['Linear', 'NearestNeighbor'], 'unknown interpolation method.'
    assert inverse_transform in [True,False], 'invalid parameter setting for "inverse_transform".'

    command = 'antsApplyTransforms '
    command += '-d 3 --float --default-value 0 '
    command += '-i %s ' % source
    command += '-r %s ' % reference
    command += '-o %s ' % output
    command += '-n %s ' % interpolation_method
    command += '-t [%s,%s] ' % (transform, ( '0' if inverse_transform == False else '1')  )

    return command
    
def deform_mask(mask,reference,deforms,output):

    affine_transform, elastic_transform = deforms[0], deforms[1]
    
    output_directory = gfd(output)
    mkdir(output_directory)

    mask_affine = join_path(output_directory, 'mask_affine.nii.gz')
    run_shell(generate_transform_command(mask,reference,affine_transform,mask_affine,interpolation_method='NearestNeighbor',inverse_transform=False))
    run_shell(generate_transform_command(mask_affine,reference,elastic_transform,output,interpolation_method='NearestNeighbor',inverse_transform=False))

    rm(mask_affine)

#####################################################################################

def affine_registration_without_mask(source_image,target_image, output_image):
    try:
        output_directory = mkdir(gfd(output_image))
        run_shell(generate_registration_command(source_image, target_image, output_image, interpolation_method='Linear', 
            use_histogram_matching=False, deform_type='rigid+affine'))
    except:
        raise
    finally:
        # remove temporary files
        rm(join_path(output_directory, 'warp_0GenericAffine.mat'))


def image_registration(source_image, source_mask, target_image, output_image, output_mask):
    try:
        output_directory = mkdir(gfd(output_image))
        run_shell(generate_registration_command(source_image, target_image, output_image, interpolation_method='Linear', use_histogram_matching=False))
        mask_header_sync_output = join_path(output_directory, 'source_mask.nii.gz')
        sync_nifti_header(source_mask, source_image, mask_header_sync_output) 
        affine_transform = join_path(output_directory, 'warp_0GenericAffine.mat')
        elastic_transform = join_path(output_directory, 'warp_1Warp.nii.gz')
        deform_mask(mask_header_sync_output,output_image,[affine_transform, elastic_transform], output_mask)
    except:
        raise
    finally:
        # remove temporary files
        rm(join_path(output_directory, 'warp_0GenericAffine.mat'))
        rm(join_path(output_directory, 'warp_1Warp.nii.gz'))
        rm(join_path(output_directory, 'warp_1InverseWarp.nii.gz'))
        rm(mask_header_sync_output)

    
