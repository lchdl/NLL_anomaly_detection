from anomaly_detection.utilities.custom_print import print_ts as print # override print implementation
from anomaly_detection.utilities.external_call import run_shell
from anomaly_detection.utilities.file_operations import rm, mv, join_path, file_exist, make_unique_dir, cd, cp, mkdir, cwd
from anomaly_detection.utilities.basic_data_io import load_csv
from multiprocessing import Pool
import shutil
import argparse
from argparse import RawTextHelpFormatter
import nibabel as nib
import numpy as np

def generate_registration_command(source,target,options):
	command = 'antsRegistration ' # program name
	#command += '--verbose 1 '  # verbose output
	command += '--dimensionality 3 ' # 3D image
	command += '--float 1 ' # 0: use float64, 1: use float32
	command += '--collapse-output-transforms 1 '
	warped_file = options['transformed']
	inv_warped_file = options['inv_transformed']
	interp_method = options['interpolation']
	histogram_matching = options['histogram_matching']
	command += '--output [warp_,%s,%s] ' % (warped_file,inv_warped_file)
	command += '--interpolation %s ' % interp_method
	command += '--use-histogram-matching %d ' % histogram_matching
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
	command += '--transform SyN[0.1,3,0] '
	command += '--metric CC[%s,%s,1,4] ' % (target,source)
	command += '--convergence [100x70x50x20,1e-6,10] '
	command += '--shrink-factors 8x4x2x1 '
	command += '--smoothing-sigmas 3x2x1x0vox '
	return command

def generate_transform_command(source,reference,transform,options,inverse='0'):
	assert inverse in ['0','1']
	command = 'antsApplyTransforms '
	command += '-d 3 --float --default-value 0 '
	command += '-i %s ' % source
	command += '-r %s ' % reference
	command += '-o %s ' % options['output']
	command += '-n %s ' % options['interpolation']
	command += '-t [%s,%s] ' % (transform,inverse)
	return command
	
def deform_label(label,reference,deform,output):
	affine_transform = deform[0]
	elastic_transform = deform[1]
	options = {
		'output':'__temp__.nii.gz',
		'interpolation':'NearestNeighbor'
	}
	run_shell(generate_transform_command(label,reference,affine_transform,options))
	options = {
		'output':output,
		'interpolation':'NearestNeighbor'
	}
	run_shell(generate_transform_command('__temp__.nii.gz',reference,elastic_transform,options))
	rm('__temp__.nii.gz')

def save_nifti_with_header(data, header, path):
	nib.save(nib.nifti1.Nifti1Image(data.astype('float32'), None, header=header),path) 

def sync_nifti_header(source_path, target_path, output_path):
	target_header = nib.load(target_path).header.copy()
	source_data = nib.load(source_path).get_fdata()
	save_nifti_with_header(source_data, target_header, output_path)

def worker_func(arg):
	# unpack args
	source_dict, target_dict, save_dir, base_dir = arg[0], arg[1], arg[2], arg[3]

	final_case_name = '%s_to_%s' % (source_dict['case'], target_dict['case'])
	final_data = join_path(save_dir,'%s_data.nii.gz' % final_case_name)
	final_mask = join_path(save_dir,'%s_mask.nii.gz' % final_case_name)
	
	print('checking if both "%s" and "%s" exist.' % (final_data, final_mask))
	if file_exist(final_data) and file_exist(final_mask):
		print('Okay. Files already exists, skip this task.')
		return
	else:
		print('Nope. I will continue image registration.')

	working_dir = make_unique_dir(base_dir)
	
	try:
		print('changing working directory to "%s"' % working_dir)
		cd(working_dir)

		options={
			'transformed':'transformed.nii.gz',
			'inv_transformed':'inv_transformed.nii.gz',
			'interpolation':'Linear',
			'histogram_matching':0
		}
		cp(source_dict['data'],'source_data.nii.gz')
		cp(source_dict['mask'],'source_mask.nii.gz')
		cp(target_dict['data'],'target_data.nii.gz')
		
		run_shell(generate_registration_command('source_data.nii.gz','target_data.nii.gz',options))
		# in case the header for the mask and data does not match,
		# the mask header should be consistent with that of data,
		# we need to guarantee this.
		sync_nifti_header('source_mask.nii.gz','source_data.nii.gz','source_mask.nii.gz') 
		deform_label('source_mask.nii.gz','target_data.nii.gz',['warp_0GenericAffine.mat','warp_1Warp.nii.gz'],
			'brain_mask.nii.gz')

		print('moving NIFTIs to target location...')
		mv('transformed.nii.gz',final_data)
		mv('brain_mask.nii.gz',final_mask)

		cd(base_dir)
		print('removing temporary working dir')
		shutil.rmtree(working_dir)		

	except:
		shutil.rmtree(working_dir)
		raise

def main():

	parser = argparse.ArgumentParser(
		description=
			'Register two sets of images using antsRegistration,'
			'you need to install ANTs toolkit to use this script.'
			'The two sets of images are specified by two "*.csv" files,'
			'and you should give the correct paths of those "*.csv"s.'
			'The format of source csv should be as follows: \n\n'
			'case, data,                 mask\n'
			'0001, /path/to/nii1.nii.gz, /path/to/mask1.nii.gz\n'
			'0002, /path/to/nii2.nii.gz, /path/to/mask2.nii.gz\n'
			'...\n\n'
			'The format of target csv should be as follows: \n\n'
			'case, data          \n'
			'0001, /path/to/nii1.nii.gz \n'
			'0002, /path/to/nii2.nii.gz \n'
			'...\n\n',
		formatter_class=RawTextHelpFormatter)
	parser.add_argument('-s', '--source', help='Source image dataset.',type=str,required=True)
	parser.add_argument('-t', '--target', help='Target image dataset.',type=str,required=True)
	parser.add_argument('-o', '--output-dir',required=True, 
		help='Target output directory used for saving the registered images.',
		type=str)
	parser.add_argument('-j', '--num-workers', 
		help=
			'Number of processes used for registration. '
			'This applies to servers that has lots of CPU cores. '
			'Although antsRegistration is multithreaded, it doesn\'t '
			'use all of the CPU cores. Changing number of workers to '
			'an integer larger than 1 can further speed up the '
			'registration process.',
		type=int,
		default=2)
	args = parser.parse_args()

	# passing arguments
	source_csv = args.source
	target_csv = args.target
	save_dir = args.output_dir
	num_workers = args.num_workers

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



