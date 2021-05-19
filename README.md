# NLL_anomaly_detection
A simple anomaly detection algorithm for medical imaging based on multi-atlas image registration and negative log likelihood.

## 1. Paper
MICCAI-2021: Improved Brain Lesion Segmentation with Anatomical Priors from Healthy Subjects.

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
> We need to use `antsRegistration` to reigster medical images. `N4BiasFieldCorrection` is used to correct image intensity bias.

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
pip install -e .
```



## 4. Prepare your data

In this example we used two datasets, [HCP](https://www.humanconnectome.org/study/hcp-young-adult/data-releases) (Human Connectome Project) and [ATLAS](http://fcon_1000.projects.nitrc.org/indi/retro/atlas.html) (Anatomical Tracings of Lesions After Stroke). They are all publicly avaliable. HCP dataset provides healthy MRI T1-weighted scans and ATLAS dataset provides T1-weighted scans of chronic stroke patients. Here are the examples of the downloaded images, you need to check if the appearances of the downloaded images are similar with the following examples:

<div style="text-align:center"><img align="center" src="https://github.com/lchdl/NLL_anomaly_detection/blob/main/images/HCP_ATLAS_examples.png" width="300" /></div>

![image_example](https://github.com/lchdl/NLL_anomaly_detection/blob/main/images/HCP_ATLAS_examples.png?raw=true "Image examples from HCP and ATLAS dataset.")

## 5. Quick start

I packed the code 

Randomly pick 10 normal-appearing images from HCP dataset, and then randomly pick one patient image from ATLAS dataset.

You need to tell the script where those downloaded images are stored.

You can

The calculated NLL anomaly score map can be found in ...
Implementation principle and details is given in the following part

Once you understand how the code works, you can modify the NLL anomaly detection interface to your own need :), this is why I only uploaded a minimum working example.


## Implementation details

### Pre-processing
Here I provided the details about pre-processing steps for HCP and ATLAS dataset.

> **1. N4 bias field correction**
> 


