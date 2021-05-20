# NLL_anomaly_detection
A simple anomaly detection algorithm for medical imaging based on multi-atlas image registration and negative log likelihood (NLL).

## 1. Paper
MICCAI-2021: Improved Brain Lesion Segmentation with Anatomical Priors from Healthy Subjects.

Chenghao Liu, Xiangzhu Zeng, Kongming Liang, Yizhou Yu, Chuyang Ye

## 2. Prerequisites
You need to install the following softwares for running the code.

**ANTs-2.3** (older versions should also work) and **FSL-6.0**

If you already have **ANTs** and **FSL** installed before, just skip the following steps.

**2.1. ANTs (Advanced Normalization Tools)**
>
> **Link**: https://github.com/ANTsX/ANTs
>
> **How to install**: compile from [source code](https://github.com/ANTsX/ANTs) (recommended) or pre-built [binaries](https://github.com/ANTsX/ANTs/releases)
> 
> **Verify your install**: to see whether ANTs is installed correctly on your system, after the installation you need to type in
> ```
> antsRegistration --version
> ```
> and
> ```
> N4BiasFieldCorrection --version
> ```
> in your console. It should produce output such as:
> ```
> ANTs Version: 3.0.0.0.dev13-ga16cc
> Compiled: Jan 22 2019 00:23:29
> ```
> Then test if `antsApplyTransforms` can work:
> ```
> antsApplyTransforms
> ```
> if no error shows, then ANTs is successfully installed.
> We need to use `antsRegistration` to reigster medical images, `antsApplyTransforms` to apply transforms to images, and `N4BiasFieldCorrection` to correct image intensity bias.

**2.2. FSL (FMRIB Software Library)**
>
> **Link**: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki
>
> **How to install**: FSL is installed using the *fsl_installer.py* downloaded from [here](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation). You need to register your personal information to the FSL site before download. After download you need to run the installer script and wait for the installation to finish.
>
> **Verify your install**: when the installation finished, type in
> ```
> bet -h
> ```
> in your console. If no error occurs then everything is OK! :). We use `bet` (brain extraction tool) to calculate brain mask for each image.

## 3. Install this script

After the installation of ANTs and FSL, you need to do the following steps to install this script:

1. Create a new Python3 venv ([link](https://docs.python.org/3/library/venv.html)). 

2. Activate the newly created virtual environment, download and unzip the codes, then `cd` into the directory where `setup.py` is located, and type:

```
pip install -U setuptools
pip install -e .
```

## 4. Prepare your data

In this example we used two datasets, [HCP](https://www.humanconnectome.org/study/hcp-young-adult/data-releases) (Human Connectome Project) and [ATLAS](http://fcon_1000.projects.nitrc.org/indi/retro/atlas.html) (Anatomical Tracings of Lesions After Stroke). They are all publicly avaliable. HCP dataset provides healthy MRI T1-weighted scans and ATLAS dataset provides T1-weighted scans of chronic stroke patients. Here is a screenshot of the downloaded images, you need to check if the appearances of the downloaded images are similar with the following example:

<p align="center">
  <img 
       src="https://github.com/lchdl/NLL_anomaly_detection/blob/main/images/HCP_ATLAS_examples.png"
       width="350"
  />
</p>

Note that the image appearances from HCP may vary in different releases. In this demo the HCP image release is not bias field corrected (you can see the center brain darker than the outside), which is a more generalized case. If you use your own dataset instad of HCP, and the images are bias field corrected, you can skip "N4 correction". For more details, please refer to "Sect. 5: Quick start".

## 5. Quick start

Once you installed the scripts, you can use the following command to calculate anomaly scores for a patient image:
```
<pre>
<b>NLL_anomaly_detection</b> \
--source-images /path/to/source/image1.nii.gz /path/to/source/image2.nii.gz /path/to/source/image3.nii.gz ... /path/to/source/image10.nii.gz \
--target-image /path/to/target/image.nii.gz \
--output-dir /path/to/output/dir/
</pre>
```

...

## 6. Implementation details

### 6.1 Pre-processing

**1. N4 bias field correction**
>...

**2. Skull-stripping**
>...

### 6.2 Image registration using ANTs


### 6.3 NLL anomaly score calculation



